import os
import torch
from datasets import load_dataset
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    Trainer,
    TrainingArguments,
    DataCollatorForLanguageModeling,
)
from peft import LoraConfig, get_peft_model

DATASET_DIR = "dataset"
OUTPUT_DIR = "./best_model"

if not os.path.exists(DATASET_DIR):
    raise FileNotFoundError(f"Folder {DATASET_DIR} not found")

texts = []
for file in os.listdir(DATASET_DIR):
    if file.endswith(".txt"):
        with open(os.path.join(DATASET_DIR, file), "r", encoding="utf-8") as f:
            content = f.read().strip()
            if content:
                texts.append(content)
                print(f"Loaded {file} ({len(content.split())} words)")

if not texts:
    raise ValueError("No .txt files found in dataset/")

full_text = "\n\n".join(texts)
split = int(len(full_text) * 0.9)
train_text, eval_text = full_text[:split], full_text[split:]

with open("train.txt", "w", encoding="utf-8") as f:
    f.write(train_text)
with open("eval.txt", "w", encoding="utf-8") as f:
    f.write(eval_text)

print(f"train.txt and eval.txt created ({len(full_text.split())} words)")

model_name = "mosaicml/mpt-7b"

tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token

model = AutoModelForCausalLM.from_pretrained(
    model_name,
    load_in_4bit=True,
    device_map="auto",
    torch_dtype=torch.float16,
    trust_remote_code=True,
)

lora_config = LoraConfig(
    r=16,
    lora_alpha=32,
    target_modules=["Wqkv", "out_proj"],
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM"
)

model = get_peft_model(model, lora_config)

def load_dataset_from_txt(file_path, tokenizer, block_size=512):
    dataset = load_dataset("text", data_files=file_path)
    def tokenize(batch):
        return tokenizer(
            batch["text"],
            truncation=True,
            padding="max_length",
            max_length=block_size,
        )
    tokenized = dataset.map(tokenize, batched=True, remove_columns=["text"])
    tokenized.set_format(type="torch", columns=["input_ids", "attention_mask"])
    return tokenized["train"]

train_dataset = load_dataset_from_txt("train.txt", tokenizer)
eval_dataset = load_dataset_from_txt("eval.txt", tokenizer)

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

print(f"Training complete. Model saved in {OUTPUT_DIR}")
