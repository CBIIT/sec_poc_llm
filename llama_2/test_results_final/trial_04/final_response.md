| Criterion Text | Inclusion/Exclusion | Disease | Biomarker | Prior Therapy | Criterion Rule |
| --- | --- | --- | --- | --- | --- |
| Pathologically confirmed diagnosis of high-grade (grade 2-3) epithelial ovarian cancer, primary peritoneal cancer, or fallopian tube carcinoma (EOC), which are serous, endometrioid, clear cell, mucinous, mixed epithelial, or undifferentiated | Inclusion | Epithelial ovarian cancer | - | - | (EOC) = (serous ∨ endometrioid ∨ clear cell ∨ mucinous ∨ mixed epithelial ∨ undifferentiated) |
|  Baseline values of CA-125 at least 2 x upper limit of normal AND EITHER | Inclusion | Ovarian cancer | CA-125 | None | (CA-125 ≥ 2 x ULN) ∧ (presence of EITHER condition A OR condition B) |
| Patient’s carcinoma should express the FSHR antigen, detectable by polymerase chain reaction (PCR) analysis of archival tumor sample | Inclusion | None | FSHR | None | FSHR expression ≠ negative |
| Tissue IHC FSHR positivity in the historical FFPE sample is not required for eligibility | Inclusion | None | FSHR | None | NOT (FSHR) |
| Patients must have had 1 prior platinum-based chemotherapeutic regimen for the management of ovarian, primary peritoneal, or fallopian tube carcinoma and at least 2 prior chemotherapy regimens | Inclusion | Ovarian, primary peritoneal, or fallopian tube carcinoma | - | Platinum-based chemotherapy | CriterionText = "Patients must have had 1 prior platinum-based chemotherapeutic regimen for the management of ovarian, primary peritoneal, or fallopian tube carcinoma and at least 2 prior chemotherapy regimens" |
| Patients should be considered platinum-refractory (progression while on a prior platinum chemotherapy) or resistant (persistence or recurrence within 6 months after a prior platinum chemotherapy) and be deemed unlikely to have significant benefit from any standard therapies by the treating investigator | Inclusion | None | None | Platinum chemotherapy | Patients who have progressed or recurred within 6 months of platinum chemotherapy and are unlikely to benefit from standard therapies, as determined by the treating investigator, are eligible. |
| Patients with a known germline or somatic BRCA pathogenic mutation should have a prior PARP inhibitor and subsequent progression, unless they have a documented history of intolerance or inability to swallow oral medications | Inclusion | BRCA | BRCA1, BRCA2 | PARP inhibitor | Criterion Rule: (BRCA1 or BRCA2) and (PARP inhibitor) and (progression) and not (intolerance or inability to swallow oral medications) |
| Patients are allowed to receive, but are not required to receive, up to 6 additional prior chemotherapy treatment regimens (including platinum-based chemotherapy) | Inclusion | None | None | Chemotherapy | (Prior Chemotherapy ≤ 6) |
| Prior maintenance therapy with an agent when there has not been progression will not be a separate treatment regimen | Inclusion | None | None | Maintenance Therapy | (Progression-free Maintenance Therapy = True) |
| Prior hormonal therapy is allowed, and when used alone, even as a therapeutic agent, it does not count toward this prior regimen requirement | Inclusion | None | None | Hormonal Therapy | (Hormonal Therapy ≠ Chemotherapy) |
| Hormonal therapy must be discontinued at least 1 week before T-cell infusion | Inclusion | None | None | Hormonal Therapy | (Hormonal Therapy Discontinued ≥ 1 week before T-cell Infusion) |
| Continuation of hormone replacement therapy is permitted | Inclusion | None | None | Hormone Replacement Therapy | (Hormone Replacement Therapy = True) |
| No anticancer therapy in the 3 weeks before the T-cell infusion (and all hematologic effects have resolved) | Inclusion |  |  | Chemotherapy, biologic therapy, or immunotherapy |  ~TreatmentFreeInterval(3 weeks) ∧ HematologicEffectsResolved() |
| No prior immunotherapy with checkpoint blockade (e.g., PD1 inhibitor, PDL1 inhibitor, or CTL4- antagonist or similar agent) in the 6 months before the T-cell infusion (and all clinically significant related side effects must be resolved) | Inclusion |  |  | Immunotherapy with checkpoint blockade |  ~ImmunotherapyFreeInterval(6 months) ∧ SideEffectsResolved() |
| Known active hepatitis B infection | Exclusion | Hepatitis B | - | - | NOT (Hepatitis B) |
| Known history of hepatitis C or human immunodeficiency virus (HIV) infection | Exclusion | Hepatitis C, HIV | - | - | NOT (Hepatitis C) AND NOT (HIV) |
| Clinically significant heart disease (New York Heart Association class 3 or 4) or symptomatic congestive heart failure | Exclusion | Heart disease |  |  | "HeartDisease(NYHA3or4) ∨ SymptomaticCHF" |
| Myocardial infarction < 6 months before enrollment | Exclusion | Myocardial infarction |  |  | "MI(<6months)" |
| History of severe non-ischemic cardiomyopathy with ejection fraction < 20% | Exclusion | Cardiomyopathy |  |  | "Cardiomyopathy(ejectionFraction<20%)" |
| Active autoimmune disease... | Exclusion | Systemic lupus erythematous |  |  | (Disease = "Systemic lupus erythematous") ∧ (Disease = "Rheumatoid arthritis") ∧ (Disease = "Ulcerative colitis") ∧ (Disease = "Crohn's disease") ∧ (Disease = "Temporal arteritis") |
| Known or suspected leptomeningeal disease and patients with metastases to the brain stem, midbrain, pons, or medulla | Exclusion | Leptomeningeal disease | - | - | NOT (LeptomeningealDisease OR BrainStemMetastases OR MidbrainMetastases OR PonsMetastases OR MedullaMetastases) |
| Known or suspected untreated brain metastases | Exclusion | Brain Metastases | None | None | NOT (Brain Metastases = "Untreated") |
| Patients with radiographically stable, asymptomatic previously irradiated lesions are eligible | Inclusion | Brain Metastases | None | Cranial irradiation | (Brain Metastases = "Previously irradiated" AND Time since completion of cranial irradiation > 4 weeks AND Time since completion of corticosteroid therapy > 3 weeks) |
| Prior history of clinically significant seizure disorder (e.g., not including childhood febrile seizures) | Exclusion | Seizure Disorder |  |  | HasSeizureDisorder(true) |
| Any concurrent active malignancies | Exclusion | Ovarian cancer | - | - | !Expectant observation |
| Prior radiotherapy to any portion of the abdominal cavity or pelvis | Exclusion |  |  | Radiotherapy | NOT (Radiotherapy = "None") |