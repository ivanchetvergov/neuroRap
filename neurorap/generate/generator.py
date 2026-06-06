from pathlib import Path

import torch
from transformers import AutoModelForCausalLM

from neurorap.artists import ARTIST_DEFAULT_TAGS
from neurorap.data.tokenizer import RapDataTokenizer
from neurorap.generate.cleaner import clean_generated_lyrics


class Generator:
    def __init__(self, model_path: Path | str, base_model: str = "sberbank-ai/rugpt3small_based_on_gpt2"):
        self._rap_tokenizer = RapDataTokenizer(base_model)
        self._model = AutoModelForCausalLM.from_pretrained(str(model_path))
        self._device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self._model = self._model.to(self._device).eval()
        print(f"Generator ready on {self._device}")

    def generate(
        self,
        artist: str,
        tags: list[str] | None = None,
        seed: str = "",
        section: str = "VERSE",
        max_tokens: int = 200,
        temperature: float = 0.85,
        top_k: int = 40,
        top_p: float = 0.85,
        repetition_penalty: float = 1.8,
    ) -> list[str]:
        resolved_tags = tags or ARTIST_DEFAULT_TAGS.get(artist, ["Hip-Hop"])
        prompt = self._rap_tokenizer.create_generation_prompt(artist, resolved_tags, section)
        if seed:
            prompt += seed + "\n"

        inputs = self._rap_tokenizer.tokenizer(
            prompt, return_tensors="pt", truncation=True
        )
        input_ids = inputs["input_ids"].to(self._device)
        attention_mask = inputs["attention_mask"].to(self._device)

        with torch.no_grad():
            output_ids = self._model.generate(
                input_ids,
                attention_mask=attention_mask,
                max_length=input_ids.shape[1] + max_tokens,
                do_sample=True,
                temperature=temperature,
                top_k=top_k,
                top_p=top_p,
                repetition_penalty=repetition_penalty,
                num_return_sequences=1,
                pad_token_id=self._rap_tokenizer.tokenizer.pad_token_id,
            )

        raw = self._rap_tokenizer.tokenizer.decode(output_ids[0], skip_special_tokens=False)
        return clean_generated_lyrics(raw)
