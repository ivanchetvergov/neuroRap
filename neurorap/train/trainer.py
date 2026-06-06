import dataclasses
import logging

import pandas as pd
import torch
from datasets import Dataset
from transformers import (
    DataCollatorForLanguageModeling,
    EarlyStoppingCallback,
    Trainer,
    TrainingArguments,
)

from neurorap.config import DATA_DIR, MODELS_DIR, ModelConfig, TrainConfig
from neurorap.train.metrics import LMMetricsCallback, compute_generation_metrics
from neurorap.train.models import load_model

log = logging.getLogger(__name__)

_EVAL_ARTISTS = ["PHARAOH", "Oxxxymiron", "Скриптонит", "Kai Angel", "FACE"]


def train(model_cfg: ModelConfig, config: TrainConfig) -> None:
    log.info("Модель: %s (%s)", model_cfg.name, model_cfg.hf_id)

    model, rap_tokenizer = load_model(model_cfg)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    df = pd.read_csv(DATA_DIR / "lyrics_df.csv")
    df_processed = rap_tokenizer.process_dataframe(df)
    log.info("Датасет: %d треков", len(df_processed))

    dataset = Dataset.from_dict({"text": df_processed["tokenized_text"].tolist()})

    def tokenize(examples: dict) -> dict:
        return rap_tokenizer.tokenizer(examples["text"], padding=False)

    def group_texts(examples: dict) -> dict:
        concatenated = {k: sum(examples[k], []) for k in examples}
        total = (len(next(iter(concatenated.values()))) // config.block_size) * config.block_size
        result = {
            k: [v[i: i + config.block_size] for i in range(0, total, config.block_size)]
            for k, v in concatenated.items()
        }
        result["labels"] = result["input_ids"].copy()
        return result

    tokenized = dataset.map(tokenize, batched=True, num_proc=2, remove_columns=["text"])
    lm_dataset = tokenized.map(group_texts, batched=True, batch_size=1000, num_proc=2)
    split = lm_dataset.train_test_split(test_size=0.1, seed=42)
    log.info("Блоков train=%d eval=%d", len(split["train"]), len(split["test"]))

    output_dir = MODELS_DIR / model_cfg.name
    results_path = output_dir / "results.json"
    output_dir.mkdir(parents=True, exist_ok=True)

    config_dict = {**dataclasses.asdict(config), **dataclasses.asdict(model_cfg)}
    metrics_cb = LMMetricsCallback(results_path, model_cfg.name, config_dict)

    training_args = TrainingArguments(
        output_dir=str(output_dir / "checkpoints"),
        num_train_epochs=config.epochs,
        per_device_train_batch_size=model_cfg.batch_size,
        per_device_eval_batch_size=model_cfg.batch_size,
        learning_rate=model_cfg.learning_rate,
        warmup_steps=config.warmup_steps,
        weight_decay=config.weight_decay,
        gradient_accumulation_steps=model_cfg.gradient_accumulation_steps,
        optim="adamw_8bit",
        logging_dir=str(output_dir / "logs"),
        logging_steps=50,
        save_strategy="epoch",
        save_total_limit=2,
        eval_strategy="epoch",
        load_best_model_at_end=True,
        metric_for_best_model="eval_loss",
        greater_is_better=False,
        fp16=torch.cuda.is_available() and not model_cfg.use_qlora,
        bf16=model_cfg.use_qlora and torch.cuda.is_available(),
        gradient_checkpointing=model_cfg.gradient_checkpointing,
        dataloader_num_workers=2,
        ddp_find_unused_parameters=False,
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
        callbacks=[
            metrics_cb,
            EarlyStoppingCallback(early_stopping_patience=config.early_stopping_patience),
        ],
    )

    trainer.train()

    final_dir = output_dir / "final"
    final_dir.mkdir(parents=True, exist_ok=True)
    trainer.save_model(str(final_dir))
    rap_tokenizer.tokenizer.save_pretrained(str(final_dir))
    log.info("Модель сохранена: %s", final_dir)

    log.info("Считаю generation metrics...")
    gen_metrics = compute_generation_metrics(model, rap_tokenizer, _EVAL_ARTISTS, device)
    log.info("distinct-1=%.3f distinct-2=%.3f", gen_metrics["distinct_1"], gen_metrics["distinct_2"])

    metrics_cb.finalize(gen_metrics)
    log.info("Результаты сохранены: %s", results_path)
