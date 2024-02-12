# Note: The openai-python library support for Azure OpenAI is in preview.
# Note: This code sample requires OpenAI Python library version 0.28.1 or lower.
import argparse
import json
import os
import backoff

import dotenv
import openai
from fabulous.color import italic, white
from models import *

dotenv.load_dotenv()


def parse_answer(content: str):
    entities = []
    for line in content.split("\n"):
        line = line.strip()
        if not line:
            continue
        try:
            assert is_model(line)
            entities.append(eval(line))
        except:
            if line.startswith("SourceText("):
                entities.append(SourceText(line.removeprefix("SourceText(")))
            elif line.startswith("Answer("):
                entities.append(Answer(line.removeprefix("Answer(")))
            elif entities:
                entities[-1].value += line.removesuffix(")")
            else:
                entities.append(Answer(line))

    return entities


@backoff.on_exception(backoff.expo, openai.error.RateLimitError)
def do_generate(*args, **kwargs):
    return openai.ChatCompletion.create(*args, **kwargs)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--trialf",
        type=str,
        default="trials/trial_01.txt",
        help="Name of file containing EC section.",
    )
    parser.add_argument(
        "--startq",
        type=int,
        default=0,
        help="Starting question index (0-based).",
    )
    parser.add_argument(
        "--endq",
        type=int,
        default=-1,
        help="Ending question index (0-based, -1 continues to the end).",
    )
    parser.add_argument(
        "--new_tokens",
        type=int,
        default=512,
        help="Controls how many tokens are generated.",
    )
    parser.add_argument(
        "--outf",
        type=str,
        default="outputs.json",
        help="Output the results to JSON file.",
    )
    args = parser.parse_args()
    openai.api_type = "azure"
    openai.api_base = os.environ["OPENAI_API_BASE"]
    openai.api_version = "2023-07-01-preview"
    openai.api_key = os.environ["OPENAI_API_KEY"]

    with open(args.trialf) as filein:
        ec_section = filein.read().strip()
    if not os.path.exists(args.outf):
        with open(args.outf, "w") as fileout:
            json.dump([], fileout)
    with open(args.outf) as fileout:
        outputs = json.load(fileout)
    with open("inputs/prompt_system.txt") as filein:
        prompt_sys = filein.read().strip()
    with open("inputs/prompt_template.txt") as filein:
        prompt_t = filein.read().strip()
    with open("inputs/questions.txt") as filein:
        questions = filein.read().strip()
        questions = questions.split("----")

    message_text = [
        {"role": "system", "content": prompt_sys},
    ]
    for idx, q in enumerate(questions):
        if idx < args.startq:
            continue
        if args.endq != -1:
            if idx > args.endq:
                break

        q = q.strip()

        if q.startswith("CONFIRM"):
            assert idx != args.startq, "CONFIRM must be a follow-up query."
            q = q.removeprefix("CONFIRM: ")
            # Use answers from last question as the confirmation prompt
            last_answers = [
                e.value
                for e in parse_answer(message_text[-1]["content"])
                if isinstance(e, Answer)
            ]
            q = q.format(", ".join(last_answers))
            message_text.append(
                {
                    "role": "user",
                    "content": q,
                }
            )
        else:
            if idx > args.startq:
                # At least one query/answer has been added to the message history, so don't add redundant info.
                message_text.append(
                    {
                        "role": "user",
                        "content": q,
                    }
                )
            else:
                # This is the first query, so add relevant conversation info.
                message_text.append(
                    {
                        "role": "user",
                        "content": prompt_t.format(prompt=q, ec_section=ec_section),
                    }
                )

        print(italic(f"{idx}. {q}"))

        completion = do_generate(
            engine="gpt4_preview",
            messages=message_text,
            max_tokens=args.new_tokens,
            seed=0,
            temperature=0.2,
            stream=False,
        )
        content = completion["choices"][0]["message"]["content"]
        new_tokens = completion["usage"]["completion_tokens"]
        print(white(content))
        print(italic("New tokens:", new_tokens))
        print()
        message_text.append({"role": "assistant", "content": content})

        entities = parse_answer(content)
        outputs.append(
            {
                "idx": idx,
                "question": message_text[-2]["content"],
                "answers": [e for e in entities if isinstance(e, Answer)],
                "source_texts": [e for e in entities if isinstance(e, SourceText)],
                "_new_tokens": new_tokens,
            }
        )
        with open(args.outf, "w") as fileout:
            json.dump(outputs, fileout, indent=2, cls=ModelJSONEncoder)
    if idx == len(questions):
        print("END")


if __name__ == "__main__":
    main()
