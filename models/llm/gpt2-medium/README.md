# GPT-2 Fine-Tuning on Wikipedia Articles

This project demonstrates how to fine-tune **GPT-2 (medium)** on a custom dataset of Wikipedia articles.  
Each article must be saved as a separate **.txt** file inside the `dataset/` directory (file name = article title).  

## Project Structure

```

project/
├── dataset/           # folder containing Wikipedia articles in .txt format
│   ├── Python.txt
│   ├── Machine Learning.txt
│   └── ...
├── train.txt          # automatically generated training split (90%)
├── eval.txt           # automatically generated evaluation split (10%)
├── script.py          # main training script
├── best\_model/        # directory where the best fine-tuned model is saved

````


## Requirements

- **Python 3.9+**
- **GPU with CUDA** (optional but strongly recommended for training speed)


### Python dependencies

```bash
pip install torch transformers
````

*(Ensure you install the correct `torch` version that matches your CUDA setup if training on GPU.)*


## System Requirements

* At least **8 GB RAM**
* Disk space: **\~1 GB** for GPT-2 medium + additional space for dataset and checkpoints
* **GPU with ≥8 GB VRAM** recommended for practical training speeds (otherwise training will fall back to CPU, which is significantly slower)

---

The script automatically processes all `.txt` files in `dataset/`, generates `train.txt` and `eval.txt`, fine-tunes GPT-2, and saves the best model into `best_model/`.
