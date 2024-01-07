from torch import cuda, bfloat16
import transformers

model_id = "epfl-llm/meditron-7b"

device = f'cuda:{cuda.current_device()}' if cuda.is_available() else 'cpu'

# set quantization configuration to load large model with less GPU memory
# this requires the `bitsandbytes` library
bnb_config = transformers.BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type='nf4',
    bnb_4bit_use_double_quant=True,
    bnb_4bit_compute_dtype=bfloat16
)

model_config = transformers.AutoConfig.from_pretrained(
    model_id,
)

model = transformers.AutoModelForCausalLM.from_pretrained(
    model_id,
    trust_remote_code=True,
    config=model_config,
    quantization_config=bnb_config,
    device_map='auto',
)

tokenizer = transformers.AutoTokenizer.from_pretrained(
    model_id,
)

# enable evaluation mode to allow model inference
model.eval()

print(f"Model loaded on {device}")


def get_token_len(text: str):
    return len(tokenizer.encode(text))