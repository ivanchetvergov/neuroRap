from config import TRAIN_CONFIG
from src.train.trainer import train


def main() -> None:
    print(f"Config: {TRAIN_CONFIG}")
    train(TRAIN_CONFIG)


if __name__ == "__main__":
    main()
