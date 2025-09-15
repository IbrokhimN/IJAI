# Fine-tuning Qwen-1.5

## Requirements
- Python 3.10+
- PyTorch (CUDA recommended)
- Hugging Face `transformers`, `datasets`, `accelerate`
- `trl` (для SFT/PEFT)

```bash
pip install torch transformers datasets accelerate trl peft
````

## Model & Tokenizer

```python
from transformers import AutoModelForCausalLM, AutoTokenizer

model_name = "Qwen/Qwen1.5-1.8B"
model = AutoModelForCausalLM.from_pretrained(model_name, device_map="auto")
tokenizer = AutoTokenizer.from_pretrained(model_name)
```

## Dataset Example

```python
from datasets import load_dataset

dataset = load_dataset("tatsu-lab/alpaca", split="train")
```

## Training (PEFT LoRA)

```python
from trl import SFTTrainer, SFTTrainingArguments

args = SFTTrainingArguments(
    output_dir="./qwen-finetuned",
    per_device_train_batch_size=2,
    gradient_accumulation_steps=8,
    num_train_epochs=3,
    learning_rate=2e-5,
    fp16=True,
    logging_steps=10,
    save_strategy="epoch",
)

trainer = SFTTrainer(
    model=model,
    tokenizer=tokenizer,
    train_dataset=dataset,
    args=args,
    peft_config={"lora_r": 8, "lora_alpha": 16, "lora_dropout": 0.05},
)

trainer.train()
```

## Inference

```python
text = "Explain quantum computing in simple terms."
inputs = tokenizer(text, return_tensors="pt").to(model.device)
outputs = model.generate(**inputs, max_new_tokens=200)
print(tokenizer.decode(outputs[0], skip_special_tokens=True))
```


Хочешь, я могу расписать ещё отдельно **вариант без LoRA (полный fine-tuning)**, но в суперкоротком виде?
