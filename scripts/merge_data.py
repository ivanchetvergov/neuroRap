import pandas as pd
from config import DATA_DIR


def main() -> None:
    genius_path = DATA_DIR / "checkpoint_genius.csv"
    spotify_path = DATA_DIR / "checkpoint_spotify.csv"
    output_path = DATA_DIR / "lyrics_df.csv"

    if not genius_path.exists():
        raise FileNotFoundError(f"Genius checkpoint не найден: {genius_path}")

    genius_df = pd.read_csv(genius_path)
    print(f"Genius: {len(genius_df)} треков")

    if spotify_path.exists():
        spotify_df = pd.read_csv(spotify_path)
        print(f"Spotify: {len(spotify_df)} треков обогащено")
        merged = genius_df.merge(spotify_df, on=["artist", "title"], how="left")
    else:
        print("Spotify checkpoint не найден, аудио-фичи будут пустыми")
        merged = genius_df

    merged.to_csv(output_path, index=False)
    n_enriched = merged["energy"].notna().sum() if "energy" in merged.columns else 0
    print(f"\nФинальный датасет: {len(merged)} треков, {n_enriched} с аудио-фичами → {output_path}")


if __name__ == "__main__":
    main()
