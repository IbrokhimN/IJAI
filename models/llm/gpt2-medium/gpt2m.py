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

# === 0. Темы для обучения ===
articles = [
    "Python",  # возьмёт все статьи про Python
    "Фридрих Гаусс",  # точная статья
    "Machine Learning",
    ]

# === 1. Настройка википедии ===
DATASET_DIR = "dataset"
os.makedirs(DATASET_DIR, exist_ok=True)

wiki = wikipediaapi.Wikipedia("en")  # "ru" если нужна русская вики

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
        # Если точной статьи нет → ищем все статьи по ключевому слову
        print(f"🔎 Поиск статей по теме: {topic}")
        results = wiki.search(topic, results=10)  # можно увеличить число
        if not results:
            print(f"❌ Ничего не найдено: {topic}")
        for r in results:
            p = wiki.page(r)
            save_page(p)

# === 2. Собираем train.txt и eval.txt ===
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

# === 3. Загружаем токенайзер и модель GPT-2 Medium ===
model_name = "gpt2-medium"
tokenizer = GPT2Tokenizer.from_pretrained(model_name)
tokenizer.pad_token = tokenizer.eos_token
model = GPT2LMHeadModel.from_pretrained(model_name)

# === 4. Загружаем датасеты ===
def load_dataset(file_path, tokenizer, block_size=512):
    return TextDataset(
        tokenizer=tokenizer,
        file_path=file_path,
        block_size=block_size,
    )

train_dataset = load_dataset(train_path, tokenizer)
eval_dataset = load_dataset(eval_path, tokenizer)

# === 5. Collator ===
data_collator = DataCollatorForLanguageModeling(
    tokenizer=tokenizer,
    mlm=False,
)

# === 6. Аргументы обучения ===
training_args = TrainingArguments(
    output_dir="./gpt2-medium-finetuned",
    overwrite_output_dir=True,
    num_train_epochs=2,  # 🔥 норм для вики
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

    # сохраняем только лучший результат
    load_best_model_at_end=True,
    metric_for_best_model="eval_loss",
    greater_is_better=False,
)

# === 7. Trainer ===
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=eval_dataset,
    tokenizer=tokenizer,
    data_collator=data_collator,
)

# === 8. Запускаем обучение ===
trainer.train()

# === 9. Сохраняем только лучший вариант ===
trainer.save_model("./best_model")
tokenizer.save_pretrained("./best_model")

print("🎉 Обучение завершено, лучшая модель сохранена в ./best_model")

