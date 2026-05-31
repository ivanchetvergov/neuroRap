from dataclasses import dataclass
from pathlib import Path

DATA_DIR = Path("data")
MODELS_DIR = Path("models")


@dataclass(frozen=True)
class TrainConfig:
    base_model: str = "sberbank-ai/rugpt3small_based_on_gpt2"
    block_size: int = 1024
    batch_size: int = 4
    epochs: int = 11
    learning_rate: float = 2e-5
    warmup_steps: int = 100
    weight_decay: float = 0.01
    gradient_accumulation_steps: int = 2


TRAIN_CONFIG = TrainConfig()
