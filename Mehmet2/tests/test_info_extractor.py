from pathlib import Path
from typing import Any, Union

import pytest
import yaml

import Mehmet2.info_extractor as ie
from Mehmet2.gpt_client import system_message
from Mehmet2.response_parser_v2 import Response
from Mehmet2.settings import Settings

test_data = Path(__file__).parent / "data"
questions_file = test_data / "prompts.yaml"
prompts_other_f = test_data / "prompts_other.yaml"
prompts_only_diseases_f = test_data / "prompts_only_diseases.yaml"


class Prompts:
    prompts: list[dict[str, str]]

    def __init__(self, prompts_file: Union[str, Path]) -> None:
        with open(prompts_file) as fp:
            self.prompts = yaml.safe_load(fp)

    def _get_prompt(self, name: str):
        """Get the first prompt named `name`."""
        return next(
            (prompt["question"] for prompt in self.prompts if prompt["prompt"] == name),
            "",
        )

    def _get_prompts(self, name: str):
        """Get all prompts named `name`."""
        return [
            prompt["question"] for prompt in self.prompts if prompt["prompt"] == name
        ]

    @property
    def cohort(self):
        return self._get_prompt("cohort")

    @property
    def organ_w_cohort(self):
        return self._get_prompts("organ")[0]

    @property
    def organ_wout_cohort(self):
        return self._get_prompts("organ")[1]

    @property
    def organ_confirm(self):
        return self._get_prompt("organ_confirmation")

    @property
    def cell_type(self):
        return self._get_prompt("cell_type")

    @property
    def cell_morphology(self):
        return self._get_prompt("cell_morphology")

    @property
    def disease_names_lead(self):
        return self._get_prompt("disease_names_lead")

    @property
    def biomarker_inclusion(self):
        return self._get_prompt("biomarker_inclusion")

    @property
    def biomarker_exclusion(self):
        return self._get_prompt("biomarker_exclusion")

    @property
    def prior_therapy_inclusion(self):
        return self._get_prompt("prior_therapy_inclusion")

    @property
    def prior_therapy_exclusion(self):
        return self._get_prompt("prior_therapy_exclusion")

    @property
    def diseases(self):
        return self._get_prompt("diseases")


@pytest.fixture
def prompts():
    return Prompts(questions_file)


@pytest.fixture
def prompts_other():
    return Prompts(prompts_other_f)


@pytest.fixture
def prompts_only_diseases():
    return Prompts(prompts_only_diseases_f)


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
def cohorts_2_organs_2each(prompts):
    """A conversation with 2 cohorts (A and B) and 2 organs per cohort."""
    cohorts = (
        prompts.cohort,
        Response(
            """SOURCE-TEXT: lorem ipsum
ANSWER: [[Cohort A]] AND [[Cohort B]]"""
        ),
    )
    cohort_a_organs = (
        prompts.organ_w_cohort.format(cohort="Cohort A"),
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
        prompts.organ_w_cohort.format(cohort="Cohort B"),
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


def test_cohorts_2_organs_2each(monkeypatch, settings, cohorts_2_organs_2each):
    mock_send_messages, sent_prompts, expected_prompts = get_send_messages_mock(
        cohorts_2_organs_2each
    )
    monkeypatch.setattr(ie.GPTClient, "send_messages", mock_send_messages)

    chat = [system_message(settings.SYSTEM_MESSAGE)]
    results = ie.process_questions(
        gpt=ie.GPTClient(settings),
        questions_file=questions_file,
        chat_history=chat,
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
def cohorts_1_organs_1(prompts):
    """A conversation with one cohort and one organ."""
    cohorts = (prompts.cohort, Response("ANSWER: [[Cohort A]]"))
    organs = (
        prompts.organ_w_cohort.format(cohort="Cohort A"),
        Response("ANSWER: [[Breast]]"),
    )
    organ_conf = (
        prompts.organ_confirm.format(organ="Breast"),
        Response("ANSWER: [[YES]]"),
    )
    cell_type = (
        prompts.cell_type.format(organ="Breast"),
        Response("ANSWER: [[HER-2 neu/negative]]"),
    )
    cell_morph = (
        prompts.cell_morphology.format(organ="Breast", cell_type="HER-2 neu/negative"),
        Response("ANSWER: [[Breast, HER-2 neu/negative, cell morph]]"),
    )

    return [cohorts, organs, organ_conf, cell_type, cell_morph]


def test_cohorts_1_organs_1(monkeypatch, settings, cohorts_1_organs_1):
    mock_send_messages, sent_prompts, expected_prompts = get_send_messages_mock(
        cohorts_1_organs_1
    )
    monkeypatch.setattr(ie.GPTClient, "send_messages", mock_send_messages)

    chat = [system_message(settings.SYSTEM_MESSAGE)]
    results = ie.process_questions(
        gpt=ie.GPTClient(settings),
        questions_file=questions_file,
        chat_history=chat,
    )
    assert sent_prompts == expected_prompts
    assert results == [
        {
            "cohort": "Cohort A",
            "organ": "Breast",
            "organ_confirmation": "YES",
            "cell_type": "HER-2 neu/negative",
            "cell_morphology": "Breast, HER-2 neu/negative, cell morph",
        },
    ]


@pytest.fixture
def cohorts_1_organs_0(prompts):
    """A conversation with one cohort and NO organs."""
    cohorts = (prompts.cohort, Response("ANSWER: [[Dose Escalation cohorts]]"))
    organs = (
        prompts.organ_w_cohort.format(cohort="Dose Escalation cohorts"),
        Response("ANSWER: [[NOT SPECIFIED]]"),
    )
    organ_conf = (
        prompts.organ_confirm.format(organ="None"),
        Response("ANSWER: [[YES]]"),
    )
    cell_type = (
        prompts.cell_type.format(organ="None"),
        Response("ANSWER: [[NOT SPECIFIED]]"),
    )

    return [cohorts, organs, organ_conf, cell_type]


def test_cohorts_1_organs_0(monkeypatch, settings, cohorts_1_organs_0):
    mock_send_messages, sent_prompts, expected_prompts = get_send_messages_mock(
        cohorts_1_organs_0
    )
    monkeypatch.setattr(ie.GPTClient, "send_messages", mock_send_messages)

    chat = [system_message(settings.SYSTEM_MESSAGE)]
    results = ie.process_questions(
        gpt=ie.GPTClient(settings),
        questions_file=questions_file,
        chat_history=chat,
    )
    assert sent_prompts == expected_prompts
    assert results == [
        {
            "cohort": "Dose Escalation cohorts",
            "organ": None,
            "organ_confirmation": "YES",
            "cell_type": None,
        },
    ]


@pytest.fixture
def cohorts_0_organs_2(prompts):
    """A conversation with NO cohorts and two organs."""
    cohorts = (prompts.cohort, Response("ANSWER:[[NO]]"))
    organs = (
        prompts.organ_wout_cohort,
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


def test_cohorts_0_organs_2(monkeypatch, settings, cohorts_0_organs_2):
    mock_send_messages, sent_prompts, expected_prompts = get_send_messages_mock(
        cohorts_0_organs_2
    )
    monkeypatch.setattr(ie.GPTClient, "send_messages", mock_send_messages)

    chat = [system_message(settings.SYSTEM_MESSAGE)]
    results = ie.process_questions(
        gpt=ie.GPTClient(settings),
        questions_file=questions_file,
        chat_history=chat,
    )
    assert sent_prompts == expected_prompts
    assert results == [
        {
            "cohort": None,
            "organ": "Organ 1",
            "organ_confirmation": "YES",
            "cell_type": "Organ 1 cell type",
            "cell_morphology": "Organ 1 cell morph",
        },
        {
            "cohort": None,
            "organ": "Organ 2",
            "organ_confirmation": "YES",
            "cell_type": "Organ 2 cell type",
            "cell_morphology": "Organ 2 cell morph",
        },
    ]


@pytest.fixture
def cohorts_0_organs_2_no_cell_type(prompts):
    """A conversation with NO cohorts and two organs where one organ does not have a cell_type."""
    cohorts = (prompts.cohort, Response("ANSWER:[[NO]]"))
    organs = (
        prompts.organ_wout_cohort,
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
            Response("ANSWER: [[NOT SPECIFIED]]"),
        ),
    ]
    return [
        cohorts,
        organs,
        *organ_1,
        *organ_2,
    ]


def test_cohorts_0_organs_2_no_cell_type(
    monkeypatch, settings, cohorts_0_organs_2_no_cell_type
):
    mock_send_messages, sent_prompts, expected_prompts = get_send_messages_mock(
        cohorts_0_organs_2_no_cell_type
    )
    monkeypatch.setattr(ie.GPTClient, "send_messages", mock_send_messages)

    chat = [system_message(settings.SYSTEM_MESSAGE)]
    results = ie.process_questions(
        gpt=ie.GPTClient(settings),
        questions_file=questions_file,
        chat_history=chat,
    )
    assert sent_prompts == expected_prompts
    assert results == [
        {
            "cohort": None,
            "organ": "Organ 1",
            "organ_confirmation": "YES",
            "cell_type": "Organ 1 cell type",
            "cell_morphology": "Organ 1 cell morph",
        },
        {
            "cohort": None,
            "organ": "Organ 2",
            "organ_confirmation": "YES",
            "cell_type": None,
        },
    ]


@pytest.fixture
def cohorts_0_organs_1(prompts):
    """A conversation with NO cohorts and one organ."""
    cohorts = (prompts.cohort, Response("ANSWER:[[NO]]"))
    organs = (
        prompts.organ_wout_cohort,
        Response("ANSWER: [[Breast]]"),
    )
    organ_conf = (
        prompts.organ_confirm.format(organ="Breast"),
        Response("ANSWER: [[YES]]"),
    )
    cell_type = (
        prompts.cell_type.format(organ="Breast"),
        Response("ANSWER: [[Breast cell type]]"),
    )
    cell_morph = (
        prompts.cell_morphology.format(organ="Breast", cell_type="Breast cell type"),
        Response("ANSWER: [[Breast cell morph]]"),
    )

    return [cohorts, organs, organ_conf, cell_type, cell_morph]


def test_cohorts_0_organs_1(monkeypatch, settings, cohorts_0_organs_1):
    mock_send_messages, sent_prompts, expected_prompts = get_send_messages_mock(
        cohorts_0_organs_1
    )
    monkeypatch.setattr(ie.GPTClient, "send_messages", mock_send_messages)

    chat = [system_message(settings.SYSTEM_MESSAGE)]
    results = ie.process_questions(
        gpt=ie.GPTClient(settings),
        questions_file=questions_file,
        chat_history=chat,
    )
    assert sent_prompts == expected_prompts
    assert results == [
        {
            "cohort": None,
            "organ": "Breast",
            "organ_confirmation": "YES",
            "cell_type": "Breast cell type",
            "cell_morphology": "Breast cell morph",
        },
    ]


@pytest.fixture
def cohorts_0_organs_0(prompts):
    """A conversation with NO cohorts and NO organs."""
    cohorts = (prompts.cohort, Response("ANSWER:[[NO]]"))
    organs = (
        prompts.organ_wout_cohort,
        Response("ANSWER: [[NOT SPECIFIED]]"),
    )
    organ_conf = (
        prompts.organ_confirm.format(organ="None"),
        Response("ANSWER: [[YES]]"),
    )
    cell_type = (
        prompts.cell_type.format(organ="None"),
        Response("ANSWER: [[NOT SPECIFIED]]"),
    )
    cell_morph = (
        prompts.cell_morphology.format(organ="None", cell_type="None"),
        Response("ANSWER: [[NOT SPECIFIED]]"),
    )

    return [cohorts, organs, organ_conf, cell_type, cell_morph]


def test_cohorts_0_organs_0(monkeypatch, settings, cohorts_0_organs_0):
    mock_send_messages, sent_prompts, expected_prompts = get_send_messages_mock(
        cohorts_0_organs_0
    )
    monkeypatch.setattr(ie.GPTClient, "send_messages", mock_send_messages)

    chat = [system_message(settings.SYSTEM_MESSAGE)]
    results = ie.process_questions(
        gpt=ie.GPTClient(settings),
        questions_file=questions_file,
        chat_history=chat,
    )
    assert sent_prompts == expected_prompts
    assert results == [
        {
            "cohort": None,
            "organ": None,
            "organ_confirmation": "YES",
            "cell_type": None,
        },
    ]


@pytest.fixture
def cohorts_disjunctive(prompts):
    """A conversation with two cohorts that are disjunctive (OR)."""
    cohorts = (
        prompts.cohort,
        Response("ANSWER: [[Dose Escalation cohorts]] OR [[Dose Expansion cohorts]]"),
    )
    organs = (
        prompts.organ_w_cohort.format(
            cohort="Dose Escalation cohorts OR Dose Expansion cohorts"
        ),
        Response("ANSWER: [[Organ]]"),
    )
    organ_conf = (
        prompts.organ_confirm.format(organ="Organ"),
        Response("ANSWER: [[Organ]] OR [[Organ X]]"),
    )
    cell_type = (
        prompts.cell_type.format(organ="Organ"),
        Response("ANSWER: [[Organ cell type]]"),
    )
    cell_morph = (
        prompts.cell_morphology.format(organ="Organ", cell_type="Organ cell type"),
        Response("ANSWER: [[Organ cell morph]]"),
    )

    return [cohorts, organs, organ_conf, cell_type, cell_morph]


def test_cohorts_disjunctive(monkeypatch, settings, cohorts_disjunctive):
    mock_send_messages, sent_prompts, expected_prompts = get_send_messages_mock(
        cohorts_disjunctive
    )
    monkeypatch.setattr(ie.GPTClient, "send_messages", mock_send_messages)

    chat = [system_message(settings.SYSTEM_MESSAGE)]
    results = ie.process_questions(
        gpt=ie.GPTClient(settings),
        questions_file=questions_file,
        chat_history=chat,
    )
    assert sent_prompts == expected_prompts
    assert results == [
        {
            "cohort": "Dose Escalation cohorts OR Dose Expansion cohorts",
            "organ": "Organ",
            "organ_confirmation": "Organ OR Organ X",
            "cell_type": "Organ cell type",
            "cell_morphology": "Organ cell morph",
        },
    ]


@pytest.fixture
def organs_conjunctive(prompts):
    """A conversation with two organs that are conjunctive (AND)."""
    cohorts = (
        prompts.cohort,
        Response("ANSWER: [[NO]]"),
    )
    organs = (
        prompts.organ_wout_cohort,
        Response("ANSWER: [[Organ A]] AND [[Organ B]]"),
    )
    organ_conf = (
        prompts.organ_confirm.format(organ="Organ A AND Organ B"),
        Response("ANSWER: [[YES]]"),
    )
    cell_type = (
        prompts.cell_type.format(organ="Organ A AND Organ B"),
        Response("ANSWER: [[Cell type A]] AND [[Cell type B]]"),
    )
    cell_morph = (
        prompts.cell_morphology.format(
            organ="Organ A AND Organ B", cell_type="Cell type A AND Cell type B"
        ),
        Response("ANSWER: [[Organ A cell morph]] AND [[Organ B cell morph]]"),
    )

    return [cohorts, organs, organ_conf, cell_type, cell_morph]


def test_organs_conjunctive(monkeypatch, settings, organs_conjunctive):
    mock_send_messages, sent_prompts, expected_prompts = get_send_messages_mock(
        organs_conjunctive
    )
    monkeypatch.setattr(ie.GPTClient, "send_messages", mock_send_messages)

    chat = [system_message(settings.SYSTEM_MESSAGE)]
    results = ie.process_questions(
        gpt=ie.GPTClient(settings),
        questions_file=questions_file,
        chat_history=chat,
    )
    assert sent_prompts == expected_prompts
    assert results == [
        {
            "cohort": None,
            "organ": "Organ A AND Organ B",
            "organ_confirmation": "YES",
            "cell_type": "Cell type A AND Cell type B",
            "cell_morphology": "Organ A cell morph AND Organ B cell morph",
        },
    ]


@pytest.fixture
def diseases_disjunctive(prompts_other):
    disease_names_lead = (
        prompts_other.disease_names_lead,
        Response("""SOURCE-TEXT: [[lorem ipsum]]
PRIMARY-ORGANS:[[Breast]] OR [[Rectum]]
ANSWER: [[Ductal Carcinoma In Situ]] OR [[Locally-advanced Rectal Cancer]]
"""),
    )
    biomarkers_inc_disease_a = (
        prompts_other.biomarker_inclusion,
        Response("""SOURCE-TEXT:[[lorem ipsum]]
ANSWER:[[Estrogen Receptor Positive]]
"""),
    )
    biomarkers_exc_disease_a = (
        prompts_other.biomarker_exclusion,
        Response("""SOURCE-TEXT:[[lorem ipsum]]
ANSWER:[[NOT SPECIFIED]]
"""),
    )
    biomarkers_inc_disease_b = (
        prompts_other.biomarker_inclusion,
        Response("""SOURCE-TEXT:[[lorem ipsum]]
ANSWER:[[Biomarker for Locally-advanced Rectal Cancer]]
"""),
    )
    biomarkers_exc_disease_b = (
        prompts_other.biomarker_exclusion,
        Response("""SOURCE-TEXT:[[lorem ipsum]]
ANSWER:[[NOT SPECIFIED]]
"""),
    )
    return [
        disease_names_lead,
        biomarkers_inc_disease_a,
        biomarkers_exc_disease_a,
        biomarkers_inc_disease_b,
        biomarkers_exc_disease_b,
    ]


def test_diseases_disjunctive(monkeypatch, settings, diseases_disjunctive):
    mock_send_messages, sent_prompts, expected_prompts = get_send_messages_mock(
        diseases_disjunctive
    )
    monkeypatch.setattr(ie.GPTClient, "send_messages", mock_send_messages)

    chat = [system_message(settings.SYSTEM_MESSAGE)]
    results = ie.process_questions(
        gpt=ie.GPTClient(settings),
        questions_file=prompts_other_f,
        chat_history=chat,
        output_file="test.out.csv",
    )
    assert sent_prompts == expected_prompts
    assert results == [
        {
            "ncit_disease_names_lead": ("C40374", "Microinvasive Breast Carcinoma"),
            "disease_names_lead": "Ductal Carcinoma In Situ",
            "biomarker_exclusion": None,
            "biomarker_inclusion": "Estrogen Receptor Positive",
        },
        {
            "ncit_disease_names_lead": ("C170778", "Locally Advanced Rectal Carcinoma"),
            "biomarker_exclusion": None,
            "biomarker_inclusion": "Biomarker for Locally-advanced Rectal Cancer",
            "disease_names_lead": "Locally-advanced Rectal Cancer",
        },
    ]


@pytest.fixture
def diseases_only(prompts_only_diseases):
    disease_names_lead = (
        prompts_only_diseases.disease_names_lead,
        Response("""SOURCE-TEXT:[[lorem ipsum]]
ANSWER:[[Stage IIA, IIB, IIIA, or IIIB Non-Squamous or Squamous NSCLC]]"""),
    )
    diseases = (
        prompts_only_diseases.diseases.format(
            disease_names_lead="Stage IIA, IIB, IIIA, or IIIB Non-Squamous or Squamous NSCLC"
        ),
        Response("""SOURCE-TEXT:[[lorem ipsum]]
ANSWER:[[Stage IIA Non-Squamous NSCLC OR Stage IIB Non-Squamous NSCLC OR Stage IIIA Non-Squamous NSCLC OR Stage IIIB Non-Squamous NSCLC OR Stage IIA Squamous NSCLC OR Stage IIB Squamous NSCLC OR Stage IIIA Squamous NSCLC OR Stage IIIB Squamous NSCLC]]
"""),
    )
    return [disease_names_lead, diseases]


def test_diseases_only(monkeypatch, settings, diseases_only):
    mock_send_messages, sent_prompts, expected_prompts = get_send_messages_mock(
        diseases_only
    )
    monkeypatch.setattr(ie.GPTClient, "send_messages", mock_send_messages)

    chat = [system_message(settings.SYSTEM_MESSAGE)]
    results = ie.process_questions(
        gpt=ie.GPTClient(settings),
        questions_file=prompts_only_diseases_f,
        chat_history=chat,
        output_file="test.out.csv",
    )
    assert sent_prompts == expected_prompts
    assert results == [
        {
            "disease_names_lead": "Stage IIA, IIB, IIIA, or IIIB Non-Squamous or Squamous NSCLC",
            "diseases": "Stage IIA Non-Squamous NSCLC OR Stage IIB Non-Squamous NSCLC OR Stage IIIA Non-Squamous NSCLC OR Stage IIIB Non-Squamous NSCLC OR Stage IIA Squamous NSCLC OR Stage IIB Squamous NSCLC OR Stage IIIA Squamous NSCLC OR Stage IIIB Squamous NSCLC",
            "ncit_disease_names_lead": (
                "C43588",
                "Colorectal Squamous Cell Carcinoma",
            ),
            "ncit_diseases": ("C134188", "Stage IIB Colorectal Cancer AJCC v8"),
        },
    ]
