# neuroRap

Проект по дообучению языковых моделей на русскоязычной рэп-лирике. Тексты собираются с Genius API, модель обучается генерировать лирику в стиле конкретных артистов.

## Стек

- PyTorch, Hugging Face Transformers, Datasets
- lyricsgenius для сбора данных
- Telegram Bot API для интерфейса генерации

## Модели

Поддерживаются три варианта обучения:

- `rugpt3large` — sberbank-ai/rugpt3large_based_on_gpt2, 760M параметров, полный fine-tune
- `mgpt` — ai-forever/mGPT, 1.3B параметров, полный fine-tune
- `qwen_qlora` — Qwen/Qwen2.5-7B, QLoRA (4-bit + LoRA)

## Запуск

Установка зависимостей:

```bash
make install
```

Сбор данных:

```bash
make collect
```

Обучение (по умолчанию rugpt3large):

```bash
make train
make train-mgpt
make train-qwen
```

Генерация из командной строки:

```bash
make generate ARGS="--artist PHARAOH --seed текст"
```

Телеграм-бот:

```bash
make bot
```

## Переменные окружения

Создай `.env` файл:

```env
GENIUS_ACCESS_TOKEN=...
TELEGRAM_BOT_TOKEN=...
```

## Датасет

49 артистов, ~7000 треков. После обучения каждая модель сохраняет `results.json` с метриками по эпохам: train loss, eval loss, perplexity, distinct-1/2.

## Структура

```text
neurorap/         пакет
  artists.py      список артистов и теги
  config.py       конфиги моделей и обучения
  collect/        сбор данных с Genius
  data/           токенизатор и структурирование текстов
  train/          пайплайн обучения, метрики, загрузка моделей
  generate/       инференс
  bot/            телеграм-бот
scripts/          точки входа для Makefile
```
