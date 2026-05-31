PYTHON := python3
export PYTHONPATH := .

.PHONY: collect train generate bot clean-data clean-model clean

collect:
	$(PYTHON) scripts/collect.py

train:
	$(PYTHON) scripts/train.py

generate:
	$(PYTHON) scripts/generate.py $(ARGS)

bot:
	$(PYTHON) scripts/bot.py

clean-data:
	rm -f data/checkpoint.csv data/lyrics_df.csv

clean-model:
	rm -rf models/

clean: clean-data clean-model
