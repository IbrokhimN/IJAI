from pathlib import Path
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, TextIteratorStreamer
from peft import PeftModel

BASE = Path(__file__).resolve().parent
MODEL_PATH = BASE / "stablelm-lora"

device = "cuda" if torch.cuda.is_available() else "cpu"

tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token

model = AutoModelForCausalLM.from_pretrained(
    MODEL_PATH,
    device_map="auto",
    torch_dtype=torch.float16,
)

model = PeftModel.from_pretrained(model, MODEL_PATH, device_map="auto")
model.eval()

messages = [{"role": "system", "content": "You are a helpful assistant."}]

def ask(prompt: str, max_tokens: int = 200, temperature: float = 0.7):
    reply = ""
    for token in ask_stream(prompt, max_tokens=max_tokens, temperature=temperature):
        reply += token
    return reply

def ask_stream(prompt: str, max_tokens: int = 200, temperature: float = 0.7):
    messages.append({"role": "user", "content": prompt})
    input_text = ""
    for msg in messages:
        role = msg["role"]
        content = msg["content"]
        if role == "system":
            input_text += f"<|system|>{content}\n"
        elif role == "user":
            input_text += f"<|user|>{content}\n"
        elif role == "assistant":
            input_text += f"<|assistant|>{content}\n"
    
    input_ids = tokenizer(input_text, return_tensors="pt").input_ids.to(device)
    streamer = TextIteratorStreamer(tokenizer, skip_prompt=True, skip_special_tokens=True)
    
    import threading
    generation_kwargs = dict(
        input_ids=input_ids,
        max_new_tokens=max_tokens,
        temperature=temperature,
        do_sample=True,
        streamer=streamer
    )
    thread = threading.Thread(target=model.generate, kwargs=generation_kwargs)
    thread.start()
    
    reply = ""
    for token in streamer:
        reply += token
        yield token
    messages.append({"role": "assistant", "content": reply})
