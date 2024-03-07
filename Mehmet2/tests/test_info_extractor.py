from pathlib import Path
from unittest.mock import MagicMock
from Mehmet2.gpt_client import system_message

import Mehmet2.info_extractor as ie
from Mehmet2.response_parser import Response

test_data_path = Path(__file__).parent / "data"

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
    Response("""ANSWER: [[Cell Morph]]"""),
    #
    # For Cohort B, Brain confirmation
    Response("""ANSWER: [[YES]]"""),
    # For Cohort B, Cell Type
    Response("""ANSWER: [[Type 1]]"""),
    # For Cohort B, Cell Morphology
    Response("""ANSWER: [[Cell Morph]]"""),
]


def test_process_questions(monkeypatch):
    mock_send_messages = MagicMock(side_effect=responses_chat1)
    monkeypatch.setattr(ie.GPTClient, "send_messages", mock_send_messages)

    q = 0
    p2a = {}
    chat = [system_message()]
    accumulated_p2a = []
    ie.process_questions(
        ie.GPTClient(search_params={"indexName": "test"}),
        test_data_path / "prompts.yaml",
        q,
        p2a,
        chat,
        accumulated_p2a,
    )
    assert accumulated_p2a == [
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
            "cell_morphology": "Cell Morph",
        },
        {
            "cohort": "Cohort B",
            "organ": "Brain",
            "organ_confirmation": "YES",
            "cell_type": "Type 1",
            "cell_morphology": "Cell Morph",
        },
    ]
