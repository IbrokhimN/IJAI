import os
import wikipediaapi
import torch
from transformers import (
    GPT2LMHeadModel,
    GPT2Tokenizer,
    Trainer,
    TrainingArguments,
    TextDataset,
    DataCollatorForLanguageModeling,
)

articles = [
    "Python", 
    "Фридрих Гаусс", 
    "Machine Learning",
    ]

DATASET_DIR = "dataset"
os.makedirs(DATASET_DIR, exist_ok=True)

wiki = wikipediaapi.Wikipedia("en")  

all_texts = []

def save_page(page, dataset_dir=DATASET_DIR):
    """Сохраняет одну страницу в dataset"""
    if not page.exists():
        return False
    safe_name = page.title.replace(" ", "_").replace("/", "_")
    file_path = os.path.join(dataset_dir, f"{safe_name}.txt")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(page.text)
    all_texts.append(page.text)
    print(f"✅ Сохранено: {file_path} ({len(page.text.split())} слов)")
    return True

for topic in articles:
    page = wiki.page(topic)
    if page.exists():
        save_page(page)
    else:
        print(f"🔎 Поиск статей по теме: {topic}")
        results = wiki.search(topic, results=10) 
        if not results:
            print(f"❌ Ничего не найдено: {topic}")
        for r in results:
            p = wiki.page(r)
            save_page(p)

if all_texts:
    full_text = "\n\n".join(all_texts)
    train_path = "train.txt"
    eval_path = "eval.txt"

    split = int(len(full_text) * 0.9)
    with open(train_path, "w", encoding="utf-8") as f:
        f.write(full_text[:split])
    with open(eval_path, "w", encoding="utf-8") as f:
        f.write(full_text[split:])

    print(f"📂 train.txt и eval.txt созданы (всего {len(full_text.split())} слов)")
else:
    raise ValueError("❌ Нет статей для обучения")

model_name = "gpt2-medium"
tokenizer = GPT2Tokenizer.from_pretrained(model_name)
tokenizer.pad_token = tokenizer.eos_token
model = GPT2LMHeadModel.from_pretrained(model_name)

def load_dataset(file_path, tokenizer, block_size=512):
    return TextDataset(
        tokenizer=tokenizer,
        file_path=file_path,
        block_size=block_size,
    )

train_dataset = load_dataset(train_path, tokenizer)
eval_dataset = load_dataset(eval_path, tokenizer)

data_collator = DataCollatorForLanguageModeling(
    tokenizer=tokenizer,
    mlm=False,
)

training_args = TrainingArguments(
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
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=eval_dataset,
    tokenizer=tokenizer,
    data_collator=data_collator,
)

trainer.train()

trainer.save_model("./best_model")
tokenizer.save_pretrained("./best_model")

print("🎉 Обучение завершено, лучшая модель сохранена в ./best_model")

