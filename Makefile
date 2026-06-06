PYTHON := python3
export PYTHONPATH := .

.PHONY: collect train generate bot clean-data clean-model clean

# ── setup ────────────────────────────────────────────────────────────────────

install:
	pip install -r requirements.txt

# ── data collection ──────────────────────────────────────────────────────────

collect:
	$(PYTHON) scripts/collect_genius.py

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
	rm -f data/lyrics_df.csv

clean-model:
	rm -rf models/

clean: clean-data clean-model
