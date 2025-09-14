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

