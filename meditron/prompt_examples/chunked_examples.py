examples = [
    {
        "context": """
Below is an example of clinical trial eligibility inclusion/exclusion criteria. Your task is to identify 3 categories of data within it. The 3 categories are: 1) Disease: a disorder affecting humans, 2) Biomarker: genes, proteins, or other substances that can be tested for to reveal important details about a patient’s cancer, and 3) Prior Therapy: medications, surgeries, or procedures that a patient may be treated with. For each of the identified categories, state whether it is an inclusion or exclusion.
Criteria:
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
Diseases: Metastatic breast cancer (inclusion)
Biomarkers: Estrogen receptor (ER)+/HER2-, HER2+ (inclusion)
Prior Therapies: Previous radiotherapy to the intended treatment site (exclusion)
""",
    },
    {
        "context": """
Below is an example of clinical trial eligibility inclusion/exclusion criteria. Your task is to identify 3 categories of data within it. The 3 categories are: 1) Disease: a disorder affecting humans, 2) Biomarker: genes, proteins, or other substances that can be tested for to reveal important details about a patient’s cancer, and 3) Prior Therapy: medications, surgeries, or procedures that a patient may be treated with. For each of the identified categories, state whether it is an inclusion or exclusion.
Criteria:
    Inclusion Criteria
    •	Signed informed consent must be obtained prior to performing any specific pre-screening and screening procedure
    •	Male or female >= 18 years of age at the time of informed consent
    •	Histologically or cytologically confirmed diagnosis of advanced/metastatic differentiated thyroid cancer
    •	Radio active iodine refractory disease
    •	BRAFV600E mutation positive tumor sample as per Novartis designated central laboratory result
    •	Has progressed on at least 1 but not more than 2 prior VEGFR targeted therapy
    •	Eastern Cooperative Oncology Group performance status >= 2
    •	At least one measurable lesion as defined by RECIST 1.1
    •	Anaplastic or medullary carcinoma of the Tyroid

    Exclusion Criteria
    •	Previous treatment with BRAF inhibitor and/or MEK inhibitor
    •	Concomitant RET Fusion Positive Thyroid cancer
    •	Receipt of any type of small molecule kinase inhibitor within 2 weeks before randomization
    •	Receipt of any type of cancer antibody or systemic chemotherapy within 4 weeks before randomization
    •	Receipt of radiation therapy for bone metastasis within 2 weeks or any other radiation therapy within 4 weeks before randomization
    •	A history or current evidence/risk of retinal vein occlusion or central serous retinopathy
""",
        "answer": """
Diseases: thyroid cancer (inclusion), Anaplastic or medullary carcinoma of the Tyroid (inclusion)
Biomarkers: BRAFV600E mutation positive (inclusion), RET Fusion Positive (exclusion)
Prior Therapies: VEGFR targeted therapy (inclusion), BRAF inhibitor and/or MEK inhibitor (exclusion)
""",
    },
    {
        "context": """
Below is an example of clinical trial eligibility inclusion/exclusion criteria. Your task is to identify 3 categories of data within it. The 3 categories are: 1) Disease: a disorder affecting humans, 2) Biomarker: genes, proteins, or other substances that can be tested for to reveal important details about a patient’s cancer, and 3) Prior Therapy: medications, surgeries, or procedures that a patient may be treated with. For each of the identified categories, state whether it is an inclusion or exclusion.
Criteria:
    Inclusion Criteria
    •	Participants must be ‚â• 18 years of age
    •	Histologically or cytologically confirmed diagnosis of metastatic solid tumors
    •	Eastern Cooperative Oncology Group (ECOG) performance status 0-1
    •	All participants should have at least 1 measurable disease per RECIST v1.1. An irradiated lesion can be considered measurable only if progression has been demonstrated on the irradiated lesion.
    •	Body weight within [45 - 150 kg] (inclusive)
    •	All Contraceptive use by men and women should be consistent with local regulations regarding the methods of contraception for those participating in clinical studies.
    •	Capable of giving signed informed consent
    •	Any clinically significant cardiac disease
    •	History of or current interstitial lung disease or pneumonitis

    Exclusion Criteria
    •	Uncontrolled or unresolved acute renal failure
    •	Prior solid organ or hematologic transplant.
    •	Known positivity with human immunodeficiency virus (HIV), known active hepatitis A, B, and C, or uncontrolled chronic or ongoing infectious requiring parenteral treatment.
    •	Receipt of a live-virus vaccination within 28 days of planned treatment start
    •	Participation in a concurrent clinical study in the treatment period.
    •	Inadequate hematologic, hepatic and renal function
    •	Participant not suitable for participation, whatever the reason, as judged by the Investigator, including medical or clinical conditions.
""",
        "answer": """
Diseases: Metastatic solid tumor (inclusion)
Biomarkers: none
Prior Therapies: organ or hematologic transplant (exclusion)
"""
    },
    {
        "context": """
Below is an example of clinical trial eligibility inclusion/exclusion criteria. Your task is to identify 3 categories of data within it. The 3 categories are: 1) Disease: a disorder affecting humans, 2) Biomarker: genes, proteins, or other substances that can be tested for to reveal important details about a patient’s cancer, and 3) Prior Therapy: medications, surgeries, or procedures that a patient may be treated with. For each of the identified categories, state whether it is an inclusion or exclusion.
Criteria:
    Inclusion Criteria:
    •	Adults with a confirmed diagnosis of unresectable, locally advanced and/or metastatic Stage IIIB/IV NSCLC, Stage III/IV PDAC and/or Stage III/IV CRC with no curative-intent treatment options and documented activating KRAS mutation (without known additional actionable driver mutations such as EGFR, ALK or ROS1)
    •	Documented progression and measurable disease after ‚â• 1 prior line of systemic therapy (‚â• 2 and ‚â§ 4 prior lines for NSCLC) with adequate washout period and resolution of treatment-related toxicities to ‚â§ Grade 2
    •	ECOG PS of 0-2 (0-1 for PDAC) and a life expectancy > 3 months in the opinion of the Investigator
    •	Adequate hematological, liver, and renal function
    •	Men and women of childbearing potential must use adequate birth control measures for the duration of the trial and at least 90 days after discontinuing study treatment
    •	Symptomatic and/or untreated CNS or brain metastasis, pre-existing ILD or pericardial/pleural effusion of ‚â• grade 2 or requiring chronic oxygen therapy for COPD or pleural effusions
    •	Serious concomitant disorder including infection
    •	Known positive test for HIV, HCV, HBV surface antigen

    Exclusion Criteria:
    •	Concurrent malignancy in the previous 2 years
    •	Prior menin inhibitor therapy
    •	Requiring treatment with a strong or moderate CYP3A inhibitor/inducer
    •	Significant cardiovascular disease or QTcF or QTcB prolongation.
    •	Major surgery within 4 weeks prior to first dose
    •	Women who are pregnant or lactating.
""",
        "answer": """
Diseases: unresectable, locally advanced and/or metastatic Stage IIIB/IV NSCLC, Stage III/IV PDAC and/or Stage III/IV CRC (inclusion)
Biomarkers: KRAS mutation (inclusion)
Prior Therapies: menin inhibitor therapy (exclusion)
"""
    }
]