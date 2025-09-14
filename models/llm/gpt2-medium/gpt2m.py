import os
import torch
from transformers import GPT2LMHeadModel, GPT2Tokenizer, Trainer, TrainingArguments, TextDataset, DataCollatorForLanguageModeling

DATASET_DIR = "dataset"
texts = []
for f in os.listdir(DATASET_DIR):
    if f.endswith(".txt"):
        with open(os.path.join(DATASET_DIR, f), "r", encoding="utf-8") as file:
            t = file.read().strip()
            if t:
                texts.append(t)

if not texts:
    raise ValueError("нет текстов")

full_text = "\n\n".join(texts)
train_path, eval_path = "train.txt", "eval.txt"
split = int(len(full_text) * 0.9)
open(train_path, "w", encoding="utf-8").write(full_text[:split])
open(eval_path, "w", encoding="utf-8").write(full_text[split:])

model_name = "gpt2-medium"
tokenizer = GPT2Tokenizer.from_pretrained(model_name)
tokenizer.pad_token = tokenizer.eos_token
model = GPT2LMHeadModel.from_pretrained(model_name)

def load_dataset(p, tok, block_size=512):
    return TextDataset(tokenizer=tok, file_path=p, block_size=block_size)

train_dataset = load_dataset(train_path, tokenizer)
eval_dataset = load_dataset(eval_path, tokenizer)

data_collator = DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False)

args = TrainingArguments(
    output_dir="./gpt2-medium-finetuned",
    overwrite_output_dir=True,
    num_train_epochs=2,
    per_device_train_batch_size=2,
    per_device_eval_batch_size=2,
    gradient_accumulation_steps=8,
    evaluation_strategy="steps",
    eval_steps=500,
    save_steps=500,
    logging_steps=100,
    learning_rate=5e-5,
    warmup_steps=200,
    save_total_limit=2,
    fp16=torch.cuda.is_available(),
    report_to="none",
    load_best_model_at_end=True,
    metric_for_best_model="eval_loss",
    greater_is_better=False,
)

trainer = Trainer(
    model=model,
    args=args,
    train_dataset=train_dataset,
    eval_dataset=eval_dataset,
    tokenizer=tokenizer,
    data_collator=data_collator,
)

trainer.train()
trainer.save_model("./best_model")
tokenizer.save_pretrained("./best_model")
