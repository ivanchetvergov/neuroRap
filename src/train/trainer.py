import torch
import pandas as pd
from datasets import Dataset
from transformers import (
    AutoModelForCausalLM,
    DataCollatorForLanguageModeling,
    Trainer,
    TrainingArguments,
)

from config import DATA_DIR, MODELS_DIR, TrainConfig
from src.data.tokenizer import RapDataTokenizer


def train(config: TrainConfig) -> None:
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Device: {device}")

    rap_tokenizer = RapDataTokenizer(config.base_model)

    df = pd.read_csv(DATA_DIR / "lyrics_df.csv")
    df_processed = rap_tokenizer.process_dataframe(df)

    dataset = Dataset.from_dict({"text": df_processed["tokenized_text"].tolist()})

    def tokenize(examples: dict) -> dict:
        return rap_tokenizer.tokenizer(
            examples["text"],
            truncation=True,
            max_length=config.block_size,
            padding=False,
        )

    def group_texts(examples: dict) -> dict:
        concatenated = {k: sum(examples[k], []) for k in examples}
        total = (len(next(iter(concatenated.values()))) // config.block_size) * config.block_size
        result = {
            k: [v[i: i + config.block_size] for i in range(0, total, config.block_size)]
            for k, v in concatenated.items()
        }
        result["labels"] = result["input_ids"].copy()
        return result

    tokenized = dataset.map(tokenize, batched=True, num_proc=4, remove_columns=["text"])
    lm_dataset = tokenized.map(group_texts, batched=True, batch_size=1000, num_proc=4)
    split = lm_dataset.train_test_split(test_size=0.1, seed=42)

    model = AutoModelForCausalLM.from_pretrained(config.base_model).to(device)
    model.resize_token_embeddings(len(rap_tokenizer.tokenizer))
    model.config.pad_token_id = model.config.eos_token_id

    checkpoints_dir = MODELS_DIR / "checkpoints"
    final_dir = MODELS_DIR / "final"
    logs_dir = MODELS_DIR / "logs"

    training_args = TrainingArguments(
        output_dir=str(checkpoints_dir),
        num_train_epochs=config.epochs,
        per_device_train_batch_size=config.batch_size,
        per_device_eval_batch_size=config.batch_size,
        learning_rate=config.learning_rate,
        warmup_steps=config.warmup_steps,
        weight_decay=config.weight_decay,
        gradient_accumulation_steps=config.gradient_accumulation_steps,
        logging_dir=str(logs_dir),
        logging_steps=50,
        save_strategy="epoch",
        save_total_limit=3,
        eval_strategy="epoch",
        load_best_model_at_end=True,
        metric_for_best_model="eval_loss",
        fp16=torch.cuda.is_available(),
        report_to="none",
        seed=42,
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=split["train"],
        eval_dataset=split["test"],
        data_collator=DataCollatorForLanguageModeling(
            tokenizer=rap_tokenizer.tokenizer, mlm=False
        ),
    )

    trainer.train()

    final_dir.mkdir(parents=True, exist_ok=True)
    trainer.save_model(str(final_dir))
    rap_tokenizer.tokenizer.save_pretrained(str(final_dir))
    print(f"Модель сохранена: {final_dir}")
