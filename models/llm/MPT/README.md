# Fine-Tuning MPT with LoRA

This repository contains a training script for fine-tuning **MPT (Mosaic Pretrained Transformer)** models with **Low-Rank Adaptation (LoRA)**. The implementation is based on Hugging Face Transformers, PEFT, and Datasets.

## Overview

The script executes the following workflow:

1. Loads text files from a dataset directory.  
2. Combines all files into a single corpus and creates a 90/10 train-eval split.  
3. Tokenizes the dataset using the MPT tokenizer.  
4. Wraps the base model with LoRA adapters for efficient fine-tuning.  
5. Trains the model with evaluation checkpoints.  
6. Saves the resulting model and tokenizer.  

## Requirements

- Python 3.10 or later  
- CUDA-enabled GPU with sufficient VRAM  
- Installed dependencies:  
  - `transformers` (with `trust_remote_code=True` for MPT)  
  - `datasets`  
  - `torch`  
  - `peft`  
  - `accelerate`  
  - `bitsandbytes`  

## Dataset

Place plain text files in the `dataset/` directory.  
The script will automatically load all `.txt` files, concatenate them, and generate `train.txt` and `eval.txt`.

## Model

The script is configured to use the Hugging Face implementation of MPT:

- `mosaicml/mpt-7b-instruct`  

Other MPT checkpoints (e.g., `mpt-7b`, `mpt-30b`) can be used by replacing the model name.

## Training Details

- Mixed precision (`fp16`) is enabled for efficiency.  
- LoRA adapters reduce memory requirements and training time.  
- Checkpoints and evaluation occur every 500 steps.  
- The best model is chosen based on evaluation loss.  

## Output

The fine-tuned model and tokenizer are saved in `./best_model_mpt`.  
This directory can be reloaded using `from_pretrained` for inference or further fine-tuning.

## License

The project follows the licensing terms of MosaicML’s MPT models. Ensure compliance with the MPT license when using or distributing fine-tuned models.
