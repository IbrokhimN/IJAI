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
