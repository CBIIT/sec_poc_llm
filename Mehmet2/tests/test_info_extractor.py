from pathlib import Path
from typing import Any, Union

import pytest
import yaml

import Mehmet2.info_extractor as ie
from Mehmet2.gpt_client import system_message
from Mehmet2.response_parser import Response
from Mehmet2.settings import Settings

test_data = Path(__file__).parent / "data"
questions_file = test_data / "prompts.yaml"


class Prompts:
    prompts: list[dict[str, str]]

    def __init__(self, prompts_file: Union[str, Path]) -> None:
        with open(prompts_file) as fp:
            self.prompts = yaml.safe_load(fp)

    def _get_prompt(self, name: str):
        return next(
            (prompt["question"] for prompt in self.prompts if prompt["prompt"] == name),
            "",
        )

    @property
    def cohort(self):
        return self._get_prompt("cohort")

    @property
    def organ(self):
        return self._get_prompt("organ")

    @property
    def organ_confirm(self):
        return self._get_prompt("organ_confirmation")

    @property
    def cell_type(self):
        return self._get_prompt("cell_type")

    @property
    def cell_morphology(self):
        return self._get_prompt("cell_morphology")


@pytest.fixture
def prompts():
    return Prompts(questions_file)


@pytest.fixture
def settings():
    config_file = test_data / "config.yaml"
    env_file = test_data / ".envtest"
    with open(config_file) as fp:
        config = yaml.safe_load(fp)

    settings = Settings(env_file, config, cliargs={"search": {"indexName": "trial-01"}})
    assert settings.SYSTEM_MESSAGE == "You are a helpful assistant."
    assert settings.SEARCH_CONFIG == {
        "roleInformation": "You are a helpful assistant.",
        "key": "<search_key>",
        "endpoint": "<search_endpoint>",
        "indexName": "trial-01",
    }
    return settings


def get_send_messages_mock(mock_chat: list[tuple[Any, Response]]):
    sent_prompts = []
    expected_prompts = []

    def mock_fn(self, messages):
        expected_prompt, mock_response = mock_chat.pop(0)
        expected_prompts.append(expected_prompt)
        sent_prompts.append(messages[-1]["content"])
        return mock_response

    return mock_fn, sent_prompts, expected_prompts


@pytest.fixture
def cohorts_2_organs_2(prompts):
    """A conversation with 2 cohorts (A and B) and 2 organs per cohort."""
    cohorts = (
        prompts.cohort,
        Response(
            """SOURCE-TEXT: lorem ipsum
ANSWER: [[Cohort A]] AND [[Cohort B]]"""
        ),
    )
    cohort_a_organs = (
        prompts.organ.format(cohort="Cohort A"),
        Response("""ANSWER: [[Lung]] OR [[Liver]]"""),
    )
    cohort_a_lung = [
        (
            prompts.organ_confirm.format(organ="Lung"),
            Response("""ANSWER: [[YES]]"""),
        ),
        (
            prompts.cell_type.format(organ="Lung"),
            Response("""ANSWER: [[Squamous Cell]] AND [[Non Squamous Cell]]"""),
        ),
        (
            prompts.cell_morphology.format(
                organ="Lung", cell_type="Squamous Cell AND Non Squamous Cell"
            ),
            Response("""ANSWER: [[Lung cell morph]]"""),
        ),
    ]
    cohort_a_liver = [
        (
            prompts.organ_confirm.format(organ="Liver"),
            Response("""ANSWER: [[YES]]"""),
        ),
        (
            prompts.cell_type.format(organ="Liver"),
            Response("""ANSWER: [[Liver cell type]]"""),
        ),
        (
            prompts.cell_morphology.format(organ="Liver", cell_type="Liver cell type"),
            Response("""ANSWER: [[Liver cell morph]]"""),
        ),
    ]

    cohort_b_organs = (
        prompts.organ.format(cohort="Cohort B"),
        Response("""ANSWER: [[CNS]] OR [[Brain]]"""),
    )
    cohort_b_cns = [
        (
            prompts.organ_confirm.format(organ="CNS"),
            Response("""ANSWER: [[YES]]"""),
        ),
        (
            prompts.cell_type.format(organ="CNS"),
            Response("""ANSWER: [[CNS cell type]]"""),
        ),
        (
            prompts.cell_morphology.format(organ="CNS", cell_type="CNS cell type"),
            Response("""ANSWER: [[CNS cell morph]]"""),
        ),
    ]
    cohort_b_brain = [
        (
            prompts.organ_confirm.format(organ="Brain"),
            Response("""ANSWER: [[YES]]"""),
        ),
        (
            prompts.cell_type.format(organ="Brain"),
            Response("""ANSWER: [[Brain cell type]]"""),
        ),
        (
            prompts.cell_morphology.format(organ="Brain", cell_type="Brain cell type"),
            Response("""ANSWER: [[Brain cell morph]]"""),
        ),
    ]
    return [
        cohorts,
        cohort_a_organs,
        *cohort_a_lung,
        *cohort_a_liver,
        cohort_b_organs,
        *cohort_b_cns,
        *cohort_b_brain,
    ]


def test_cohorts_2_organs_2(monkeypatch, settings, cohorts_2_organs_2):
    mock_send_messages, sent_prompts, expected_prompts = get_send_messages_mock(
        cohorts_2_organs_2
    )
    monkeypatch.setattr(ie.GPTClient, "send_messages", mock_send_messages)

    chat = [system_message(settings.SYSTEM_MESSAGE)]
    results = []
    ie.process_questions(
        gpt=ie.GPTClient(settings),
        questions_file=questions_file,
        chat_history=chat,
        results=results,
    )
    assert sent_prompts == expected_prompts
    assert results == [
        {
            "cohort": "Cohort A",
            "organ": "Lung",
            "organ_confirmation": "YES",
            "cell_type": "Squamous Cell AND Non Squamous Cell",
            "cell_morphology": "Lung cell morph",
        },
        {
            "cohort": "Cohort A",
            "organ": "Liver",
            "organ_confirmation": "YES",
            "cell_type": "Liver cell type",
            "cell_morphology": "Liver cell morph",
        },
        {
            "cohort": "Cohort B",
            "organ": "CNS",
            "organ_confirmation": "YES",
            "cell_type": "CNS cell type",
            "cell_morphology": "CNS cell morph",
        },
        {
            "cohort": "Cohort B",
            "organ": "Brain",
            "organ_confirmation": "YES",
            "cell_type": "Brain cell type",
            "cell_morphology": "Brain cell morph",
        },
    ]


@pytest.fixture
def no_cohort_2_organs(prompts):
    """A conversation with NO cohorts and two organs."""
    cohorts = (prompts.cohort, Response("ANSWER:[[NO]]"))
    organs = (
        prompts.organ.format(cohort="NO"),
        Response("ANSWER: [[Organ 1]] OR [[Organ 2]]"),
    )
    organ_1 = [
        (prompts.organ_confirm.format(organ="Organ 1"), Response("ANSWER: [[YES]]")),
        (
            prompts.cell_type.format(organ="Organ 1"),
            Response("ANSWER: [[Organ 1 cell type]]"),
        ),
        (
            prompts.cell_morphology.format(
                organ="Organ 1", cell_type="Organ 1 cell type"
            ),
            Response("ANSWER: [[Organ 1 cell morph]]"),
        ),
    ]
    organ_2 = [
        (prompts.organ_confirm.format(organ="Organ 2"), Response("ANSWER: [[YES]]")),
        (
            prompts.cell_type.format(organ="Organ 2"),
            Response("ANSWER: [[Organ 2 cell type]]"),
        ),
        (
            prompts.cell_morphology.format(
                organ="Organ 2", cell_type="Organ 2 cell type"
            ),
            Response("ANSWER: [[Organ 2 cell morph]]"),
        ),
    ]
    return [
        cohorts,
        organs,
        *organ_1,
        *organ_2,
    ]


def test_no_cohort_2_organs(monkeypatch, settings, no_cohort_2_organs):
    mock_send_messages, sent_prompts, expected_prompts = get_send_messages_mock(
        no_cohort_2_organs
    )
    monkeypatch.setattr(ie.GPTClient, "send_messages", mock_send_messages)

    chat = [system_message(settings.SYSTEM_MESSAGE)]
    results = []
    ie.process_questions(
        gpt=ie.GPTClient(settings),
        questions_file=questions_file,
        chat_history=chat,
        results=results,
    )
    assert sent_prompts == expected_prompts
    assert results == [
        {
            "cohort": "NO",
            "organ": "Organ 1",
            "organ_confirmation": "YES",
            "cell_type": "Organ 1 cell type",
            "cell_morphology": "Organ 1 cell morph",
        },
        {
            "cohort": "NO",
            "organ": "Organ 2",
            "organ_confirmation": "YES",
            "cell_type": "Organ 2 cell type",
            "cell_morphology": "Organ 2 cell morph",
        },
    ]
