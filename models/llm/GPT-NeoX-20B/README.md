# GPT-NeoX-20B Fine-Tuning with LoRA

![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Transformers](https://img.shields.io/badge/Transformers-GPT--NeoX--20B-orange)

---

## Overview

This project provides a framework for **fine-tuning the GPT-NeoX-20B language model** using **LoRA (Low-Rank Adaptation)** and **4-bit quantization**.
It enables efficient adaptation of a very large language model on custom text datasets while significantly reducing GPU memory requirements.

The pipeline includes:

* Dataset loading and splitting into training and evaluation sets.
* Tokenization with the GPT-NeoX-20B tokenizer.
* LoRA integration for parameter-efficient fine-tuning.
* 4-bit quantization for memory-efficient model loading.
* Trainer setup using Hugging Face `Trainer` API.
* Automatic saving of the fine-tuned model and tokenizer.

---

## Features

* **GPT-NeoX-20B support** — state-of-the-art causal language model with 20B parameters.
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

## Project Status

> The project is currently in the **development stage**, with core functionalities implemented and tested.
> Additional features, optimizations, and refinements are planned for subsequent development phases, including enhanced dataset processing, support for multiple GPU training, and advanced LoRA configurations.

---

## License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details.

---

## Acknowledgments

* Built using **Hugging Face Transformers**, **PEFT**, and **bitsandbytes**.
* Inspired by parameter-efficient fine-tuning techniques for large language models.
