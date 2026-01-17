import re
from typing import List


def clean_generated_lyrics(raw_output: str) -> List[str]:

    # 1. Удаление всех мета-блоков и их содержимого (<META>...</META>)
    text = re.sub(r'<META>.*?<\/META>', '', raw_output, flags=re.DOTALL)

    # 2. Удаление структурных тегов <LYRICS> и </LYRICS>
    text = text.replace('<LYRICS>', '').replace('</LYRICS>', '')

    # 3. Замена тегов секций на человекочитаемые заголовки (Куплет, Припев и т.д.)
    def replace_section_tag(match):
        sec_type = match.group(1).capitalize()

        # Переводим основные русские теги
        if sec_type == 'VERSE':
            sec_type = 'Куплет'
        elif sec_type == 'CHORUS':
            sec_type = 'Припев'
        elif sec_type == 'BRIDGE':
            sec_type = 'Бридж'
        elif sec_type == 'INTRO':
            sec_type = 'Интро'
        elif sec_type == 'OUTRO':
            sec_type = 'Аутро'

        return f"\n\n[{sec_type}]\n"

        # Шаг 3a: Замена открывающих тегов

    text = re.sub(r'<SEC><(VERSE|CHORUS|BRIDGE|INTRO|OUTRO)>',
                  replace_section_tag,
                  text, flags=re.IGNORECASE)

    text = text.replace('</SEC>', '')

    # 4. Удаление любых оставшихся специальных токенов (например, <TM_LOW>, <EMPTY_METRIC>)
    text = re.sub(r'<[A-Z_ /]+>', '', text)

    # 4.5.  Вставка переносов строк после знаков препинания
    text = re.sub(r'([.?!])\s+', r'\1\n', text)

    # Дополнительно: вставка переноса после запятой, если далее идет заглавная буква
    text = re.sub(r'(,\s+)([А-ЯЁA-Z])', r',\n\2', text)

    # 5. Финальная очистка и нормализация пробелов
    text = re.sub(r'(\n\s*){3,}', '\n\n', text).strip()  # Сжать более двух пустых строк до двух

    # 6. Преобразование в список строк
    return text.split('\n')
