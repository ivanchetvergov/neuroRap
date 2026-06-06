import argparse

from neurorap.artists import ARTIST_LIST
from neurorap.config import MODEL_REGISTRY, MODELS_DIR
from neurorap.generate.generator import Generator


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Генерация рэп-лирики")
    parser.add_argument("--artist", "-a", default="PHARAOH", help="Имя артиста")
    parser.add_argument("--model", "-m", choices=list(MODEL_REGISTRY), default="rugpt3large", help="Имя модели")
    parser.add_argument("--seed", "-s", default="", help="Затравочный текст")
    parser.add_argument("--section", default="VERSE", choices=["VERSE", "CHORUS", "BRIDGE", "INTRO", "OUTRO"])
    parser.add_argument("--max-tokens", type=int, default=200)
    parser.add_argument("--temperature", type=float, default=0.85)
    parser.add_argument("--repetition-penalty", type=float, default=1.8)
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.artist not in ARTIST_LIST:
        print(f"Неизвестный артист. Доступные:\n{chr(10).join(ARTIST_LIST)}")
        return

    generator = Generator(model_path=MODELS_DIR / args.model / "final")

    lines = generator.generate(
        artist=args.artist,
        seed=args.seed,
        section=args.section,
        max_tokens=args.max_tokens,
        temperature=args.temperature,
        repetition_penalty=args.repetition_penalty,
    )

    print(f"\n[{args.artist}]\n")
    print("\n".join(line for line in lines if line.strip()))


if __name__ == "__main__":
    main()
