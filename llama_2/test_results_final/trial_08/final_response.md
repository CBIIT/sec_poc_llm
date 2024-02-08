| Criterion Text | Inclusion/Exclusion | Disease | Biomarker | Prior Therapy | Criterion Rule |
| --- | --- | --- | --- | --- | --- |
| Metastatic or locally advanced breast cancer not amenable to curative treatment by surgery or radiotherapy | Inclusion | Breast Cancer | None | None | (Disease = "Breast Cancer") AND (Treatment.Surgery = "Not Amenable") AND (Treatment.Radiotherapy = "Not Amenable") |
| Currently receiving palbociclib and AI or fulvestrant | Inclusion | Breast cancer | - | Palbociclib and AI or fulvestrant therapy for ≥6 months | (Disease = "Breast cancer") ∧ (Prior Therapy = "Palbociclib and AI or fulvestrant therapy for ≥6 months") |
| Currently receiving palbociclib or ribociclib and AI or fulvestrant therapy in the metastatic setting with evidence of progressive disease | Inclusion | Breast cancer | - | Palbociclib or ribociclib and AI or fulvestrant therapy for ≥6 months | (Disease = "Breast cancer") ∧ (Prior Therapy = "Palbociclib or ribociclib and AI or fulvestrant therapy for ≥6 months") ∧ (Evidence of progressive disease) |
| All men and premenopausal women must be on medical gonadal suppression therapy with a gonadotropin analog (e.g, goserelin or leuprolide) and have estrogen levels in the postmenopausal range by institutional criteria at baseline. | Inclusion | None | None | Gonadotropin analog (e.g, goserelin or leuprolide) | Criterion Text = "All men and premenopausal women must be on medical gonadal suppression therapy with a gonadotropin analog (e.g, goserelin or leuprolide) and have estrogen levels in the postmenopausal range by institutional criteria at baseline." |
| Has documented confirmation of histological or cytological HR-positive, HER2-negative breast cancer per local laboratory testing | Inclusion | Breast Cancer | HR-positive, HER2-negative | - | (HR-positive ∧ HER2-negative) |
| Up to 2 prior lines of systemic treatment (most recent line of therapy must be palbociclib and AI or fulvestrant for Phase 1b and palbociclib or ribociclib and AI or fulvestrant for Phase 2) in the locally advanced or metastatic setting is allowed; the participant must have shown evidence of progressive disease on palbociclib and AI or fulvestrant for Phase 1b and palbociclib or ribociclib and AI or fulvestrant for Phase 2 | Inclusion | None | None | Palbociclib, AI, fulvestrant, ribociclib | (Palbociclib ∧ AI ∧ (Phase 1b ∨ Phase 2)) ∨ (fulvestrant ∧ (Phase 1b ∨ Phase 2)) |
| Willing to provide a representative fresh tumor tissue specimen prior to enrollment | Inclusion | None | None | Palbociclib and AI or fulvestrant for Phase 1b, or palbociclib or ribociclib and AI or fulvestrant for Phase 2 | (Participant.willingness_to_provide_tumor_specimen = true) ∧ (Tumor.freshness = "fresh") ∧ (Tumor.tissue_type = "representative") ∧ (Study.phase = "Phase 1b" ∨ Study.phase = "Phase 2") ∧ (Participant.treatment_history.includes("palbociclib") ∧ Participant.treatment_history.includes("AI") ∨ Participant.treatment_history.includes("fulvestrant")) |
| Has received more than 2 lines of prior systemic therapy for locally advanced/metastatic breast cancer. | Inclusion | Breast Cancer | None | Systemic Therapy | (Prior Systemic Therapy ≥ 2) |
| Had prior exposure to any signal transducer and activator of transcription 3 (STAT3) inhibitor. | Inclusion |  |  | STAT3 inhibitor | Exists(PriorExposure) ∧ TypeOf(PriorExposure, STAT3Inhibitor) |
| Had radiotherapy within 3 weeks prior to Cycle 1 Day 1 (cycle is 28 days). | Inclusion |  |  | Radiotherapy | CriterionTextContains("radiotherapy") & TimeIntervalBeforeCycle1Day1IsLessThanOrEqualTo3Weeks & Grade1OrLessToxicitiesRecovered |
| Participants must have recovered from radiotherapy toxicities prior to starting study treatment and recovered to Grade 1 or better from related side effects of such therapy (with the exception of alopecia). | Inclusion |  |  | Radiotherapy | CriterionTextContains("radiotherapy") & TimeIntervalBeforeCycle1Day1IsLessThanOrEqualTo3Weeks & Grade1OrLessToxicitiesRecovered & AlopeciaIsNotPresent |
| Has HER2 overexpression by local laboratory testing (immunohistochemical [IHC] 3+ or in situ hybridization positive) | Inclusion | HER2-positive breast cancer | HER2 | None | (IHC 3+ OR ISH positive) |
| Has known loss of retinoblastoma tumor suppressor gene (Rb) (testing not mandatory) | Inclusion | Retinoblastoma | - | - | (Rb_status = "lost") |
| Has had disease progression on more than two cyclin-dependent kinase (CDK)4/6 inhibitors | Inclusion | None | None | Palbociclib or ribociclib | HasProgressedOn(CDK4/6Inhibitor, 2) |
| Adjuvant abemaciclib is allowed but must have progressed on palbociclib or ribociclib | Inclusion | None | None | Palbociclib or ribociclib, Abemaciclib | HasProgressedOn(CDK4/6Inhibitor, 2) ∧ (Palbociclib ∨ Ribociclib) → Abemaciclib |
| Concurrently using other anticancer therapy | Inclusion |  |  | Palbociclib and AI or fulvestrant for Phase 1b and palbociclib or ribociclib and AI or fulvestrant for Phase 2 | (Therapy = Palbociclib ∧ Therapy = AI ∧ Therapy = Fulvestrant) ∨ (Therapy = Ribociclib ∧ Therapy = AI ∧ Therapy = Fulvestrant) |