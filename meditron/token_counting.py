from model import get_token_len

MAX_W_SIZE = 2048
AVG_PROMPT_LEN = 0
AVG_RES_LEN = 0
MIN_PROMPT_LEN = 0
MAX_PROMPT_LEN = 0


def globalize_token_metrics(examples):
    global AVG_PROMPT_LEN, AVG_RES_LEN, MIN_PROMPT_LEN, MAX_PROMPT_LEN

    total = 0
    total_res = 0
    minm = 2000
    maxm = 0
    for example in examples:
        context_len = get_token_len(example['context'])
        answer_len = get_token_len(example['answer'])
        combined_len = context_len + answer_len
        if combined_len < minm:
            minm = combined_len
        if combined_len > maxm:
            maxm = combined_len
        total += combined_len
        total_res += answer_len

    AVG_PROMPT_LEN = total // len(examples)
    AVG_RES_LEN = total_res // len(examples)
    MIN_PROMPT_LEN = minm
    MAX_PROMPT_LEN = maxm
