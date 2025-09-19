# Fine-Tuning Mistral 7B

This repository provides a training script for fine-tuning **Mistral-7B** using Hugging Face Transformers and Datasets. The workflow is designed for causal language modeling tasks with efficient data preprocessing and evaluation.

## Overview

The script follows these steps:

1. Loads all `.txt` files from the `dataset/` directory.  
2. Concatenates them into a single corpus and splits into 90% training and 10% evaluation data.  
3. Tokenizes the text using the **Mistral** tokenizer.  
4. Groups tokenized sequences into fixed-length blocks suitable for training.  
5. Trains the model with evaluation checkpoints and logging.  
6. Saves the fine-tuned model and tokenizer for later use.  

## Requirements

- Python 3.10 or later  
- CUDA-enabled GPU with sufficient memory (recommended)  
- Installed dependencies:  
  - `transformers`  
  - `datasets`  
  - `torch`  
  - `accelerate`  

## Dataset

Prepare a `dataset/` folder containing plain text files (`.txt`).  
The script automatically merges them into a training and evaluation split.

## Model

The script uses the Hugging Face version of Mistral:

- `mistralai/Mistral-7B-v0.1`  

This model is a strong open-weight alternative for general language modeling tasks.

## Training Details

- Sequence length (`block_size`): 1024 tokens.  
- Mixed precision (`fp16` or `bfloat16`) is used if a GPU is available.  
- Gradient accumulation improves efficiency with small batch sizes.  
- Evaluation and checkpointing occur every 200 steps.  
- The best model is selected based on evaluation loss.  

## Output

The trained model and tokenizer are saved in the `./best_mistral` directory.  
This directory can be reloaded with Hugging Face’s `from_pretrained` for inference or further training.

## License

This project follows the licensing requirements of the Mistral models.  
Ensure compliance with Mistral AI’s model license when using or distributing fine-tuned versions.
