# Gemma Fine-Tuning with LoRA

![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Transformers](https://img.shields.io/badge/Transformers-Gemma-orange)

---

## Overview

This project provides a framework for **fine-tuning the Gemma language model** using **LoRA (Low-Rank Adaptation)** and **4-bit quantization**.
It enables efficient adaptation of Gemma on custom text datasets while reducing GPU memory usage, making it feasible to train very large models on limited hardware.

The pipeline includes:

* Dataset loading and splitting into training and evaluation sets.
* Tokenization with the Gemma tokenizer.
* LoRA integration for parameter-efficient fine-tuning.
* 4-bit quantization for memory-efficient model loading.
* Trainer setup using Hugging Face `Trainer` API.
* Automatic saving of the fine-tuned model and tokenizer.

---

## Features

* **Gemma support** — advanced causal language model.
* **LoRA fine-tuning** — train only a subset of parameters for faster and memory-efficient adaptation.
* **4-bit quantization** — reduces GPU memory usage while maintaining performance.
* **Automatic dataset handling** — text files from `dataset/` directory are processed, split, and tokenized.
* **Trainer integration** — Hugging Face `Trainer` with evaluation, logging, and checkpointing.
* **Safe model saving** — automatically saves fine-tuned model and tokenizer to `./best_model`.

---

## Requirements

* Python **3.8+**
* [Transformers](https://pypi.org/project/transformers/)
* [PyTorch](https://pypi.org/project/torch/)
* [peft](https://pypi.org/project/peft/)
* [bitsandbytes](https://pypi.org/project/bitsandbytes/)

Install dependencies:

```bash
pip install torch transformers peft bitsandbytes
```

---

## Model Source

> Replace the `model_name` variable in the script with the **actual Hugging Face repository of Gemma**, e.g.:

```python
model_name = "username/gemma"  # replace with real HF repo
```

Ensure that the repository is publicly accessible or that you have proper authentication set up for private models.

---

## Project Status

> The project is currently in the **development stage**, with core functionalities implemented and tested.
> Additional features, optimizations, and refinements are planned for subsequent development phases, including enhanced dataset processing, multi-GPU training support, and advanced LoRA configurations.

---

## License

This project is licensed under the **AGPlv3.0 License**.

---

## Acknowledgments

* Built using **Hugging Face Transformers**, **PEFT**, and **bitsandbytes**.
* Inspired by parameter-efficient fine-tuning techniques for large language models.
