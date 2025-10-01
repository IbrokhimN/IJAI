import os
import torch
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    Trainer,
    TrainingArguments,
    DataCollatorForLanguageModeling,
)
from datasets import load_dataset
from peft import LoraConfig, get_peft_model

DATASET_DIR = "dataset"
OUTPUT_DIR = "./best_model"

# If you don’t even have a dataset folder, why the hell are you running this script?
if not os.path.exists(DATASET_DIR):
    raise FileNotFoundError(f"Folder {DATASET_DIR} not found")

# Collect all texts. Hopefully you're not dumping garbage logs here.
all_texts = []
for fname in os.listdir(DATASET_DIR):
    if fname.endswith(".txt"):
        path = os.path.join(DATASET_DIR, fname)
        with open(path, "r", encoding="utf-8") as f:
            text = f.read().strip()
            if text:
                all_texts.append(text)

# Let's just smash all files together with double newlines.
# Don't complain later when the model has no clue about context boundaries.
full_text = "\n\n".join(all_texts)
train_path = "train.txt"
eval_path = "eval.txt"

# Splitting by characters. Words? Sentences? Nah, too fancy. Just raw characters.
split = int(len(full_text) * 0.9)
with open(train_path, "w", encoding="utf-8") as f:
    f.write(full_text[:split])
with open(eval_path, "w", encoding="utf-8") as f:
    f.write(full_text[split:])

model_name = "yuntian-deng/Yi-1.5-6B"

tokenizer = AutoTokenizer.from_pretrained(model_name, use_fast=True)
tokenizer.pad_token = tokenizer.eos_token  # Classic: abusing EOS as PAD. Sure, why not.
tokenizer.padding_side = "right"

# Load the model. Cross your fingers that your GPU doesn’t explode.
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    load_in_4bit=True,   # Cheap way to say "my GPU sucks"
    device_map="auto",   # Let HF figure it out. Hope for the best.
    torch_dtype=torch.float16,
)

# LoRA config. Because full fine-tuning would murder your hardware.
# And yes, we pick q_proj and v_proj like everyone else. Originality is overrated.
lora_config = LoraConfig(
    r=16,
    lora_alpha=32,
    target_modules=["q_proj", "v_proj"],
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM",
)
model = get_peft_model(model, lora_config)

# Great, let’s reinvent the wheel: custom dataset loader.
# Could’ve been done simpler, but hey, why not.
def load_dataset_from_file(file_path, tokenizer, block_size=512):
    dataset = load_dataset("text", data_files={"data": file_path})["data"]

    def tokenize_function(examples):
        return tokenizer(
            examples["text"],
            truncation=True,
            padding="max_length",  # Perfect way to waste half the sequence with PAD tokens.
            max_length=block_size,
        )

    tokenized = dataset.map(tokenize_function, batched=True, remove_columns=["text"])
    tokenized.set_format(type="torch", columns=["input_ids", "attention_mask"])
    return tokenized

train_dataset = load_dataset_from_file(train_path, tokenizer)
eval_dataset = load_dataset_from_file(eval_path, tokenizer)

# At least you didn’t try MLM here. Small mercy.
data_collator = DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False)

training_args = TrainingArguments(
    output_dir=OUTPUT_DIR,
    overwrite_output_dir=True,
    num_train_epochs=2,  # Two epochs. Fine-tuning? More like "drive-by training".
    per_device_train_batch_size=1,  # Living within VRAM poverty.
    per_device_eval_batch_size=1,
    gradient_accumulation_steps=8,  # Pretend we have a normal batch size.
    evaluation_strategy="steps",
    eval_steps=500,
    save_steps=500,
    logging_steps=100,
    learning_rate=5e-5,  # Totally scientific choice, right?
    warmup_steps=200,
    save_total_limit=2,
    fp16=True,  # Because who needs accuracy when you can fit into memory.
    report_to="none",
    load_best_model_at_end=True,
    metric_for_best_model="eval_loss",
    greater_is_better=False,
)

# HuggingFace's "Trainer" — aka the magical black box where you throw your dataset
# and hope something good happens.
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=eval_dataset,
    tokenizer=tokenizer,
    data_collator=data_collator,
)

trainer.train()

# Save the model. Pray you can actually reload this without issues.
model.save_pretrained(OUTPUT_DIR)
tokenizer.save_pretrained(OUTPUT_DIR)
