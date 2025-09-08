# script.py
from auto_gptq import AutoGPTQForCausalLM
from transformers import AutoTokenizer
import torch

# -------------------------------
# Настройки
# -------------------------------
MODEL_PATH = "."             # путь к директории с моделью
DEVICE = "cuda:0"            # GPU, можно "cpu" для теста, но будет очень медленно
MAX_NEW_TOKENS = 100
TEMPERATURE = 0.8
TOP_P = 0.9

# -------------------------------
# Загружаем токенизатор
# -------------------------------
tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)

# -------------------------------
# Загружаем GPTQ модель
# -------------------------------
model = AutoGPTQForCausalLM.from_quantized(
    MODEL_PATH,
    device=DEVICE,
    use_safetensors=True,
    trust_remote_code=True
)

# -------------------------------
# Генерация текста
# -------------------------------
prompt = "Напиши шутку про программиста"
inputs = tokenizer(prompt, return_tensors="pt").to(DEVICE)

outputs = model.generate(
    **inputs,
    max_new_tokens=MAX_NEW_TOKENS,
    do_sample=True,
    temperature=TEMPERATURE,
    top_p=TOP_P
)

# -------------------------------
# Вывод результата
# -------------------------------
print(tokenizer.decode(outputs[0], skip_special_tokens=True))

