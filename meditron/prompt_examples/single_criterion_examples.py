from langchain.prompts.few_shot import FewShotPromptTemplate
from langchain.prompts.prompt import PromptTemplate
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.prompts.example_selector import SemanticSimilarityExampleSelector
from langchain_community.vectorstores import Chroma

examples = [
    {
        "context": """
Below is an example of clinical trial eligibility inclusion/exclusion criteria. Your task is to identify 3 categories of data within it. The 3 categories are: 1) Disease: a disorder affecting humans, 2) Biomarker: genes, proteins, or other substances that can be tested for to reveal important details about a patient’s cancer, and 3) Prior Therapy: medications, surgeries, or procedures that a patient may be treated with. For each of the identified categories, state whether it is an inclusion or exclusion. Additionally, please summarize the criterion.
Criteria:
    Inclusion Criteria
    •	Subject must have invasive ductal breast cancer with HER2 over-expression in the tumor tissue.
""",
        "answer": """
Source Criterion: Subject must have invasive ductal breast cancer with HER2 over-expression in the tumor tissue.
Inclusion/Exclusion: Inclusion
Diseases: Invasive Ductal Breast Carcinoma
Biomarkers: HER2 over-expression
Prior Therapies: none
Summary: Disease is Invasive Ductal Breast Carcinoma, HER2 is True
"""
    },
    {
        "context": """
Below is an example of clinical trial eligibility inclusion/exclusion criteria. Your task is to identify 3 categories of data within it. The 3 categories are: 1) Disease: a disorder affecting humans, 2) Biomarker: genes, proteins, or other substances that can be tested for to reveal important details about a patient’s cancer, and 3) Prior Therapy: medications, surgeries, or procedures that a patient may be treated with. For each of the identified categories, state whether it is an inclusion or exclusion. Additionally, please summarize the criterion.
Criteria:
    Exclusion Criteria
    •	Subject must not have received prior radiotherapy
""",
        "answer": """
Source Criterion: Subject must not have received prior radiotherapy
Inclusion/Exclusion: Exclusion
Diseases: none
Biomarkers: none
Prior Therapies: Radiotherapy
Summary: Radiotherapy is False
"""
    },
    {
        "context": """
Below is an example of clinical trial eligibility inclusion/exclusion criteria. Your task is to identify 3 categories of data within it. The 3 categories are: 1) Disease: a disorder affecting humans, 2) Biomarker: genes, proteins, or other substances that can be tested for to reveal important details about a patient’s cancer, and 3) Prior Therapy: medications, surgeries, or procedures that a patient may be treated with. For each of the identified categories, state whether it is an inclusion or exclusion. Additionally, please summarize the criterion.
Criteria:
    Exclusion Criteria
    •	Subject must not have any affected lymph nodes or metastatic disease
""",
        "answer": """
Source Criterion: Subject must not have any affected lymph nodes or metastatic disease
Inclusion/Exclusion: Exclusion
Diseases: Lymph node-Metastases, Metastatic Disease
Biomarkers: none
Prior Therapies: none
Summary: LK MTS is False, MTS is False
"""
    },
    {
        "context": """
Below is an example of clinical trial eligibility inclusion/exclusion criteria. Your task is to identify 3 categories of data within it. The 3 categories are: 1) Disease: a disorder affecting humans, 2) Biomarker: genes, proteins, or other substances that can be tested for to reveal important details about a patient’s cancer, and 3) Prior Therapy: medications, surgeries, or procedures that a patient may be treated with. For each of the identified categories, state whether it is an inclusion or exclusion. Additionally, please summarize the criterion.
Criteria:
    Inclusion Criteria
    •	Age 18 or older
""",
        "answer": """
Source Criterion: Age 18 or older
No diseases, biomarkers, or prior therapies found.
"""
    },
    {
        "context": """
Below is an example of clinical trial eligibility inclusion/exclusion criteria. Your task is to identify 3 categories of data within it. The 3 categories are: 1) Disease: a disorder affecting humans, 2) Biomarker: genes, proteins, or other substances that can be tested for to reveal important details about a patient’s cancer, and 3) Prior Therapy: medications, surgeries, or procedures that a patient may be treated with. For each of the identified categories, state whether it is an inclusion or exclusion. Additionally, please summarize the criterion.
Criteria:
    Exclusion Criteria
    •	Pregnancy
""",
        "answer": """
Source Criterion: Pregnancy
No diseases, biomarkers, or prior therapies found.
"""
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
    k=3,
)

example_prompt = PromptTemplate(
    input_variables=["context", "answer"], template="Task:{context}{answer}"
)

prompt = FewShotPromptTemplate(
    example_selector=example_selector,
    example_prompt=example_prompt,
    suffix="""Task:
Below is an example of clinical trial eligibility inclusion/exclusion criteria. Your task is to identify 3 categories of data within it. The 3 categories are: 1) Disease: a disorder affecting humans, 2) Biomarker: genes, proteins, or other substances that can be tested for to reveal important details about a patient’s cancer, and 3) Prior Therapy: medications, surgeries, or procedures that a patient may be treated with. For each of the identified categories, state whether it is an inclusion or exclusion. Additionally, please summarize the criterion.
Criteria:
    {criteria}
""",
    input_variables=["criteria"],
)