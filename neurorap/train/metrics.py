import json
import math
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any

import torch
from transformers import TrainerCallback, TrainerControl, TrainerState


class LMMetricsCallback(TrainerCallback):
    def __init__(self, output_path: Path, model_name: str, config_dict: dict[str, Any]):
        self._path = output_path
        self._history: list[dict[str, Any]] = []
        self._meta: dict[str, Any] = {
            "model_name": model_name,
            "run_id": datetime.now().isoformat(timespec="seconds"),
            "config": config_dict,
        }

    def on_evaluate(
        self,
        args,
        state: TrainerState,
        control: TrainerControl,
        metrics: dict[str, float],
        **kwargs,
    ) -> None:
        eval_loss = metrics.get("eval_loss", float("nan"))
        perplexity = math.exp(min(eval_loss, 100))

        train_loss = next(
            (e["loss"] for e in reversed(state.log_history) if "loss" in e),
            None,
        )

        self._history.append({
            "epoch": round(state.epoch or 0, 2),
            "step": state.global_step,
            "train_loss": round(train_loss, 4) if train_loss else None,
            "eval_loss": round(eval_loss, 4),
            "perplexity": round(perplexity, 4),
        })
        self._save()

    def finalize(self, generation_metrics: dict[str, Any]) -> None:
        best = min(self._history, key=lambda x: x["eval_loss"], default={})
        data = {
            **self._meta,
            "training_history": self._history,
            "best_epoch": best.get("epoch"),
            "best_eval_loss": best.get("eval_loss"),
            "best_perplexity": best.get("perplexity"),
            "generation_metrics": generation_metrics,
        }
        self._path.write_text(json.dumps(data, ensure_ascii=False, indent=2))

    def _save(self) -> None:
        data = {**self._meta, "training_history": self._history}
        self._path.write_text(json.dumps(data, ensure_ascii=False, indent=2))


def compute_generation_metrics(
    model,
    rap_tokenizer,
    sample_artists: list[str],
    device: torch.device,
    n_per_artist: int = 3,
    max_tokens: int = 150,
) -> dict[str, Any]:
    model.eval()
    all_tokens: list[str] = []
    lengths: list[int] = []

    for artist in sample_artists:
        from neurorap.artists import ARTIST_DEFAULT_TAGS
        tags = ARTIST_DEFAULT_TAGS.get(artist, ["Hip-Hop"])
        prompt = rap_tokenizer.create_generation_prompt(artist, tags)

        inputs = rap_tokenizer.tokenizer(prompt, return_tensors="pt").to(device)

        for _ in range(n_per_artist):
            with torch.no_grad():
                out = model.generate(
                    **inputs,
                    max_new_tokens=max_tokens,
                    do_sample=True,
                    temperature=0.9,
                    top_k=50,
                    top_p=0.9,
                    repetition_penalty=1.5,
                    pad_token_id=rap_tokenizer.tokenizer.eos_token_id,
                )
            text = rap_tokenizer.tokenizer.decode(out[0], skip_special_tokens=True)
            tokens = text.split()
            all_tokens.extend(tokens)
            lengths.append(len(tokens))

    return {
        "distinct_1": _distinct_n(all_tokens, 1),
        "distinct_2": _distinct_n(all_tokens, 2),
        "avg_length_tokens": round(sum(lengths) / len(lengths), 1) if lengths else 0,
        "n_samples": len(lengths),
    }


def _distinct_n(tokens: list[str], n: int) -> float:
    if len(tokens) < n:
        return 0.0
    ngrams = [tuple(tokens[i: i + n]) for i in range(len(tokens) - n + 1)]
    return round(len(set(ngrams)) / len(ngrams), 4)
