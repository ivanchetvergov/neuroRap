import re
import pandas as pd
from typing import Dict, List
from transformers import AutoTokenizer

class RapDataTokenizer:

    def __init__(self, base_model_name: str = "sberbank-ai/rugpt3small_based_on_gpt2"):
        self.tokenizer = AutoTokenizer.from_pretrained(base_model_name)
        self._add_special_tokens()

    def _add_special_tokens(self):
        special_tokens = {
            'additional_special_tokens': [
                '<META>', '</META>',
                '<LYRICS>', '</LYRICS>',
                '<SEC>', '</SEC>',

                '<VERSE>', '<CHORUS>', '<BRIDGE>', '<INTRO>', '<OUTRO>',
            ]
        }

        num_added = self.tokenizer.add_special_tokens(special_tokens)
        self.tokenizer.pad_token = self.tokenizer.eos_token

        print(f"Добавлено {num_added} специальных токенов")
        print(f"Размер словаря: {len(self.tokenizer)}")

    def extract_sections(self, lyrics: str) -> List[tuple]:
        sections = []

        patterns = {
            'INTRO': r'\[Интро[^\]]*\]',
            'VERSE': r'\[Куплет[^\]]*\]',
            'CHORUS': r'\[Припев[^\]]*\]',
            'BRIDGE': r'\[Bridge[^\]]*\]',
            'OUTRO': r'\[Аутро[^\]]*\]'
        }

        positions = []
        for section_type, pattern in patterns.items():
            for match in re.finditer(pattern, lyrics, re.IGNORECASE):
                positions.append((match.start(), section_type, match.group()))

        positions.sort()

        for i, (pos, sec_type, header) in enumerate(positions):
            start = pos + len(header)
            end = positions[i + 1][0] if i + 1 < len(positions) else len(lyrics)
            content = lyrics[start:end].strip()

            if content:
                sections.append((sec_type, content))

        return sections

    def structure_row(self, row: pd.Series) -> str:

        artist = str(row.get('artist', 'Unknown'))

        tags_str = str(row.get('tags', ''))
        tags = [t.strip() for t in tags_str.split(',')[:3] if t.strip()]
        tags_formatted = ', '.join(tags) if tags else 'Hip-Hop'

        meta_block = (
            f"<META> [{artist}] [{tags_formatted}] </META>"
        )

        lyrics = str(row.get('lyrics', ''))
        sections = self.extract_sections(lyrics)

        if not sections:
            clean_lyrics = re.sub(r'\[.*?\]', '', lyrics).strip()
            lyrics_block = f"<LYRICS>\n<SEC><VERSE>\n{clean_lyrics}\n</SEC>\n</LYRICS>"
        else:
            formatted_sections = []
            for sec_type, content in sections:
                clean_content = re.sub(r'\[.*?\]', '', content).strip()
                if clean_content:
                    formatted_sections.append(
                        f"<SEC><{sec_type}>\n{clean_content}\n</SEC>"
                    )

            lyrics_block = "<LYRICS>\n" + "\n".join(formatted_sections) + "\n</LYRICS>"

        return f"{meta_block}\n{lyrics_block}"

    def process_dataframe(self, df: pd.DataFrame, output_column: str = 'tokenized_text') -> pd.DataFrame:
        print("Обработка датафрейма...")

        df_copy = df.copy()
        df_copy[output_column] = df_copy.apply(self.structure_row, axis=1)

        avg_length = df_copy[output_column].str.len().mean()
        print(f"Обработано строк: {len(df_copy)}")
        print(f"Средняя длина текста: {avg_length:.0f} символов")

        return df_copy

    def prepare_for_training(self, df: pd.DataFrame, text_column: str = 'tokenized_text') -> Dict:
        """
        Подготавливает данные для использования в Hugging Face Dataset.
        """
        return {'text': df[text_column].tolist()}

    def create_generation_prompt(self, artist: str, tags: List[str], section_type: str = 'VERSE') -> str:

        tags_str = ', '.join(tags[:3])

        meta = (
            f"<META> [{artist}] [{tags_str}]  </META>"
        )
        section_start = f"<LYRICS>\n<SEC><{section_type.upper()}>"

        return f"{meta}\n{section_start}\n"


def load_and_process_csv(csv_path: str, tokenizer: RapDataTokenizer) -> pd.DataFrame:
    print(f"Загрузка файла: {csv_path}")

    column_names = [
        'index', 'artist', 'title', 'lyrics', 'structured_text',
        'tags', 'primary_artist', 'album',
        'tempo', 'energy', 'valence', 'danceability' # Эти колонки будут игнорироваться в structure_row
    ]

    df = pd.read_csv(csv_path, names=column_names, skiprows=1)

    print(f"Загружено {len(df)} строк")
    print(f"Колонки: {', '.join(df.columns)}")

    df_processed = tokenizer.process_dataframe(df)

    return df_processed


def save_processed_data(df: pd.DataFrame, output_csv: str, output_txt: str):
    df.to_csv(output_csv, index=False)
    print(f"💾 CSV сохранён: {output_csv}")

    with open(output_txt, 'w', encoding='utf-8') as f:
        texts = df['tokenized_text'].tolist()
        f.write('\n\n'.join(texts))

    print(f"TXT сохранён: {output_txt}")



if __name__ == "__main__":
    print("=" * 60)
    print("ТЕСТИРОВАНИЕ RapDataTokenizer (БЕЗ АУДИО-МЕТРИК)")
    print("=" * 60 + "\n")

    tokenizer = RapDataTokenizer()

    test_data = {
        'artist': ['Boulevard Depo'],
        'title': ['Friendly Fire'],
        'lyrics': ['[Интро]\nМ м, м м\n[Куплет]\nЗависть тебя жрёт\n[Припев]\nТы попал под дым'],
        'tags': ['Cloud Rap,New School,Experimental'],
        'tempo': [float('nan')],
        'energy': [float('nan')],
        'valence': [float('nan')],
        'danceability': [float('nan')]
    }

    df_test = pd.DataFrame(test_data)

    print("Тестовый датафрейм (данные игнорируются):")
    print(df_test[['artist', 'tempo', 'energy', 'valence']].to_string())
    print("\n" + "=" * 60 + "\n")

    df_processed = tokenizer.process_dataframe(df_test)

    print("РЕЗУЛЬТАТ ТОКЕНИЗАЦИИ:")
    print("=" * 60)
    print(df_processed['tokenized_text'].iloc[0])
    print("=" * 60 + "\n")

    prompt = tokenizer.create_generation_prompt(
        artist="Хаски",
        tags=["Dark", "Industrial"],
        section_type="VERSE"
    )

    print("ПРОМПТ ДЛЯ ГЕНЕРАЦИИ:")
    print("=" * 60)
    print(prompt)
    print("=" * 60)