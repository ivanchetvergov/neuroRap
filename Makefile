PYTHON := python3
export PYTHONPATH := .

.PHONY: collect collect-genius collect-spotify merge train generate bot \
        clean-data clean-model clean

# ── data collection ─────────────────────────────────────────────────────────

collect-genius:
	$(PYTHON) scripts/collect_genius.py

collect-spotify:
	$(PYTHON) scripts/collect_spotify.py

# Genius идёт с начала списка, Spotify — с конца, встречаются в середине.
# -j2 запускает оба процесса параллельно; merge ждёт завершения обоих.
collect:
	$(MAKE) -j2 collect-genius collect-spotify
	$(PYTHON) scripts/merge_data.py

merge:
	$(PYTHON) scripts/merge_data.py

# ── model ────────────────────────────────────────────────────────────────────

train:
	$(PYTHON) scripts/train.py

generate:
	$(PYTHON) scripts/generate.py $(ARGS)

# ── bot ──────────────────────────────────────────────────────────────────────

bot:
	$(PYTHON) scripts/bot.py

# ── cleanup ──────────────────────────────────────────────────────────────────

clean-data:
	rm -f data/checkpoint_genius.csv data/checkpoint_spotify.csv data/lyrics_df.csv

clean-model:
	rm -rf models/

clean: clean-data clean-model
