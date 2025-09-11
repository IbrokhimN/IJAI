## Phi-3 Small Integration

This repository integrates the [Microsoft Phi-3 Small](https://huggingface.co/microsoft/phi-3-small) language model.  
The model is **developed and released by Microsoft**. I am **not the author of the model** – it is only used here as a dependency to provide natural language capabilities.

### License and Attribution
- Model License: Responsible AI License (see original [license terms](https://huggingface.co/microsoft/phi-3-small))  
- Code License: MIT  
- All rights to the Phi-3 model remain with Microsoft.

### Disclaimer
The Phi-3 Small model may generate outputs that are **inaccurate, biased, or inappropriate**.  
This repository provides the model **as is** without any warranty.  
**Use at your own risk. I do not take responsibility for model outputs or their consequences.**

### Example Usage
```python
from transformers import AutoModelForCausalLM, AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained("microsoft/phi-3-small")
model = AutoModelForCausalLM.from_pretrained("microsoft/phi-3-small")

inputs = tokenizer("Hello, world!", return_tensors="pt")
outputs = model.generate(**inputs, max_length=50)
print(tokenizer.decode(outputs[0], skip_special_tokens=True))
```

### Hardware Requirements

At the current stage, running the model requires **~32 GB of RAM** for stable performance.  
In future updates, the model will be **quantized** to significantly reduce memory usage, making it possible to run on machines with as little as **8 GB of RAM**.



# System Requirements for Phi-3 Small (Ollama)

| Component | Minimum (for phi-3-small ~2.5–3 GB) | Recommended |
|-----------|--------------------------------------|-------------|
| **CPU**   | 4 cores (x86_64 / Apple Silicon M1+) | 6–8 cores |
| **RAM**   | 6 GB (bare minimum) | 12–16 GB |
| **GPU**   | Not required (CPU works fine) | NVIDIA GPU with 4–6 GB VRAM (e.g. GTX 1660, RTX 2060) or Apple M1/M2/M3 integrated GPU |
| **Disk**  | 4–5 GB SSD free space | 10–15 GB SSD |
| **OS**    | macOS (Apple Silicon) / Linux / Windows (WSL2 recommended) | Same |
