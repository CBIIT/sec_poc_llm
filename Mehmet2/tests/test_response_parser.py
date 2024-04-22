from collections import namedtuple

import pytest

from Mehmet2.response_parser_v2 import Response

ResponseParams = namedtuple(
    "ResponseParams",
    (
        "text",
        "answer",
        "conditions",
        "entities",
        "source_text",
        "disjunctive_entities",
    ),
)


responses = [
    # Single source and answer
    ResponseParams(
        """SOURCE-TEXT: lorem ipsum
ANSWER: [[A]]""",
        answer="A",
        conditions=[],
        entities=["A"],
        source_text="lorem ipsum",
        disjunctive_entities=["A"],
    ),
    # Single source with multiple answers. Answers should be assumed conjunctive (AND).
    ResponseParams(
        """SOURCE-TEXT: lorem ipsum
ANSWER: [[A]]
ANSWER: [[B]]""",
        answer="A AND B",
        conditions=["AND"],
        entities=["A", "B"],
        source_text="lorem ipsum",
        disjunctive_entities=["A AND B"],
    ),
    # Multi source and Answer. Sources should be concatenated. Answers are assumed conjunctive.
    ResponseParams(
        """SOURCE-TEXT: lorem ipsum
ANSWER: [[A]]
SOURCE-TEXT: lorem ipsum dolor
ANSWER: [[B]]""",
        answer="A AND B",
        conditions=["AND"],
        entities=["A", "B"],
        source_text="lorem ipsum\n\nlorem ipsum dolor",
        disjunctive_entities=["A AND B"],
    ),
    # Single Answer
    ResponseParams(
        """ANSWER: [[A]]""",
        answer="A",
        conditions=[],
        entities=["A"],
        source_text="",
        disjunctive_entities=["A"],
    ),
    # Nonconforming freetext answer
    ResponseParams(
        """The source text does not mention the organ location for the primary cancer.
Therefore, the answer is [[NOT SPECIFIED]]""",
        answer="",
        conditions=[],
        entities=[],
        source_text="",
        disjunctive_entities=[],
    ),
    # Source-text nonconforming
    ResponseParams(
        """The source text does not mention the organ location for the primary cancer.
Therefore the answer is,
ANSWER: [[NOT SPECIFIED]]""",
        answer="NOT SPECIFIED",
        conditions=[],
        entities=["NOT SPECIFIED"],
        source_text="",
        disjunctive_entities=["NOT SPECIFIED"],
    ),
    # Answer nonconforming
    ResponseParams(
        """SOURCE-TEXT: The source text does not mention the organ location for the primary cancer.
Therefore the answer is [[NOT SPECIFIED]]""",
        answer="",
        conditions=[],
        entities=[],
        source_text="The source text does not mention the organ location for the primary cancer.\nTherefore the answer is [[NOT SPECIFIED]]",
        disjunctive_entities=[],
    ),
    # Possibly malformed response
    ResponseParams(
        """SOURCE-TEXTThe source text does not mention the organ location for the primary cancer.
ANSWER:[[NOT SPECIFIED]] .""",
        answer="NOT SPECIFIED",
        conditions=[],
        entities=["NOT SPECIFIED"],
        source_text="",
        disjunctive_entities=["NOT SPECIFIED"],
    ),
    # Unconventional response
    ResponseParams(
        """SOURCE-TEXT: The source
- text does not mention
- the organ location for the
- primary cancer.  


  ANSWER [[A]] and [[B]]. """,
        answer="A AND B",
        conditions=["and"],
        entities=["A", "B"],
        source_text="The source\n- text does not mention\n- the organ location for the\n- primary cancer.  \n\n",
        disjunctive_entities=["A AND B"],
    ),
    # Conjunctive
    ResponseParams(
        """SOURCE-TEXT: lorem ipsum
ANSWER: [[A]] and [[B]]""",
        answer="A AND B",
        conditions=["and"],
        entities=["A", "B"],
        source_text="lorem ipsum",
        disjunctive_entities=["A AND B"],
    ),
    # Disjunctive
    ResponseParams(
        """SOURCE-TEXT: lorem ipsum
ANSWER: [[A]] or [[B]]""",
        answer="A OR B",
        conditions=["or"],
        entities=["A", "B"],
        source_text="lorem ipsum",
        disjunctive_entities=["A", "B"],
    ),
    # Disjunctive with parentheses
    ResponseParams(
        """SOURCE-TEXT: lorem ipsum
ANSWER: [[A]] or ([[B]] and [[C]])""",
        answer="A OR ( B AND C )",
        conditions=["or (", "and", ")"],
        entities=["A", "B", "C"],
        source_text="lorem ipsum",
        disjunctive_entities=["A", "B AND C"],
    ),
    # Mixed bag of conditions
    ResponseParams(
        """SOURCE-TEXT: lorem ipsum
ANSWER: [[A]] or [[B]] and [[C]]""",
        answer="A OR B AND C",
        conditions=[
            "or",
            "and",
        ],
        entities=["A", "B", "C"],
        source_text="lorem ipsum",
        disjunctive_entities=["A", "B AND C"],
    ),
    # Mixed bag of conditions
    ResponseParams(
        """SOURCE-TEXT: lorem ipsum
dolor sit
amet consectetur
adipisicing elit
ANSWER: ([[A]]) or ([[B]] and [[C]]) and [[D]] or [[E]]""",
        answer="(A ) OR ( B AND C ) AND D OR E",
        conditions=["(", ") or (", "and", ") and", "or"],
        entities=["A", "B", "C", "D", "E"],
        source_text="lorem ipsum\ndolor sit\namet consectetur\nadipisicing elit",
        disjunctive_entities=["A", "B AND C ) AND D", "E"],
    ),
    # Case of organs with parentheses
    ResponseParams(
        """SOURCE-TEXT: What are the organs?
ANSWER: [[Lung]] or ([[Breast]] and [[Ovary]])""",
        answer="Lung OR ( Breast AND Ovary )",
        conditions=["or (", "and", ")"],
        entities=["Lung", "Breast", "Ovary"],
        source_text="What are the organs?",
        disjunctive_entities=["Lung", "Breast AND Ovary"],
    ),
    # Case of organs without parentheses
    ResponseParams(
        """SOURCE-TEXT: What are the organs?
ANSWER: [[Lung]] or [[Breast]] and [[Ovary]]""",
        answer="Lung OR Breast AND Ovary",
        conditions=["or", "and"],
        entities=["Lung", "Breast", "Ovary"],
        source_text="What are the organs?",
        disjunctive_entities=["Lung", "Breast AND Ovary"],
    ),
]


@pytest.mark.parametrize(
    "text,answer,conditions,entities,source_text,disjunctive_entities",
    responses,
)
def test_responses(
    text,
    answer,
    conditions,
    entities,
    source_text,
    disjunctive_entities,
):
    r = Response(text)
    assert r.answer == answer
    assert r.conditions == conditions
    assert r.entities == entities
    assert r.source_text == source_text
    assert r.split_as_disjunctive() == disjunctive_entities


is_conjunctive_texts = [
    (
        """SOURCE-TEXT: lorem ipsum
ANSWER: [[A]] AND [[B]]
""",
        True,
    ),
    (
        """SOURCE-TEXT: lorem ipsum
ANSWER: [[A]] AND [[B]] OR [[C]]
""",
        False,
    ),
    (
        """SOURCE-TEXT: lorem ipsum
ANSWER: ([[A]] AND [[B]]) OR ([[B]] AND [[C]])
""",
        False,
    ),
    (
        """SOURCE-TEXT: lorem ipsum
ANSWER: ([[A]] OR [[B]]) AND ([[B]] OR [[C]])
""",
        True,
    ),
    (
        """SOURCE-TEXT: lorem ipsum
ANSWER: [[A]] AND [[B]] AND ([[B]] OR [[C]])
""",
        True,
    ),
    (
        """SOURCE-TEXT: lorem ipsum
ANSWER: [[A]] AND [[B]] AND ([[B]] OR ([[C]] AND [[D]]))
""",
        True,
    ),
    (
        """SOURCE-TEXT: lorem ipsum
ANSWER: [[A]] AND [[B]] AND ([[B]] OR [[C]] OR [[D]])
""",
        True,
    ),
    (
        """SOURCE-TEXT: lorem ipsum
ANSWER: ([[A]] AND [[B]]) AND [[C]]
""",
        True,
    ),
]


@pytest.mark.parametrize(
    "text,expected",
    is_conjunctive_texts,
)
def test_is_conjunctive(
    text,
    expected,
):
    r = Response(text)
    assert r.is_conjunctive() == expected


is_disjunctive_texts = [
    (
        """SOURCE-TEXT: lorem ipsum
ANSWER: [[A]] AND [[B]]
""",
        False,
    ),
    (
        """SOURCE-TEXT: lorem ipsum
ANSWER: [[A]] AND [[B]] OR [[C]]
""",
        False,
    ),
    (
        """SOURCE-TEXT: lorem ipsum
ANSWER: ([[A]] AND [[B]]) OR ([[B]] AND [[C]])
""",
        True,
    ),
    (
        """SOURCE-TEXT: lorem ipsum
ANSWER: ([[A]] OR [[B]]) AND ([[B]] OR [[C]])
""",
        False,
    ),
    (
        """SOURCE-TEXT: lorem ipsum
ANSWER: [[A]] AND [[B]] OR ([[B]] OR [[C]])
""",
        False,
    ),
    (
        """SOURCE-TEXT: lorem ipsum
ANSWER: ([[A]] AND [[B]]) OR [[B]] OR [[C]]
""",
        True,
    ),
    (
        """SOURCE-TEXT: lorem ipsum
ANSWER: ([[A]]) or ([[B]] and [[C]]) and [[D]] or [[E]]""",
        False,
    ),
]


@pytest.mark.parametrize(
    "text,expected",
    is_disjunctive_texts,
)
def test_is_disjunctive(
    text,
    expected,
):
    r = Response(text)
    assert r.is_disjunctive() == expected


is_falsy_texts = [
    ("", True),
    (
        """SOURCE-TEXT: lorem ipsum
ANSWER: [[NOT SPECIFIED]]
""",
        True,
    ),
    (
        """SOURCE-TEXT: lorem ipsum
ANSWER: [[None]]
""",
        True,
    ),
    (
        """SOURCE-TEXT: lorem ipsum
ANSWER:[[NO]].
""",
        True,
    ),
    ("""ANSWER: [[Yes]]""", False),
    (
        """SOURCE-TEXT: lorem ipsum
ANSWER: [[Cohort A]]
""",
        False,
    ),
    # These disjunctive/conjunctive scenarios are not considered falsy,
    # though they will likely never occur in practice.
    (
        """SOURCE-TEXT: lorem ipsum
ANSWER: [[NOT SPECIFIED]] OR [[None]]
""",
        False,
    ),
]


@pytest.mark.parametrize("text,expected", is_falsy_texts)
def test_is_falsy(text, expected):
    r = Response(text)
    assert r.is_falsy() == expected
