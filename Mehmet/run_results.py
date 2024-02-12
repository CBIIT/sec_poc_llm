import glob
import json

import evaluate
import pandas as pd
import tiktoken


def tokenizer(string: str, encoding_name: str = "cl100k_base") -> int:
    """Returns the number of tokens in a text string.
    [how to count tokens](https://github.com/openai/openai-cookbook/blob/main/examples/How_to_count_tokens_with_tiktoken.ipynb)"""
    encoding = tiktoken.get_encoding(encoding_name)
    return encoding.encode(string)


def compute_rouge(preds: list[str], ec_section: str):
    references = [
        criterion.lower() for criterion in ec_section.split("\n") if criterion.strip()
    ]
    rouge = evaluate.load("rouge")
    return rouge.compute(
        predictions=[p.lower() for p in preds],
        references=[references] * len(preds),
        tokenizer=tokenizer,
    )


def compute_bleu(preds: list[str], ec_section: str):
    references = [
        criterion.lower() for criterion in ec_section.split("\n") if criterion.strip()
    ]
    bleu = evaluate.load("bleu")
    return bleu.compute(
        predictions=[p.lower() for p in preds],
        references=[references] * len(preds),
        smooth=True,
        tokenizer=tokenizer,
    )


df = pd.DataFrame(
    columns=[
        "trial",
        "question_n",
        "question",
        "answer",
        "source_similarity",
        "addl_attrs",
    ]
)
outputfs = glob.glob("outputs/*")
for f in outputfs:
    print(f)
    if "trial_01" not in f:
        continue
    with open(f) as file:
        outputs = json.load(file)
    with open(f.replace("outputs", "trials").replace("json", "txt")) as file:
        ec_section = file.read()

    # df.loc[len(df.index)] = [f, ec_section] + [None] * (len(df.columns) - 2)
    for output in outputs:
        for answer in output["answers"]:
            df.loc[len(df.index)] = [
                f,
                output["idx"],
                output["question"],
                answer.get("value"),
                compute_bleu([answer["value"]], ec_section)["bleu"]
                if answer.get("value")
                else "None",
                ", ".join(
                    [
                        f"{key}={addl_attr}"
                        for key, addl_attr in answer.items()
                        if key != "value"
                    ]
                ),
            ]
df = df.sort_values(by=["trial"])
df.to_csv("answers.csv", index=False)
