PYTHON := python3
export PYTHONPATH := .

.PHONY: collect train train-large train-mgpt train-qwen generate bot clean-data clean-model clean install

# ── setup ────────────────────────────────────────────────────────────────────

install:
	pip install -r requirements.txt

# ── data collection ──────────────────────────────────────────────────────────

collect:
	$(PYTHON) scripts/collect_genius.py

# ── training ─────────────────────────────────────────────────────────────────

train: train-large

train-large:
	$(PYTHON) scripts/train.py --model rugpt3large

train-mgpt:
	$(PYTHON) scripts/train.py --model mgpt

train-qwen:
	$(PYTHON) scripts/train.py --model qwen_qlora

# ── generation ───────────────────────────────────────────────────────────────

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
