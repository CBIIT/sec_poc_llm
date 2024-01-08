from langchain.prompts.few_shot import FewShotPromptTemplate
from langchain.prompts.prompt import PromptTemplate
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.prompts.example_selector import SemanticSimilarityExampleSelector
from langchain_community.vectorstores import Chroma

examples = [
    {
        "context": """Criterion:
    Subject must not have received prior radiotherapy
""",
        "answer": """
Output:
    Original Text: Subject must not have received prior radiotherapy
    Disease/Condition: none
    Procedure: Radiotherapy
    Biomarker: none
    Computable Rule: "Radiotherapy" is False"""
    },
    {
        "context": """Criterion:
    Metastatic breast cancer, biopsy proven and at least one of the following scenarios:
* Estrogen receptor (ER)+/HER2-, defined as > 5% ER+ staining
* HER2+ (regardless of ER status), including HER2-low and high expressors
""",
        "answer": """
Output:
    Original Text: Metastatic breast cancer, biopsy proven and at least one of the following scenarios:
* Estrogen receptor (ER)+/HER2-, defined as > 5% ER+ staining
* HER2+ (regardless of ER status), including HER2-low and high expressors
    Disease/Condition: Metastatic breast carcinoma
    Procedure: none
    Biomarker: HER2-, HER2+
    Computable Rule: Disease is "Metastatic breast carcinoma" AND HER2- is True OR HER2+ is True"""
    },
    {
        "context": """Criterion:
    Subject must not have any affected lymph nodes or metastatic disease
""",
        "answer": """
Output:
    Original Text: Subject must not have any affected lymph nodes or metastatic disease
    Disease/Condition: Lymph node-Metastases, Metastatic Disease
    Procedure: none
    Biomarker: none
    Computable Rule: LK MTS == False, MTS == False"""
    },
    {
        "context": """Criterion:
    Age 18 or older
""",
        "answer": """
Output:
    Original Text: Age 18 or older
    Disease/Condition: none
    Procedure: none
    Biomarker: none
    Computable Rule: none"""
    },
]


example_selector = SemanticSimilarityExampleSelector.from_examples(
    # This is the list of examples available to select from.
    examples,
    # This is the embedding class used to produce embeddings which are used to measure semantic similarity.
    HuggingFaceEmbeddings(),
    # This is the VectorStore class that is used to store the embeddings and do a similarity search over.
    Chroma,
    # This is the number of examples to produce.
    k=1,
)

example_prompt = PromptTemplate(
    input_variables=["context", "answer"], template="""{context}{answer}"""
)

prompt = FewShotPromptTemplate(
    example_selector=example_selector,
    example_prompt=example_prompt,
    prefix="""You are in the role of an abstractor who will analyze an eligibility criterion for a clinical trial and extract the relevant entities as described below.
Original Text: the original text of the criterion
Disease/Condition: If the criterion contains a disease or condition name it by its canonical name
Procedure: If the criterion contains a therapeutic procedure name it by its canonical name
Drug:  If the criterion contains a therapeutic drug name it by its canonical name
Biomarker:  If the criterion contains a biomarker name it by its canonical name
Computable Rule: Translate the criteria into a logical expression that could be interpreted programmatically""",
    suffix="""Criterion:
    {criterion}

Output:""",
    input_variables=["criterion"],
)