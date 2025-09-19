# Fine-Tuning LLaMA 2 with LoRA

This repository provides a training script for fine-tuning the **LLaMA 2** language model using **Low-Rank Adaptation (LoRA)**. The implementation leverages Hugging Face Transformers, PEFT, and Datasets libraries.

## Overview

The script performs the following steps:

1. Loads plain text files from a specified dataset directory.
2. Prepares training and evaluation splits.
3. Tokenizes the dataset with the LLaMA 2 tokenizer.
4. Applies LoRA to reduce the number of trainable parameters and memory usage.
5. Trains the model with evaluation and checkpointing.
6. Saves the fine-tuned model and tokenizer.

## Requirements

- Python 3.10 or later  
- CUDA-enabled GPU with sufficient VRAM  
- Installed dependencies:
  - `transformers`
  - `datasets`
  - `torch`
  - `peft`
  - `accelerate`
  - `bitsandbytes`

## Dataset

Place your text files in the `dataset/` folder.  
The script will automatically load all `.txt` files, combine them, and create a 90/10 train-eval split.

## Model

The training script uses the Hugging Face version of LLaMA 2, for example:

- `meta-llama/Llama-2-7b-hf`  
- `meta-llama/Llama-2-13b-hf`  
- `meta-llama/Llama-2-70b-hf`  

The `7b` model is the most accessible option for single-GPU setups.

## Training Details

- Optimized with mixed precision (`fp16`).  
- Gradient accumulation is enabled for memory efficiency.  
- Evaluation and checkpoint saving occur every 500 steps.  
- The best model is automatically selected based on evaluation loss.  

## Output

After training, the fine-tuned model and tokenizer are saved in the `./best_model` directory.  
This directory can be reloaded with `from_pretrained` for inference or further training.

## License

This project follows the licensing requirements of the LLaMA 2 model family. Ensure compliance with Meta’s model license when using or distributing fine-tuned versions.
