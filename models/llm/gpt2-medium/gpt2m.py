import os, torch
from transformers import GPT2LMHeadModel, GPT2Tokenizer, Trainer, TrainingArguments, TextDataset, DataCollatorForLanguageModeling

txts = [open("dataset/"+f, encoding="utf-8").read() for f in os.listdir("dataset") if f.endswith(".txt")]
if not txts: raise SystemExit("нет файлов")
txt = "\n\n".join(txts)
open("train.txt","w",encoding="utf-8").write(txt[:int(len(txt)*.9)])
open("eval.txt","w",encoding="utf-8").write(txt[int(len(txt)*.9):])

tok = GPT2Tokenizer.from_pretrained("gpt2-medium"); tok.pad_token = tok.eos_token
m = GPT2LMHeadModel.from_pretrained("gpt2-medium")
ds = lambda p: TextDataset(tokenizer=tok, file_path=p, block_size=512)
coll = DataCollatorForLanguageModeling(tokenizer=tok, mlm=False)

args = TrainingArguments("./out", num_train_epochs=1, per_device_train_batch_size=2, eval_steps=200, save_steps=200, logging_steps=50, fp16=torch.cuda.is_available())
t = Trainer(model=m, args=args, train_dataset=ds("train.txt"), eval_dataset=ds("eval.txt"), tokenizer=tok, data_collator=coll)
t.train(); t.save_model("best"); tok.save_pretrained("best")
