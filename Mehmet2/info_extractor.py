from pathlib import Path
from typing import Union

import pandas as pd
import yaml

from Mehmet2.gpt_client import (
    GPTClient,
    assistant_message,
    user_message,
)
from Mehmet2.logging import logger

FILES_CACHE = {}


class QuestionParser:
    _questions: list[dict[str, str]]
    _question_idx: int

    def __init__(self, questions_file: Union[str, Path]) -> None:
        """Parser of YAML file containing an array of `prompt` and `question` items.

        Arguments:
            questions_file -- the pathname of the YAML file.
        """
        if questions_file in FILES_CACHE:
            self._questions = FILES_CACHE[questions_file]
        else:
            with open(questions_file) as fp:
                self._questions = yaml.safe_load(fp)
                FILES_CACHE[questions_file] = self._questions

    def skip_to(self, question_n: int):
        """Set the starting question number to begin the iteration."""
        self._question_idx = question_n

    def questions(self):
        """Iterate over the questions."""
        for entry in self._questions[self._question_idx :]:
            yield entry["prompt"], entry["question"]


def serialize(output_file: Union[str, Path], **kwargs):
    headers = kwargs.keys()
    data = kwargs.values()
    df = pd.DataFrame([data], columns=headers)
    df.to_csv(output_file, mode="a", header=not Path(output_file).exists(), index=False)


def process_questions(
    gpt: GPTClient,
    questions_file: Union[str, Path],
    question_n: int = 0,
    chat_history: list[dict[str, str]] = [],
    prompt2answer: dict = {},
    results: list[dict[str, str]] = [],
    output_file: str = None,
):
    p2a_local = prompt2answer.copy()
    question_parser = QuestionParser(questions_file)
    question_parser.skip_to(question_n)

    for prompt, question in question_parser.questions():
        question = question.format(**p2a_local)
        logger.debug(f"Prompt: {question}")
        chat_history.append(user_message(question))
        logger.info(f"Token count: {gpt.count_message_tokens(chat_history)}")

        response = gpt.send_messages(chat_history)
        logger.debug(f"Response: {response.raw}")
        chat_history.append(assistant_message(response.raw))
        if output_file:
            serialize(
                output_file,
                question_number=question_n,
                prompt_type=prompt,
                prompt=question,
                raw=response.raw,
                source_text=response.source_text,
                answer=response.answer,
                entities=response.entities,
            )

        if (
            prompt == "cohort"
            and response.is_conjunctive()
            or prompt == "organ"
            and response.is_disjunctive()
        ):
            for entity in response.entities:
                p2a_local[prompt] = entity
                logger.info(f"{question_n: > 3}. {prompt} {entity}")
                process_questions(
                    gpt=gpt,
                    questions_file=questions_file,
                    question_n=question_n + 1,
                    prompt2answer=p2a_local,
                    chat_history=chat_history.copy(),
                    results=results,
                    output_file=output_file,
                )
            return results
        elif prompt == "organ" and len(response.entities) > 1:
            entity_groups = response.split_as_disjunctive()
            for entity_g in entity_groups:
                p2a_local[prompt] = entity_g
                logger.info(f"{question_n: > 3}. {prompt} {entity_g}")
                process_questions(
                    gpt=gpt,
                    questions_file=questions_file,
                    question_n=question_n + 1,
                    prompt2answer=p2a_local,
                    chat_history=chat_history.copy(),
                    results=results,
                    output_file=output_file,
                )
            return results
        else:
            p2a_local[prompt] = response.answer
            logger.info(f"{question_n: > 3}. {prompt} {response.answer}")
            question_n += 1

    results.append(p2a_local)
    return results
