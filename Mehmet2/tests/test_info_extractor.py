from pathlib import Path
from unittest.mock import MagicMock

import yaml

import Mehmet2.info_extractor as ie
from Mehmet2.gpt_client import system_message
from Mehmet2.response_parser import Response
from Mehmet2.settings import Settings

test_data = Path(__file__).parent / "data"

responses_chat1 = [
    # Cohort
    Response(
        """SOURCE-TEXT: lorem ipsum
ANSWER: [[Cohort A]] AND [[Cohort B]]"""
    ),
    #
    # For Cohort A, Organ
    Response("""ANSWER: [[Lung]]"""),
    # For Cohort A, Organ confirmation
    Response("""ANSWER: [[YES]]"""),
    # For Cohort A, Cell Type
    Response("""ANSWER: [[Squamous Cell]] AND [[Non Squamous Cell]]"""),
    # For Cohort A, Cell Morphology
    Response("""ANSWER: [[NO]]"""),
    #
    # For Cohort B, Organ
    Response("""ANSWER: [[CNS]] OR [[Brain]]"""),
    #
    # For Cohort B, CNS confirmation
    Response("""ANSWER: [[YES]]"""),
    # For Cohort B, Cell Type
    Response("""ANSWER: [[Type 1]]"""),
    # For Cohort B, Cell Morphology
    Response("""ANSWER: [[Cell Morph 1]]"""),
    #
    # For Cohort B, Brain confirmation
    Response("""ANSWER: [[YES]]"""),
    # For Cohort B, Cell Type
    Response("""ANSWER: [[Type 2]]"""),
    # For Cohort B, Cell Morphology
    Response("""ANSWER: [[Cell Morph 2]]"""),
]


def test_process_questions(monkeypatch):
    config_file = test_data / "config.yaml"
    env_file = test_data / ".envtest"
    questions_file = test_data / "prompts.yaml"

    mock_send_messages = MagicMock(side_effect=responses_chat1)
    monkeypatch.setattr(ie.GPTClient, "send_messages", mock_send_messages)

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

    chat = [system_message(settings.SYSTEM_MESSAGE)]
    results = []
    ie.process_questions(
        gpt=ie.GPTClient(settings),
        questions_file=questions_file,
        chat_history=chat,
        results=results,
    )
    assert results == [
        {
            "cohort": "Cohort A",
            "organ": "Lung",
            "organ_confirmation": "YES",
            "cell_type": "Squamous Cell AND Non Squamous Cell",
            "cell_morphology": "NO",
        },
        {
            "cohort": "Cohort B",
            "organ": "CNS",
            "organ_confirmation": "YES",
            "cell_type": "Type 1",
            "cell_morphology": "Cell Morph 1",
        },
        {
            "cohort": "Cohort B",
            "organ": "Brain",
            "organ_confirmation": "YES",
            "cell_type": "Type 2",
            "cell_morphology": "Cell Morph 2",
        },
    ]
