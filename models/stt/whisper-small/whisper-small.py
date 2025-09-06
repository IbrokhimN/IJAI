import os
import random
import pandas as pd
import torch
from datasets import load_dataset, Audio
from transformers import (
    WhisperProcessor,
    WhisperForConditionalGeneration,
    Seq2SeqTrainer,
    Seq2SeqTrainingArguments,
    DataCollatorForSeq2Seq,
)

AUDIO_DIR = "audio" # тут должны быть реальные дирректории датасета которые мы в будущем добавим
TEXT_DIR = "texts"
OUT_DIR = "data"

os.makedirs(OUT_DIR, exist_ok=True)

pairs = []
for fname in os.listdir(AUDIO_DIR):
    if fname.lower().endswith((".wav", ".flac", ".mp3")):
        base = os.path.splitext(fname)[0]
        audio_path = os.path.join(AUDIO_DIR, fname)
        text_path = os.path.join(TEXT_DIR, base + ".txt")
        if os.path.exists(text_path):
            with open(text_path, "r", encoding="utf-8") as f:
                text = f.read().strip()
            pairs.append((audio_path, text))

print(f"🔎 Найдено {len(pairs)} пар аудио+текст")

random.shuffle(pairs)
split = int(0.9 * len(pairs))
train_pairs = pairs[:split]
eval_pairs = pairs[split:]

pd.DataFrame(train_pairs, columns=["audio", "text"]).to_csv(
    os.path.join(OUT_DIR, "train.csv"), index=False
)
pd.DataFrame(eval_pairs, columns=["audio", "text"]).to_csv(
    os.path.join(OUT_DIR, "eval.csv"), index=False
)

print("✅ train.csv и eval.csv сохранены")


data_files = {"train": os.path.join(OUT_DIR, "train.csv"),
              "validation": os.path.join(OUT_DIR, "eval.csv")}

dataset = load_dataset("csv", data_files=data_files)
dataset = dataset.cast_column("audio", Audio(sampling_rate=16000))

model_name = "openai/whisper-small"
processor = WhisperProcessor.from_pretrained(model_name, language="ru", task="transcribe")
model = WhisperForConditionalGeneration.from_pretrained(model_name)


def preprocess(batch):

    audio = batch["audio"]
    inputs = processor.feature_extractor(audio["array"], sampling_rate=16000, return_tensors="pt")
    labels = processor.tokenizer(batch["text"], return_tensors="pt").input_ids

    batch["input_features"] = inputs.input_features[0]
    batch["labels"] = labels[0]
    return batch

tokenized = dataset.map(preprocess, remove_columns=dataset["train"].column_names)


data_collator = DataCollatorForSeq2Seq(processor.tokenizer, model=model, padding=True)

training_args = Seq2SeqTrainingArguments(
    output_dir="./whisper-small-finetuned",
    per_device_train_batch_size=8,
    per_device_eval_batch_size=8,
    gradient_accumulation_steps=2,
    evaluation_strategy="steps",
    save_strategy="steps",
    num_train_epochs=5,
    logging_steps=100,
    save_steps=500,
    eval_steps=500,
    learning_rate=1e-5,
    warmup_steps=200,
    predict_with_generate=True,
    fp16=torch.cuda.is_available(),
    push_to_hub=False,
    report_to="none"
)

trainer = Seq2SeqTrainer(
    args=training_args,
    model=model,
    train_dataset=tokenized["train"],
    eval_dataset=tokenized["validation"],
    data_collator=data_collator,
    tokenizer=processor.feature_extractor,
)

trainer.train()

trainer.save_model("./best_whisper_small")
processor.save_pretrained("./best_whisper_small")

print("🎉 Обучение завершено, модель сохранена в ./best_whisper_small")
