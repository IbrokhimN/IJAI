import os
import torch
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    Trainer,
    TrainingArguments,
    TextDataset,
    DataCollatorForLanguageModeling,
)
from peft import LoraConfig, get_peft_model

DATASET_DIR = "dataset"
OUTPUT_DIR = "./best_model"

if not os.path.exists(DATASET_DIR):
    raise FileNotFoundError(f"Folder {DATASET_DIR} not found")

all_texts = []
for fname in os.listdir(DATASET_DIR):
    if fname.endswith(".txt"):
        path = os.path.join(DATASET_DIR, fname)
        with open(path, "r", encoding="utf-8") as f:
            text = f.read().strip()
            if text:
                all_texts.append(text)
                print(f"Loaded {fname} ({len(text.split())} words)")

if not all_texts:
    raise ValueError("No texts found in dataset/")

full_text = "\n\n".join(all_texts)
train_path = "train.txt"
eval_path = "eval.txt"

split = int(len(full_text) * 0.9)
with open(train_path, "w", encoding="utf-8") as f:
    f.write(full_text[:split])
with open(eval_path, "w", encoding="utf-8") as f:
    f.write(full_text[split:])

print(f"train.txt and eval.txt created (total {len(full_text.split())} words)")

model_name = "Gemma"  # нужна реальная модель из hugging face

tokenizer = AutoTokenizer.from_pretrained(model_name)
tokenizer.pad_token = tokenizer.eos_token


model = AutoModelForCausalLM.from_pretrained(
    model_name,
    load_in_4bit=True,
    device_map="auto",
    torch_dtype=torch.float16,
)

lora_config = LoraConfig(
    r=16,
    lora_alpha=32,
    target_modules=["q_proj", "v_proj"],  
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM"
)
model = get_peft_model(model, lora_config)

def load_dataset(file_path, tokenizer, block_size=512):
    return TextDataset(tokenizer=tokenizer, file_path=file_path, block_size=block_size)

train_dataset = load_dataset(train_path, tokenizer)
eval_dataset = load_dataset(eval_path, tokenizer)

data_collator = DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False)

training_args = TrainingArguments(
    output_dir=OUTPUT_DIR,
    overwrite_output_dir=True,
    num_train_epochs=2,
    per_device_train_batch_size=1,
    per_device_eval_batch_size=1,
    gradient_accumulation_steps=8,
    evaluation_strategy="steps",
    eval_steps=500,
    save_steps=500,
    logging_steps=100,
    learning_rate=5e-5,
    warmup_steps=200,
    save_total_limit=2,
    fp16=True,
    report_to="none",
    load_best_model_at_end=True,
    metric_for_best_model="eval_loss",
    greater_is_better=False,
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=eval_dataset,
    tokenizer=tokenizer,
    data_collator=data_collator,
)

trainer.train()
model.save_pretrained(OUTPUT_DIR)
tokenizer.save_pretrained(OUTPUT_DIR)

print(f"Training complete, model saved in {OUTPUT_DIR}")
