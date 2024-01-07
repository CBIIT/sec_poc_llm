from langchain.prompts.few_shot import FewShotPromptTemplate
from langchain.prompts.prompt import PromptTemplate
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.prompts.example_selector import SemanticSimilarityExampleSelector
from langchain_community.vectorstores import Chroma


examples = [
    {
        "context": """
You are in the role of an abstractor who will analyze eligibility criteria for a clinical trial and represent the information as a list of individual criteria in a tabular format that will contain the following columns: 
Type: listing whether criterion is an Exclusion or Inclusion criterion
Original Text: the original text of the criterion
Disease/Condition: If the criterion contains a disease or condition name it by its canonical name
Procedure: If the criterion contains a therapeutic procedure name it by its canonical name
Drug:  If the criterion contains a therapeutic drug name it by its canonical name
Biomarker:  If the criterion contains a biomarker name it by its canonical name
Computable Rule: Translate the criteria into a logical expression that could be interpreted programmatically
Here is the criteria to analyze:
    Inclusion Criteria
    •	Age 18 or older
    •	Willing and able to provide informed consent
    •	Metastatic breast cancer, biopsy proven
    o	Estrogen receptor (ER)+/HER2-, defined as > 5% ER+ staining
    o	HER2+ (regardless of ER status), including HER2-low and high expressors
    •	History of at least 6 months, sustained response to systemic therapy (clinically or radiographically defined as complete or stable response without progression)
    •	Isolated site of disease progression on fludeoxyglucose F-18 (FDG) positron emission tomography (PET) scan
    •	Consented to 12-245
    •	Eastern Cooperative Oncology Group (ECOG) performance status 0-1

    Exclusion Criteria
    •	Pregnancy
    •	Serious medical comorbidity precluding radiation, including connective tissue disorders
    •	Intracranial disease (including previous intracranial involvement)
    •	Previous radiotherapy to the intended treatment site that precludes developing a treatment plan that respects normal tissue tolerances 
""",
        "answer": """
| Type | Original Text | Disease/Condition | Procedure | Drug | Biomarker | Computable Rule |
| --- | --- | --- | --- | --- | --- | --- |
| Inclusion | Metastatic breast cancer, biopsy proven | Metastatic breast cancer | | | | diagnosis == "Metastatic breast cancer" |
| Inclusion | Estrogen receptor (ER)+/HER2-, defined as > 5% ER+ staining | | | | HER2- | HER2 > 5% ER+ staining |
| Inclusion | HER2+ (regardless of ER status), including HER2-low and high expressors | | | | HER2+ | |
| Exclusion | Previous radiotherapy to the intended treatment site that precludes developing a treatment plan that respects normal tissue tolerances | | Prior radiation therapy | | | Prior radiation therapy is True |
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
You are in the role of an abstractor who will analyze eligibility criteria for a clinical trial and represent the information as a list of individual criteria in a tabular format that will contain the following columns:
Type: listing whether criterion is an Exclusion or Inclusion criterion
Original Text: the original text of the criterion
Disease/Condition: If the criterion contains a disease or condition name it by its canonical name
Procedure: If the criterion contains a therapeutic procedure name it by its canonical name
Drug:  If the criterion contains a therapeutic drug name it by its canonical name
Biomarker:  If the criterion contains a biomarker name it by its canonical name
Computable Rule: Translate the criteria into a logical expression that could be interpreted programmatically
Here is the criteria to analyze:
    {criteria}
""",
    input_variables=["criteria"],
)

prompt_zero = PromptTemplate.from_template("""Task:
You are in the role of an abstractor who will analyze eligibility criteria for a clinical trial and represent the information as a list of individual criteria in a tabular format that will contain the following columns:
Type: listing whether criterion is an Exclusion or Inclusion criterion
Original Text: the original text of the criterion
Disease/Condition: If the criterion contains a disease or condition name it by its canonical name
Procedure: If the criterion contains a therapeutic procedure name it by its canonical name
Drug:  If the criterion contains a therapeutic drug name it by its canonical name
Biomarker:  If the criterion contains a biomarker name it by its canonical name
Computable Rule: Translate the criteria into a logical expression that could be interpreted programmatically
Here is the criteria to analyze:
    {criteria}
""")

prompt_zero_minimal = PromptTemplate.from_template("""Based on the following list of criteria, extract the diseases, biomarkers, and prior therapies for each. If you aren't sure how to categorize a criterion, please skip that line and continue on to the next.
    {criteria}
""")
