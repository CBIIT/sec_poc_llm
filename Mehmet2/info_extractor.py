from datetime import datetime
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


# PROCESS-QUESTIONS
def process_questions(
    gpt: GPTClient,
    questions_file: Union[str, Path],
    # Initialization Line 3 question ← 1 (using 0-based indexing)
    question_n: int = 0,
    chat_history: list[dict[str, str]] = [],
    # Initialization Line 3 prompt2answer_dict ← ∅
    prompt2answer: dict = {},
    output_file: str = None,
):
    """This is the implementation of the PROCESS-QUESTIONS algorithm from Line 4.

    Arguments:
        gpt -- The Azure OpenAI GPT client.
        questions_file -- Line 1. `question-file`.

    Keyword Arguments:
        question_n -- Line 1. `question` (default: {0}).
        chat_history -- Used to preserve the chat session (default: {[]}).
        prompt2answer -- Line 1. `prompt2answer_dict` (default: {{}}).
        output_file -- A filepath to save each response to (default: {None}).

    Returns:
        _description_
    """
    results = []
    # Line 2
    p2a_local = prompt2answer.copy()
    # Line 3
    question_parser = QuestionParser(questions_file)
    # Line 4
    question_parser.skip_to(question_n)

    # Line 5 and 6
    for prompt, question in question_parser.questions():
        # Line 7 and 8
        question = question.format(**p2a_local)
        logger.debug(f"Prompt: {question}")
        chat_history.append(user_message(question))
        logger.info(f"Token count: {gpt.count_message_tokens(chat_history)}")

        #  Line 9 and 10
        response = gpt.send_messages(chat_history)
        logger.debug(f"Response: {response.raw}")
        chat_history.append(assistant_message(response.raw))
        if output_file:
            serialize(
                output_file,
                timestamp=datetime.now().strftime("%H:%M:%S"),
                question_number=question_n,
                prompt_type=prompt,
                prompt=question,
                organ=p2a_local.get("organ"),
                cohort=p2a_local.get("cohort"),
                raw=response.raw,
                source_text=response.source_text,
                answer=response.answer,
                entities=response.entities,
            )

        # Line 11
        if (
            prompt == "cohort"
            and response.is_conjunctive()
            or prompt == "organ"
            and response.is_disjunctive()
        ):
            # Line 12
            for entity in response.entities:
                # Line 13
                p2a_local[prompt] = entity
                # Line 14
                logger.info(f"{question_n: > 3}. {prompt} {entity}")
                # Line 15
                entity_results = process_questions(
                    gpt=gpt,
                    questions_file=questions_file,
                    question_n=question_n + 1,
                    prompt2answer=p2a_local,
                    chat_history=chat_history.copy(),
                    output_file=output_file,
                )
                results += entity_results
            # Line 16
            return results
        # Repeat of Lines 11 - 16 IF the organ response is not disjunctive
        elif prompt == "organ" and len(response.entities) > 1:
            entity_groups = response.split_as_disjunctive()
            for entity_g in entity_groups:
                p2a_local[prompt] = entity_g
                logger.info(f"{question_n: > 3}. {prompt} {entity_g}")
                entity_g_results = process_questions(
                    gpt=gpt,
                    questions_file=questions_file,
                    question_n=question_n + 1,
                    prompt2answer=p2a_local,
                    chat_history=chat_history.copy(),
                    output_file=output_file,
                )
                results += entity_g_results
            return results
        # Line 17
        else:
            # Line 18
            p2a_local[prompt] = response.answer
            # Line 19
            logger.info(f"{question_n: > 3}. {prompt} {response.answer}")
            # Line 20
            question_n += 1

    # Return the collected results.
    results.append(p2a_local)
    return results
