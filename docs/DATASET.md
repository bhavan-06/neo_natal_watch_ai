# DATASET.md — NeoNatal Watch AI
# Dataset Analysis and Selection Report

> ⚠️ **ACADEMIC PROTOTYPE NOTICE**
> This document is part of an academic research prototype.
> No dataset described here guarantees clinical validity.
> All labels used for model training are research-defined, not clinically validated.

---

## 1. Dataset Landscape Summary

Finding a single, perfect, publicly available, open-access neonatal ICU dataset
with all the following properties is **extremely difficult**:

- ✅ Truly neonatal / NICU population
- ✅ Multiple vital signs (HR, SpO2, RR, Temperature, BP)
- ✅ Timestamped, multi-patient
- ✅ Clinical event labels suitable for deterioration prediction
- ✅ Freely downloadable without credentialing

This honest assessment is documented below for each investigated dataset.

---

## 2. Datasets Investigated

---

### Dataset A: Preterm Infant Cardio-Respiratory Signals (PICS) Database

| Field                | Details |
|----------------------|---------|
| **Full Name**        | Preterm Infant Cardio-Respiratory Signals Database v1.0.0 |
| **Source**           | PhysioNet |
| **URL**              | https://physionet.org/content/picsdb/1.0.0/ |
| **DOI**              | https://doi.org/10.13026/C2QQ2M |
| **Published**        | February 9, 2017 |
| **Population**       | ✅ **Truly Neonatal** — 10 preterm infants, post-conceptional age 29–34 weeks |
| **Study Weights**    | 843 to 2100 grams (mean: 1468 g) |
| **Recording Duration** | ~20–70 hours per infant |
| **Signals Available** | ECG (500 Hz or 250 Hz), Respiration via inductance bands (50 Hz) |
| **Vital Signs**      | ❌ No SpO2 directly. ❌ No Temperature. ❌ No Blood Pressure. ✅ HR derivable from ECG. ✅ Respiratory signal available. |
| **Labels**           | ✅ Bradycardia onset annotations (HR < 100 bpm, ≥ 2 beats). ❌ No sepsis labels. ❌ No temperature or multi-organ failure labels. |
| **Sampling Frequency** | ECG: 500/250 Hz. Respiration: 50 Hz. High-frequency waveform data. |
| **Format**           | WFDB (Waveform Database) binary format — needs `wfdb` Python library to read |
| **License**          | Open Data Commons Attribution License v1.0 — **Fully Open Access** |
| **Access Requirements** | ✅ No credentialing required. Downloadable by anyone. |
| **Dataset Size**     | ~1.6 GB (ZIP) |

#### Suitability Assessment for NeoNatal Watch AI

| Component             | Suitable? | Notes |
|-----------------------|-----------|-------|
| HR extraction         | ✅ Yes    | Derivable from R-R intervals |
| SpO2                  | ❌ No     | Not recorded |
| Respiratory Rate      | ✅ Partial | Raw respiration waveform available; RR must be computed |
| Temperature           | ❌ No     | Not recorded |
| Blood Pressure        | ❌ No     | Not recorded |
| Multi-vital dashboard | ❌ Limited | Only 2 signal types |
| Deterioration labels  | ⚠️ Partial | Bradycardia labels only — not general deterioration |
| Multi-patient         | ✅ Yes    | 10 infants |
| ML training           | ⚠️ Limited | Only 10 patients — very small for deep learning |

**Verdict:** Authentic neonatal dataset, open access, but severely limited in scope.
Only 2 raw signal types (ECG + respiration), only 10 patients, and only bradycardia labels.
**Cannot support the full multi-vital monitoring pipeline as-is.**
However, it CAN be used for:
- Validating that the system can process real neonatal waveforms
- Demonstrating HR and RR extraction from raw signals
- Demonstrating bradycardia event detection

---

### Dataset B: MIMIC-III Clinical and Waveform Database (Neonatal Subset)

| Field                | Details |
|----------------------|---------|
| **Full Name**        | MIMIC-III (Medical Information Mart for Intensive Care) v1.4 |
| **Source**           | PhysioNet |
| **URL**              | https://physionet.org/content/mimiciii/1.4/ |
| **Waveform URL**     | https://physionet.org/content/mimic3wdb/1.0/ |
| **Population**       | ⚠️ **Partially Neonatal** — MIMIC-III includes ~7,870 neonatal ICU admissions out of ~61,000 total admissions |
| **Hospital**         | Beth Israel Deaconess Medical Center (BIDMC), Boston |
| **Vital Signs**      | ✅ HR, ✅ SpO2, ✅ RR, ✅ Temperature, ✅ Systolic/Diastolic BP (for neonatal subset from chart events) |
| **Waveform Data**    | ✅ High-resolution ECG, ABP, PPG (for matched waveform subset) |
| **Labels**           | ⚠️ No direct "deterioration" label — researchers must define using ICD-9 codes, antibiotic orders, blood culture events, mortality |
| **Sampling Frequency** | Waveform: up to 500 Hz. Clinical vitals: charted at varying intervals (typically 1/hr to 4/hr) |
| **Format**           | Clinical: PostgreSQL database + CSV export. Waveform: WFDB format |
| **License**          | PhysioNet Credentialed Health Data License 1.5.0 |
| **Access Requirements** | ❌ **Credentialed Access Required:** (1) Register on PhysioNet, (2) Complete CITI "Data or Specimens Only Research" training (~3–5 hours), (3) Sign Data Use Agreement (DUA), (4) Wait for approval |
| **Access Timeline**  | Typically 1–7 days after CITI completion |
| **CITI Training URL** | https://www.citiprogram.org/ |
| **Dataset Size**     | Clinical: ~6 GB. Waveform: ~2.7 TB |

#### Suitability Assessment for NeoNatal Watch AI

| Component             | Suitable? | Notes |
|-----------------------|-----------|-------|
| HR, SpO2, RR, Temp, BP | ✅ Yes  | All available in chart events for neonatal admissions |
| Truly neonatal        | ✅ Yes    | ~7,870 NICU admissions available |
| Deterioration labels  | ⚠️ Requires work | Must be defined from ICD-9, antibiotic orders, or mortality |
| Sepsis labels         | ⚠️ Research-defined | Not pre-labelled; must be derived |
| Multi-patient         | ✅ Yes    | Thousands of patients |
| ML training           | ✅ Excellent | Large enough for deep learning |
| Access                | ❌ Requires CITI + DUA | Cannot be used immediately |

**Verdict:** Best available dataset for this project IF access is obtained.
Contains authentic neonatal vital signs with multi-parameter coverage.
However, **cannot be used without completing CITI training and DUA**.
For academic students, this process is recommended and encouraged.

---

### Dataset C: MIMIC-II Waveform Database

| Field                | Details |
|----------------------|---------|
| **Full Name**        | MIMIC-II Waveform Database v3.0 |
| **Source**           | PhysioNet |
| **URL**              | https://physionet.org/content/mimic2wdb/3.0/ |
| **Population**       | Adults + some neonates from BIDMC |
| **Vital Signs**      | ✅ ECG, BP, SpO2 waveforms |
| **Labels**           | ❌ No pre-defined deterioration labels |
| **Access**           | ✅ Waveform portion is Open Access |
| **License**          | Open Data Commons Attribution License v1.0 |
| **Status**           | ⚠️ **Superseded** — Community strongly recommends using MIMIC-III or MIMIC-IV instead |

**Verdict:** Open access waveform component, but superseded by MIMIC-III.
Clinical annotation requires the credentialed MIMIC-III clinical database.
**Not recommended as primary dataset; use MIMIC-III instead.**

---

### Dataset D: MIMIC-IV

| Field                | Details |
|----------------------|---------|
| **Full Name**        | MIMIC-IV v2.2 |
| **Source**           | PhysioNet |
| **URL**              | https://physionet.org/content/mimiciv/2.2/ |
| **Population**       | ❌ **Does NOT include neonatal patients** |
| **Notes**            | MIMIC-IV reorganized the database. Neonatal data from BIDMC is managed separately. MIMIC-IV focuses on adult ICU patients. |
| **Access**           | Credentialed |

**Verdict:** ❌ **NOT suitable** — does not contain neonatal patients.
Do not claim MIMIC-IV has neonatal data.

---

### Dataset E: PhysioNet/CinC Challenge 2019 — Early Prediction of Sepsis

| Field                | Details |
|----------------------|---------|
| **Full Name**        | Early Prediction of Sepsis from Clinical Data: The PhysioNet/CinC Challenge 2019 |
| **Source**           | PhysioNet |
| **URL**              | https://physionet.org/content/challenge-2019/1.0.0/ |
| **Population**       | ❌ **Adult ICU patients only** — not neonatal |
| **Vital Signs**      | ✅ HR, SpO2 (O2Sat), Temperature, Systolic BP, Diastolic BP, MAP, Respiratory Rate, EtCO2 |
| **Labels**           | ✅ **SepsisLabel** — binary (0/1) sepsis label per timestep — best available deterioration label |
| **Patients**         | ~40,000+ ICU stay records |
| **Sampling**         | Hourly intervals |
| **Format**           | PSV (pipe-separated values) — simple to load with pandas |
| **License**          | Open Data Commons Attribution License v1.0 |
| **Access**           | ✅ **Fully Open Access** — no credentialing required |
| **Dataset Size**     | ~250 MB (compressed) |

#### Variable List (42 variables)

**Vital Signs (8):** HR, O2Sat, Temp, SBP, MAP, DBP, Resp, EtCO2

**Lab Values (26):** BaseExcess, HCO3, FiO2, pH, PaCO2, SaO2, AST, BUN, Alkalinephos, Calcium, Chloride, Creatinine, Bilirubin_direct, Glucose, Lactate, Magnesium, Phosphate, Potassium, Bilirubin_total, TroponinI, Hct, Hgb, PTT, WBC, Fibrinogen, Platelets

**Demographics (8):** Age, Gender, Unit1, Unit2, HospAdmTime, ICULOS, SepsisLabel

#### Suitability Assessment for NeoNatal Watch AI

| Component             | Suitable? | Notes |
|-----------------------|-----------|-------|
| HR, SpO2, RR, Temp, BP | ✅ All 8 vital signs | Exactly what we need |
| SepsisLabel           | ✅ Yes    | Binary label per timestep — perfect for supervised ML |
| Multi-patient         | ✅ Yes    | ~40,000+ records |
| ML training           | ✅ Excellent | Large, well-structured, used in many papers |
| Truly neonatal        | ❌ No     | Adult ICU patients |
| Open access           | ✅ Yes    | Immediately downloadable |
| Format                | ✅ Simple | PSV files, easily parsed |

**Verdict:** ✅ **Best choice for immediate software development and model training.**
Despite being adult ICU data, it contains all the vital sign columns we need with a
ready-to-use sepsis label. We will use this dataset while clearly labeling it as
"adult ICU reference data adapted for prototype development."
The software pipeline built on this dataset will be architecturally identical to
what would be needed for genuine neonatal data.

---

### Dataset F: PhysioNet/CinC Challenge 2012 — ICU Mortality Prediction

| Field                | Details |
|----------------------|---------|
| **Full Name**        | Predicting Mortality of ICU Patients: CinC Challenge 2012 |
| **Source**           | PhysioNet |
| **URL**              | https://physionet.org/content/challenge-2012/1.0.0/ |
| **Population**       | ❌ Adults — MIMIC-II derived |
| **Vital Signs**      | ✅ HR, RespRate, Temperature, NIDiasABP, NISysABP, SpO2 (partial) |
| **Labels**           | ✅ In-hospital mortality (binary) |
| **Patients**         | 12,000 ICU records |
| **Format**           | TXT time-series per patient |
| **License**          | Open |
| **Access**           | ✅ Open Access |

**Verdict:** Useful secondary reference. Not neonatal. Mortality label is less granular than per-timestep SepsisLabel from Challenge 2019.

---

### Dataset G: Paediatric Intensive Care (PIC) Database

| Field                | Details |
|----------------------|---------|
| **Full Name**        | Paediatric Intensive Care (PIC) Database v1.1.0 |
| **Source**           | PhysioNet |
| **URL**              | https://physionet.org/content/picdb/1.1.0/ |
| **Population**       | ⚠️ Paediatric (includes NICU) — Chinese hospital data |
| **Vital Signs**      | ✅ HR, SpO2, RR, Temperature, BP (from nursing charts) |
| **Labels**           | ⚠️ Mortality, ICD codes — no pre-built deterioration label |
| **Access**           | ❌ Credentialed Access Required |
| **Notes**            | Lacks high-resolution minute-to-minute vital sign waveforms |

**Verdict:** Potentially useful but requires credentialing. Paediatric (not strictly neonatal).

---

## 3. Recommended Dataset Strategy

### For This Academic Prototype:

```
TIER 1 (Primary — Use immediately):
┌──────────────────────────────────────────────────────────┐
│  PhysioNet CinC Challenge 2019 (Sepsis Dataset)          │
│  • Open access — no credentials needed                   │
│  • All 8 vital signs: HR, SpO2, RR, Temp, BP            │
│  • Ready SepsisLabel (binary, per-timestep)              │
│  • ~40,000 patient records                               │
│  • Simple PSV format                                     │
│  ⚠️ Adult ICU — NOT neonatal                             │
│  Label all outputs: "Adult ICU Reference Data"           │
└──────────────────────────────────────────────────────────┘

TIER 2 (Supplemental — Neonatal signal validation):
┌──────────────────────────────────────────────────────────┐
│  PICS Database (PhysioNet)                               │
│  • Open access — no credentials needed                   │
│  • 10 preterm NICU infants                               │
│  • ECG + respiration waveforms                           │
│  • Bradycardia annotations                               │
│  ✅ Authentic neonatal data                              │
│  Use for: waveform demo, HR/RR extraction validation     │
└──────────────────────────────────────────────────────────┘

TIER 3 (Synthetic — Always available):
┌──────────────────────────────────────────────────────────┐
│  Synthetic Data Generator (built in this project)        │
│  • No access restrictions                                │
│  • Neonatal-range vital sign patterns                    │
│  • Normal + abnormal scenarios                           │
│  ⚠️ NOT real patient data — clearly labeled              │
│  Use for: real-time simulation, dashboard demo           │
└──────────────────────────────────────────────────────────┘

TIER 4 (Future — If CITI training completed):
┌──────────────────────────────────────────────────────────┐
│  MIMIC-III (Neonatal Subset, ~7,870 patients)            │
│  • Best available authentic neonatal EHR data            │
│  • Requires CITI training + DUA                          │
│  • Credentialing typically takes 1–7 days                │
│  Use for: future academic publication-grade experiments  │
└──────────────────────────────────────────────────────────┘
```

---

## 4. How to Access Each Dataset

### 4.1 PhysioNet CinC Challenge 2019 (Primary — Immediate)

```bash
# No login required
wget -r -N -c -np https://physionet.org/files/challenge-2019/1.0.0/

# Or download ZIP directly:
# https://physionet.org/content/challenge-2019/1.0.0/
```

Place downloaded files in: `data/raw/challenge2019/`

### 4.2 PICS Database (Neonatal Waveforms — Immediate)

```bash
# No login required
wget -r -N -c -np https://physionet.org/files/picsdb/1.0.0/
```

Place downloaded files in: `data/raw/picsdb/`

Install Python WFDB library to read files:
```bash
pip install wfdb
```

### 4.3 MIMIC-III (Requires Credentialing)

**Step 1:** Register at https://physionet.org/register/

**Step 2:** Complete CITI Training
- URL: https://www.citiprogram.org/
- Course: "Data or Specimens Only Research"
- Estimated time: 3–5 hours
- Certificate needed: Yes

**Step 3:** Sign Data Use Agreement (DUA)
- Available after CITI completion on PhysioNet profile

**Step 4:** Request access to MIMIC-III
- URL: https://physionet.org/content/mimiciii/1.4/

**Step 5:** After approval, download and extract to: `data/raw/mimic3/`

---

## 5. Dataset Comparison Table

| Criterion              | CinC 2019 | PICS | MIMIC-III | MIMIC-IV | CinC 2012 | PIC |
|------------------------|-----------|------|-----------|----------|-----------|-----|
| Neonatal population    | ❌        | ✅   | ✅        | ❌       | ❌        | ⚠️  |
| HR available           | ✅        | ✅*  | ✅        | ✅       | ✅        | ✅  |
| SpO2 available         | ✅        | ❌   | ✅        | ✅       | ⚠️        | ✅  |
| Respiratory Rate       | ✅        | ✅*  | ✅        | ✅       | ✅        | ✅  |
| Temperature            | ✅        | ❌   | ✅        | ✅       | ✅        | ✅  |
| Blood Pressure         | ✅        | ❌   | ✅        | ✅       | ✅        | ✅  |
| Deterioration label    | ✅        | ✅*  | ⚠️        | ⚠️       | ✅        | ⚠️  |
| Open access            | ✅        | ✅   | ❌        | ❌       | ✅        | ❌  |
| Immediately usable     | ✅        | ✅   | ❌        | ❌       | ✅        | ❌  |
| Number of patients     | ~40,000   | 10   | ~7,870 N  | N/A      | 12,000    | unk |
| Best for prototype     | ✅ **YES**| ⚠️   | ✅ Future  | ❌       | ⚠️        | ⚠️  |

*Derived from raw waveform

---

## 6. Label Strategy

### For CinC 2019 (Primary):
```
SepsisLabel = 1  →  "Deterioration Event" (for prototype purposes)
SepsisLabel = 0  →  "Stable" (for prototype purposes)
```
> **Important Disclaimer:** SepsisLabel from CinC 2019 refers to adult sepsis criteria.
> This is used purely as a proxy deterioration label for prototype development.
> It must NOT be claimed as neonatal sepsis ground truth.

### For PICS (Supplemental):
```
atr annotation (bradycardia onset) = 1  →  "Cardio-Respiratory Event"
No annotation in window             = 0  →  "Stable window"
```

### For Synthetic Data:
```
manually_injected_event = 1  →  "Simulated Deterioration Event"
normal_period           = 0  →  "Simulated Normal"
```

---

## 7. Vital Sign Reference Ranges

### Neonatal Normal Ranges (for synthetic data generation):

| Vital Sign            | Preterm Neonate          | Term Neonate           |
|-----------------------|--------------------------|------------------------|
| Heart Rate (HR)       | 120–160 bpm              | 100–160 bpm            |
| SpO2                  | 90–95% (preterm target)  | 95–100%                |
| Respiratory Rate (RR) | 40–60 breaths/min        | 30–60 breaths/min      |
| Temperature           | 36.5–37.5 °C             | 36.5–37.5 °C           |
| Systolic BP           | 40–60 mmHg (preterm)     | 60–90 mmHg (term)      |
| Diastolic BP          | 20–35 mmHg               | 30–60 mmHg             |

> **Source:** These are general reference ranges from neonatal care literature.
> They are used for synthetic data generation only. They are NOT clinical targets.

### Abnormal / Alert Patterns (for synthetic simulation):

| Condition             | Signal Pattern                                            |
|-----------------------|-----------------------------------------------------------|
| Bradycardia           | HR drops below 100 bpm (preterm), below 80 bpm (term)    |
| Apnea / Desaturation  | SpO2 drops below 85%, RR drops or becomes erratic        |
| Hyperthermia          | Temperature > 38.0 °C                                    |
| Hypothermia           | Temperature < 36.0 °C                                    |
| Tachycardia           | HR > 180 bpm                                             |
| Cardiovascular stress | BP drops, HR increases simultaneously                    |

---

## 8. Summary Recommendation

### Decision for NeoNatal Watch AI Prototype:

```
PRIMARY DATASET:   PhysioNet CinC Challenge 2019
                   Adult ICU (labeled "Reference ICU Data")
                   Used for all ML model training and evaluation

SUPPLEMENTAL:      PICS Database (10 preterm infants)
                   Used for neonatal waveform demonstration

SYNTHETIC:         Custom generator (built in Phase 4)
                   Used for real-time simulation dashboard

FUTURE GOAL:       MIMIC-III neonatal subset
                   After completing CITI training
                   For academic publication-grade experiments
```

This approach is honest, transparent, academically sound, and immediately executable
without waiting for data access approvals.

---

## 9. References

1. Gee, A. H., Barbieri, R., Paydarfar, D., & Indic, P. (2017). Predicting Bradycardia in
   Preterm Infants Using Point Process Analysis of Heart Rate. IEEE Transactions on
   Biomedical Engineering, 64(9), 2300–2308. https://doi.org/10.1109/TBME.2016.2632746

2. Reyna, M. A., et al. (2020). Early Prediction of Sepsis From Clinical Data: The
   PhysioNet/Computing in Cardiology Challenge 2019. Critical Care Medicine.
   https://physionet.org/content/challenge-2019/1.0.0/

3. Johnson, A. E. W., et al. (2016). MIMIC-III, a freely accessible critical care
   database. Scientific Data, 3, 160035. https://doi.org/10.1038/sdata.2016.35

4. PhysioNet. (2026). PhysioNet as a global platform for biomedical research.
   Nature Health. https://doi.org/10.1038/s44360-026-00096-z

---

*Generated: 2026-09-21 | NeoNatal Watch AI — Phase 1: Dataset Analysis*

