import os
import torch
from datasets import load_dataset
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    DataCollatorForLanguageModeling,
    Trainer,
    TrainingArguments,
)

DATASET_DIR = "dataset"
assert os.path.exists(DATASET_DIR), "❌ Папка dataset не найдена"

all_texts = []
for fname in os.listdir(DATASET_DIR):
    if fname.endswith(".txt"):
        file_path = os.path.join(DATASET_DIR, fname)
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read().strip()
            if text:
                all_texts.append(text)

if not all_texts:
    raise ValueError("❌ Нет текстов для обучения в dataset/")

full_text = "\n\n".join(all_texts)
train_path = "train.txt"
eval_path = "eval.txt"

split = int(len(full_text) * 0.9)
with open(train_path, "w", encoding="utf-8") as f:
    f.write(full_text[:split])
with open(eval_path, "w", encoding="utf-8") as f:
    f.write(full_text[split:])

model_name = "mistralai/Mistral-7B-v0.1"
tokenizer = AutoTokenizer.from_pretrained(model_name)
tokenizer.pad_token = tokenizer.eos_token
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype=torch.bfloat16 if torch.cuda.is_available() else torch.float32,
    device_map="auto",
)

def load_text_dataset(train_path, eval_path, tokenizer, block_size=1024):
    dataset = load_dataset("text", data_files={"train": train_path, "validation": eval_path})

    def tokenize_function(examples):
        return tokenizer(examples["text"])

    tokenized_datasets = dataset.map(tokenize_function, batched=True, num_proc=2, remove_columns=["text"])

    def group_texts(examples):
        concatenated = {k: sum(examples[k], []) for k in examples.keys()}
        total_length = len(concatenated[list(examples.keys())[0]])
        total_length = (total_length // block_size) * block_size
        result = {
            k: [t[i : i + block_size] for i in range(0, total_length, block_size)]
            for k, t in concatenated.items()
        }
        result["labels"] = result["input_ids"].copy()
        return result

    lm_datasets = tokenized_datasets.map(group_texts, batched=True, num_proc=2)
    return lm_datasets["train"], lm_datasets["validation"]

train_dataset, eval_dataset = load_text_dataset(train_path, eval_path, tokenizer)

data_collator = DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False)

training_args = TrainingArguments(
    output_dir="./mistral-7b-finetuned",
    overwrite_output_dir=True,
    num_train_epochs=1,
    per_device_train_batch_size=1,
    per_device_eval_batch_size=1,
    gradient_accumulation_steps=16,
    evaluation_strategy="steps",
    eval_steps=200,
    save_steps=200,
    logging_steps=50,
    learning_rate=2e-5,
    warmup_steps=100,
    save_total_limit=2,
    fp16=torch.cuda.is_available(),
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
trainer.save_model("./best_mistral")
tokenizer.save_pretrained("./best_mistral")
