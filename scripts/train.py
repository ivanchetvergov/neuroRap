import argparse
import logging

from neurorap.config import MODEL_REGISTRY, TRAIN_CONFIG
from neurorap.train.trainer import train

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)s  %(message)s",
    datefmt="%H:%M:%S",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Обучение модели генерации рэп-лирики")
    parser.add_argument(
        "--model",
        choices=list(MODEL_REGISTRY),
        default="rugpt3large",
        help="Модель для обучения",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    model_cfg = MODEL_REGISTRY[args.model]
    train(model_cfg, TRAIN_CONFIG)


if __name__ == "__main__":
    main()
