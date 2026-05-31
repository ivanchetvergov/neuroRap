PYTHON := python3
export PYTHONPATH := .

.PHONY: collect collect-genius collect-spotify merge train generate bot \
        clean-data clean-model clean

# ── data collection ──────────────────────────────────────────────────────────

collect-genius:
	$(PYTHON) scripts/collect_genius.py

collect-spotify:
	$(PYTHON) scripts/collect_spotify.py

merge:
	$(PYTHON) scripts/merge_data.py

# Genius собирает лирику → Spotify обогащает аудио-фичами → merge
collect:
	$(MAKE) collect-genius
	$(MAKE) collect-spotify
	$(MAKE) merge

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
