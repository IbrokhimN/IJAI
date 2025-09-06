import os
import wikipediaapi
import torch
from datasets import load_dataset
from transformers import (
    GPTNeoForCausalLM,
    GPT2Tokenizer,
    Trainer,
    TrainingArguments,
    DataCollatorForLanguageModeling,
)

articles = [
    "Python",
    "Фридрих Гаусс",
    "Machine Learning",
    # должно быть больше статей ( мы добавим отдельный файл с ними )
]

DATASET_DIR = "dataset"
os.makedirs(DATASET_DIR, exist_ok=True)

wiki = wikipediaapi.Wikipedia("en")
all_texts = []


def save_page(page, dataset_dir=DATASET_DIR):
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

    split = int(len(full_text) * 0.95)  
    with open(train_path, "w", encoding="utf-8") as f:
        f.write(full_text[:split])
    with open(eval_path, "w", encoding="utf-8") as f:
        f.write(full_text[split:])

    print(f"📂 train.txt и eval.txt созданы (всего {len(full_text.split())} слов)")
else:
    raise ValueError("❌ Нет статей для обучения")


model_name = "EleutherAI/gpt-neo-1.3B" 
tokenizer = GPT2Tokenizer.from_pretrained(model_name)
tokenizer.pad_token = tokenizer.eos_token
model = GPTNeoForCausalLM.from_pretrained(model_name)


datasets = load_dataset("text", data_files={"train": train_path, "validation": eval_path})


def tokenize_function(examples):
    return tokenizer(
        examples["text"],
        truncation=True,
        padding="max_length",
        max_length=512,
    )


tokenized_datasets = datasets.map(tokenize_function, batched=True, remove_columns=["text"])

data_collator = DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False)


training_args = TrainingArguments(
    output_dir="./gptneo-finetuned",
    overwrite_output_dir=True,
    num_train_epochs=2,                
    per_device_train_batch_size=8,     
    per_device_eval_batch_size=8,
    gradient_accumulation_steps=2,      
    evaluation_strategy="steps",
    eval_steps=5000,                   
    save_steps=5000,                   
    logging_steps=500,
    learning_rate=5e-5,
    warmup_steps=1000,
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
    train_dataset=tokenized_datasets["train"],
    eval_dataset=tokenized_datasets["validation"],
    tokenizer=tokenizer,
    data_collator=data_collator,
)

trainer.train()

trainer.save_model("./best_gptneo_model")
tokenizer.save_pretrained("./best_gptneo_model")

print("🎉 Обучение завершено, лучшая модель сохранена в ./best_gptneo_model")
