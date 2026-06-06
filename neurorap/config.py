from dataclasses import dataclass, field
from pathlib import Path

DATA_DIR = Path("data")
MODELS_DIR = Path("models")


@dataclass(frozen=True)
class TrainConfig:
    block_size: int = 1024
    epochs: int = 10
    warmup_steps: int = 200
    weight_decay: float = 0.01
    early_stopping_patience: int = 3


@dataclass(frozen=True)
class ModelConfig:
    name: str
    hf_id: str
    batch_size: int
    gradient_accumulation_steps: int
    learning_rate: float
    use_qlora: bool = False
    lora_r: int = 16
    lora_alpha: int = 32
    lora_dropout: float = 0.05
    lora_target_modules: tuple[str, ...] = field(default_factory=tuple)


MODEL_REGISTRY: dict[str, ModelConfig] = {
    "rugpt3large": ModelConfig(
        name="rugpt3large",
        hf_id="sberbank-ai/rugpt3large_based_on_gpt2",
        batch_size=8,
        gradient_accumulation_steps=4,
        learning_rate=2e-5,
    ),
    "mgpt": ModelConfig(
        name="mgpt",
        hf_id="ai-forever/mGPT",
        batch_size=4,
        gradient_accumulation_steps=8,
        learning_rate=1e-5,
    ),
    "qwen_qlora": ModelConfig(
        name="qwen_qlora",
        hf_id="Qwen/Qwen2.5-7B",
        batch_size=4,
        gradient_accumulation_steps=8,
        learning_rate=2e-4,
        use_qlora=True,
        lora_r=16,
        lora_alpha=32,
        lora_target_modules=("q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"),
    ),
}

TRAIN_CONFIG = TrainConfig()
