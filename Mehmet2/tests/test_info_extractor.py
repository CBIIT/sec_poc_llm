from pathlib import Path
from unittest.mock import MagicMock

import pytest
import yaml

import Mehmet2.info_extractor as ie
from Mehmet2.gpt_client import system_message
from Mehmet2.response_parser import Response
from Mehmet2.settings import Settings

test_data = Path(__file__).parent / "data"
questions_file = test_data / "prompts.yaml"


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


responses_2_cohorts_3_organs = [
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


def test_2_cohorts_3_organs(monkeypatch, settings):
    mock_send_messages = MagicMock(side_effect=responses_2_cohorts_3_organs)
    monkeypatch.setattr(ie.GPTClient, "send_messages", mock_send_messages)

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


responses_not_specified = [
    # No cohort
    Response("""ANSWER:[[NO]]"""),
    # organ
    Response("""ANSWER: [[NOT SPECIFIED]]"""),
    # organ_confirmation
    Response("""ANSWER: [[YES]]"""),
    # cell_type
    Response("""ANSWER: [[NOT SPECIFIED]]"""),
    # cell_morphology
    Response("""ANSWER: [[NOT SPECIFIED]]"""),
]
NO = "NO"
NOT_SPECIFIED = "NOT SPECIFIED"
prompts_not_specified = [
    """Are there multiple cohorts specified in the eligibility criteria for the clinical cancer trial protocol in the attached file? If so, please specify them; e.g., 
ANSWER: [[Cohort 1]] AND [[Cohort 2]] AND [[Cohort 3]]
If not, say ANSWER:[[NO]]
""",
    #
    # Organ
    f"""Based on the eligibility criteria for {NO} in the attached file, what are the primary organs that the cancer originated from? Please provide the source text portion that your answer is based on. If it is a metastatic cancer and the primary organ was not specified, say ANSWER: [[NOT SPECIFIED]].
First, please specify the source text that your answer is based on. Then, specify only the name of each primary organ in your ANSWER within double-square brackets without further details.
""",
    #
    # Organ confirmation
    f"""Please confirm that {NOT_SPECIFIED} is the primary organ that cancer originated from. If affirmative, please say,
ANSWER: [[YES]]. Otherwise, provide the name of the organs in the ANSWER.
""",
    #
    # Cell Type
    f"""What cell types of {NOT_SPECIFIED} cancer are required in the inclusion criteria of the attached file. If multiple cell types are mentioned, please specify all of them. If no cell type is mentioned, please say, ANSWER: [[NOT SPECIFIED]].
""",
    #
    # Cell morph
    f"""Is there any mention of required cell morphology specifications in the inclusion criteria for {NOT_SPECIFIED} {NOT_SPECIFIED} in the attached protocol? If not, please indicate with ANSWER: [[NO]]. If there are, please provide the SOURCE-TEXT before answering.
""",
]


def test_not_specified(monkeypatch, settings):
    sent_messages = []

    def mock_send_messages(self, messages):
        sent_messages.append(messages[-1]["content"])
        return responses_not_specified.pop(0)

    monkeypatch.setattr(ie.GPTClient, "send_messages", mock_send_messages)

    chat = [system_message(settings.SYSTEM_MESSAGE)]
    results = []
    ie.process_questions(
        gpt=ie.GPTClient(settings),
        questions_file=questions_file,
        chat_history=chat,
        results=results,
    )
    assert sent_messages == prompts_not_specified
    assert results == [
        {
            "cohort": "NO",
            "organ": "NOT SPECIFIED",
            "organ_confirmation": "YES",
            "cell_type": "NOT SPECIFIED",
            "cell_morphology": "NOT SPECIFIED",
        },
    ]
