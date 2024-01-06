from langchain.prompts.few_shot import FewShotPromptTemplate
from langchain.prompts.prompt import PromptTemplate
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.prompts.example_selector import SemanticSimilarityExampleSelector
from langchain_community.vectorstores import Chroma


examples = [
    {
        "context": """
Below is an example of ...
""",
        "answer": """

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
    k=1,
)

example_prompt = PromptTemplate(
    input_variables=["context", "answer"], template="Task:{context}{answer}"
)

prompt = FewShotPromptTemplate(
    example_selector=example_selector,
    example_prompt=example_prompt,
    suffix="""Task:
Below is an example of clinical trial eligibility inclusion/exclusion criteria. Your task is to identify 3 categories of data within it. The 3 categories are: 1) Disease: a disorder affecting humans, 2) Biomarker: genes, proteins, or other substances that can be tested for to reveal important details about a patient’s cancer, and 3) Prior Therapy: medications, surgeries, or procedures that a patient may be treated with. For each of the identified categories, state whether it is an inclusion or exclusion.
Criteria:
    {criteria}
""",
    input_variables=["criteria"],
)