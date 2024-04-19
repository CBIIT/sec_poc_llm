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
from Mehmet2.match_ncit import get_match

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
        self._question_idx = 0

    def skip_to(self, question_n: int):
        """Set the starting question number to begin the iteration."""
        self._question_idx = question_n

    def questions(self):
        """Iterate over the questions.
        Returns a 3-element tuple consisting of (
            prompt -- the prompt identifier,
            question -- the message to send to GPT,
            condition -- an optional str consisting of a lambda expression to evaluate before sending the prompt
        )
        """
        for entry in self._questions[self._question_idx :]:
            yield entry["prompt"], entry["question"], entry.get("condition")


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
    for prompt, question, condition in question_parser.questions():
        # Check if the prompt has a conditional expression to evaluate before sending to the GPT
        if condition:
            try:
                condition_fn = eval(condition, {"__builtins__": {}}, {})
                should_ask = bool(condition_fn(**p2a_local))
            except Exception as e:
                logger.error(e)
                logger.warning(
                    f"Skipping prompt {prompt} because the condition function failed to evaluate."
                )
                logger.debug(p2a_local)
                question_n += 1
                continue
            else:
                # If the condition is False, continue to the next question (i.e. skip this one)
                if not should_ask:
                    logger.info(
                        f"Skipping prompt {prompt} because the condition evaluated to False."
                    )
                    question_n += 1
                    continue

        # Line 7 and 8
        question = question.format(**p2a_local)
        logger.debug(f"Prompt: {question}")
        chat_history.append(user_message(question))
        logger.info(f"Token count: {gpt.count_message_tokens(chat_history)}")

        #  Line 9 and 10
        response = gpt.send_messages(chat_history)
        logger.debug(f"Response: {response.raw}")
        chat_history.append(assistant_message(response.raw))
        if prompt == "disease_names_lead" or prompt == "diseases":
            ncit_diseases = []
            disease_entities = (
                response.entities if len(response.entities) > 1 else [response.answer]
            )
            for disease in disease_entities:
                ncit_match = get_match(disease)
                ncit_diseases.append(ncit_match)
            p2a_local["ncit_" + prompt] = ncit_diseases
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
                ncit_concepts=p2a_local.get("ncit_" + prompt),
            )

        # Line 11
        if (
            # Cohorts should only be separated by ANDs (i.e., conjunctive)
            prompt == "cohort"
            and response.is_conjunctive()
            # Organs might be separated by a combination of ANDs/ORs, so only check if it has multiple answers "[[]]"
            or prompt == "organ"
            and len(response.entities) > 1
        ):
            answers = (
                # For organs, split the response as if the organs were only separated by "OR"
                response.split_as_disjunctive()
                if prompt == "organ"
                else response.entities
            )
            # Line 12
            for answer in answers:
                # Line 13
                p2a_local[prompt] = answer
                # Line 14
                logger.info(f"{question_n: > 3}. {prompt} {answer}")
                # Line 15
                subresults = process_questions(
                    gpt=gpt,
                    questions_file=questions_file,
                    question_n=question_n + 1,
                    prompt2answer=p2a_local,
                    chat_history=chat_history.copy(),
                    output_file=output_file,
                )
                results += subresults
            # Line 16
            return results
        else:
            # Line 18
            p2a_local[prompt] = None if response.is_falsy() else response.answer
            # Line 19
            logger.info(f"{question_n: > 3}. {prompt} {response.answer}")
            # Line 20
            question_n += 1

    # Return the collected results.
    results.append(p2a_local)
    return results
