import torch
from transformers import AutoModelForCausalLM

from neurorap.config import ModelConfig
from neurorap.data.tokenizer import RapDataTokenizer


def load_model(model_cfg: ModelConfig) -> tuple[AutoModelForCausalLM, RapDataTokenizer]:
    rap_tokenizer = RapDataTokenizer(model_cfg.hf_id)
    vocab_size = len(rap_tokenizer.tokenizer)

    if model_cfg.use_qlora:
        model = _load_qlora(model_cfg, vocab_size)
    else:
        model = AutoModelForCausalLM.from_pretrained(model_cfg.hf_id)
        model.resize_token_embeddings(vocab_size)
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        model = model.to(device)

    model.config.pad_token_id = rap_tokenizer.tokenizer.eos_token_id
    return model, rap_tokenizer


def _load_qlora(model_cfg: ModelConfig, vocab_size: int) -> AutoModelForCausalLM:
    from peft import LoraConfig, TaskType, get_peft_model, prepare_model_for_kbit_training
    from transformers import BitsAndBytesConfig

    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_use_double_quant=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.bfloat16,
    )

    model = AutoModelForCausalLM.from_pretrained(
        model_cfg.hf_id,
        quantization_config=bnb_config,
        device_map="auto",
    )
    model.resize_token_embeddings(vocab_size)
    model = prepare_model_for_kbit_training(model)

    lora_cfg = LoraConfig(
        r=model_cfg.lora_r,
        lora_alpha=model_cfg.lora_alpha,
        target_modules=list(model_cfg.lora_target_modules),
        lora_dropout=model_cfg.lora_dropout,
        bias="none",
        task_type=TaskType.CAUSAL_LM,
    )
    model = get_peft_model(model, lora_cfg)
    model.print_trainable_parameters()
    return model
