| Criterion Text | Inclusion/Exclusion | Disease | Biomarker | Prior Therapy | Criterion Rule |
| --- | --- | --- | --- | --- | --- |
| In good general health as evidenced by medical history to be a candidate for curative-intent prostate cancer treatment | Inclusion | Prostate Cancer | - | - | Good general health status |
| Previously untreated prostate cancer (with cytotoxic chemotherapy, cryotherapy, surgical or radiation therapy) | Inclusion | Prostate Cancer | None | None | (Disease = "Prostate Cancer") AND (Prior Therapy = "None") |
| Localized adenocarcinoma of the prostate with the following features | Inclusion | Prostate Adenocarcinoma | - | - | (Feature 1) ∧ (Feature 2) ∧ (Feature 3) |
| PSA < 20 | Inclusion | Prostate Cancer | PSA | None | PSA(<20) |
| Patients receiving a 5-alpha reductase inhibitor must have a PSA < 10 | Inclusion | Prostate cancer | PSA | 5-alpha reductase inhibitor | PSA < 10 |
| International Prostate Symptom Score (IPSS) score =< 20 at time of initial history and physical with treating radiation oncologist | Inclusion | Prostate Cancer | - | - | IPSS score ≤ 20 |
| Concurrent use of testosterone supplementation as it is contraindicated during prostate cancer treatment | Exclusion | Prostate Cancer |  |  | HasTestosteroneSupplementation(true) ∧ HasProstateCancer(true) |
|  Prior pelvic RT | Exclusion |  |  | Pelvic RT | Not Pelvic RT |
| Prior or concurrent invasive pelvic malignancy (except non-melanomatous skin cancer) or lymphomatous or hematogenous malignancy, unless disease free for a minimum of 5 years | Exclusion | Pelvic malignancy | - | - | !(DiseaseFreeFor5Years)  |
| Prior prostatectomy, cryotherapy, high-intensity focused ultrasound directed towards the prostate for any prostate disease or condition | Exclusion | Prostate Cancer | None | Prostatectomy, cryotherapy, high-intensity focused ultrasound | Not (Prostatectomy OR Cryotherapy OR High-Intensity Focused Ultrasound) |
