# Synthetic Patients Casebook & Longitudinal Trajectories

**Project**: NeoNatal Watch AI  
**Dataset**: Academic Demonstration Dataset v1.0  
**Classification**: 100% SYNTHETIC / ACADEMIC DEMONSTRATION DATA (NOT FOR CLINICAL USE)  

This casebook details the clinical journey of each synthetic patient across the maternal-fetal-neonatal continuum.

---

## Patient 1: `P-SYN-001` (Sarah Miller) — Scenario A: Normal Physiological Pregnancy

### 1. Patient & Maternal Profile
- **Patient ID**: `P-SYN-001` (Code: `SYN-PAT-001`)
- **Maternal Age**: 28 years | **BMI**: 22.4 kg/m² | **MAP**: 82 mmHg
- **Medical History**: Nulliparous, healthy, no chronic hypertension, no pregestational diabetes.

### 2. Pregnancy & First Trimester Progression
- **Pregnancy ID**: `101` | **Conception**: Oct 1, 2025 | **EDD**: Jul 8, 2026
- **First Trimester Scan (GA 12.2w, Dec 10, 2025)**:
  - CRL: 58.2 mm | NT: 1.4 mm | Nasal Bone: Present
  - Serum Markers: PAPP-A 1.15 MoM, PlGF 62.0 pg/mL, free beta-hCG 1.02 MoM
  - Uterine Artery Doppler: Mean PI 1.12, no diastolic notch (normal impedance).
- **First-Trimester AI Prediction (Dec 10, 2025)**:
  - Predicted 20w EFW Percentile: **52.0%**
  - Deterioration / FGR Risk Score: **0.08** (Level: `LOW`)
  - Clinician Review: Low-risk routine antenatal care confirmed (`DOC-OBGYN-01`).
  - Prescription: Routine prenatal multivitamins with folic acid.

### 3. Mid-Trimester Follow-Up & Growth Analysis
- **Second Trimester Scan (GA 20.5w, Feb 6, 2026)**:
  - Actual EFW: 365 g | Actual EFW Percentile: **50.0%**
  - Umbilical Artery Doppler: Normal positive end-diastolic flow (PI 1.02, RI 0.65).
- **Longitudinal Growth Trajectory Analysis**:
  - Predicted Percentile: 52.0% vs Actual Percentile: 50.0% (Variance: **-2.0%**)
  - Status: `NORMAL_CONCORDANT`
  - Pattern: Steady physiological growth along the median trajectory.

### 4. Delivery & Newborn Outcome
- **Labor & Delivery (Jul 3, 2026)**: Spontaneous uncomplicated vaginal delivery at **39.2 weeks**.
- **Newborn (`SYN-NB-1001`)**: Weight: **3,350 g** | Length: 50.0 cm | Status: `healthy_live_birth`.
- **NICU Admission**: **None required**. Rooming-in with mother, discharged home day 2.

---

## Patient 2: `P-SYN-002` (Elena Rostova) — Scenario B: Fetal Growth Restriction (FGR) Decoupling

### 1. Patient & Maternal Profile
- **Patient ID**: `P-SYN-002` (Code: `SYN-PAT-002`)
- **Maternal Age**: 32 years | **BMI**: 24.1 kg/m² | **MAP**: 88 mmHg
- **Medical History**: History of mild childhood asthma, otherwise healthy.

### 2. Pregnancy & First Trimester Progression
- **Pregnancy ID**: `102` | **Conception**: Sep 15, 2025 | **EDD**: Jun 22, 2026
- **First Trimester Scan (GA 12.0w, Nov 24, 2025)**:
  - CRL: 55.0 mm | NT: 1.6 mm | Nasal Bone: Present
  - Serum Markers: PAPP-A 0.85 MoM, PlGF 44.0 pg/mL
  - Uterine Artery Doppler: Mean PI 1.45, normal resistance profile.
- **First-Trimester AI Prediction (Nov 24, 2025)**:
  - Predicted 20w EFW Percentile: **48.0%**
  - Deterioration / FGR Risk Score: **0.15** (Level: `LOW`)

### 3. Mid-Trimester Follow-Up & Growth Analysis
- **Second Trimester Scan (GA 22.0w, Feb 2, 2026)**:
  - Actual EFW: 410 g | Actual EFW Percentile: **22.0%** (Sharp divergence)
  - Biometry shows asymmetric growth lag: Abdominal Circumference (AC) dropped to 18th percentile.
  - Uterine Artery PI: 1.18 (mild resistance elevation).
- **Longitudinal Growth Trajectory Analysis**:
  - Predicted Percentile: 48.0% vs Actual Percentile: 22.0% (Variance: **-26.0%**)
  - Status: `GROWTH_RESTRICTION_SUSPECTED`
  - Pattern: Asymmetric fetal growth lag decoupled from first-trimester trajectory.
  - Alert: `growth_deviation_flag` (Severity: `medium`, Risk: 0.62) acknowledged by `DOC-OBGYN-02`.

### 4. Delivery & Postnatal NICU Course
- **Labor & Delivery (Jun 5, 2026)**: Induction of labor at **37.5 weeks** for late-onset FGR.
- **Newborn (`SYN-NB-1002`)**: Weight: **2,450 g** | Length: 46.5 cm | Status: `small_for_gestational_age`.
- **NICU Admission (`2001`)**: Admitted for 3 days for thermoregulation and feeding support.
- **NICU Telemetry**: 5 vital readings (HR 138-143 bpm, SpO2 96-98%). Discharged in stable condition.

---

## Patient 3: `P-SYN-003` (Amina Patel) — Scenario C: Vascular & Doppler-Related Early FGR

### 1. Patient & Maternal Profile
- **Patient ID**: `P-SYN-003` (Code: `SYN-PAT-003`)
- **Maternal Age**: 34 years | **BMI**: 26.8 kg/m² | **MAP**: 96 mmHg
- **Medical History**: Baseline elevated vascular tone.

### 2. Pregnancy & First Trimester Progression
- **Pregnancy ID**: `103` | **Conception**: Aug 20, 2025 | **EDD**: May 27, 2026
- **First Trimester Scan (GA 12.4w, Nov 1, 2025)**:
  - CRL: 57.0 mm | NT: 1.8 mm | Nasal Bone: Present
  - Serum Markers: PAPP-A 0.42 MoM (depressed), PlGF 24.5 pg/mL (significantly depressed)
  - Uterine Artery Doppler: Mean PI **2.25** with **bilateral protodiastolic notches** (high placental impedance).
- **First-Trimester AI Prediction (Nov 1, 2025)**:
  - Predicted 20w EFW Percentile: **30.0%**
  - Deterioration / FGR Risk Score: **0.68** (Level: `WATCH`)
  - Alert: `fgr_vascular_high_risk` triggered and acknowledged by `DOC-MFM-01`.
  - Clinical Intervention: Immediate initiation of **Aspirin 150 mg nightly** for preeclampsia prophylaxis.

### 3. Mid-Trimester Follow-Up & Growth Analysis
- **Second Trimester Scan (GA 21.0w, Jan 5, 2026)**:
  - Actual EFW: 340 g | Actual EFW Percentile: **14.0%**
  - Umbilical Artery Doppler: PI 1.48 (elevated), reduced end-diastolic velocity.
- **Longitudinal Growth Trajectory Analysis**:
  - Predicted Percentile: 30.0% vs Actual Percentile: 14.0% (Variance: **-16.0%**)
  - Status: `EARLY_FGR_VASCULAR`
  - Pattern: Persistent uteroplacental and fetoplacental vascular resistance.

### 4. Delivery & Postnatal NICU Course
- **Labor & Delivery (Apr 28, 2026)**: Urgent cesarean section at **35.8 weeks** due to abnormal Doppler and non-reassuring CTG.
- **Newborn (`SYN-NB-1003`)**: Weight: **2,080 g** | Length: 44.0 cm | Status: `late_preterm_fgr`.
- **NICU Admission (`2002`)**: Admitted to NICU for transient tachypnea of the newborn and low birth weight.
- **NICU Telemetry**: 5 vital readings with reactive mild tachycardia (HR 152-160 bpm, SpO2 94-97%). Discharged after 6 days.

---

## Patient 4: `P-SYN-004` (Maria Garcia) — Scenario D: Severe Maternal Comorbid Risk Pattern

### 1. Patient & Maternal Profile
- **Patient ID**: `P-SYN-004` (Code: `SYN-PAT-004`)
- **Maternal Age**: 37 years | **BMI**: 31.5 kg/m² | **MAP**: 108 mmHg
- **Medical History**: **Chronic essential hypertension** and **Pre-gestational Type 2 Diabetes Mellitus**.

### 2. Pregnancy & First Trimester Progression
- **Pregnancy ID**: `104` | **Conception**: Nov 1, 2025 | **EDD**: Aug 8, 2026
- **First Trimester Scan (GA 11.8w, Jan 10, 2026)**:
  - CRL: 52.0 mm | NT: 2.1 mm | Nasal Bone: Present
  - Serum Markers: PAPP-A 0.58 MoM, PlGF 31.0 pg/mL, free beta-hCG 1.45 MoM
  - Uterine Artery Doppler: Mean PI **1.95** with unilateral diastolic notch.
- **First-Trimester AI Prediction (Jan 10, 2026)**:
  - Predicted 20w EFW Percentile: **35.0%**
  - Deterioration / FGR Risk Score: **0.76** (Level: `HIGH`)
  - Alert: `maternal_comorbidity_high_risk` acknowledged by `DOC-MFM-02`.
  - Clinical Interventions: Labetalol 100 mg BID for hypertension + Aspirin 150 mg nightly.

### 3. Mid-Trimester Follow-Up & Growth Analysis
- **Second Trimester Scan (GA 20.0w, Mar 10, 2026)**:
  - Actual EFW: 320 g | Actual EFW Percentile: **28.0%**
  - Umbilical Artery Doppler: Positive diastolic flow maintained (PI 1.30).
- **Longitudinal Growth Trajectory Analysis**:
  - Predicted Percentile: 35.0% vs Actual Percentile: 28.0% (Variance: **-7.0%**)
  - Status: `MATERNAL_RISK_CONCORDANT`
  - Pattern: Mild symmetrical deceleration concordant with high maternal metabolic and vascular risk.

### 4. Delivery & Postnatal NICU Course
- **Labor & Delivery (Jul 15, 2026)**: Planned primary cesarean section at **36.5 weeks**.
- **Newborn (`SYN-NB-1004`)**: Weight: **2,550 g** | Length: 47.0 cm | Status: `near_term_infant`.
- **NICU Admission (`2003`)**: 3-day admission for maternal diabetes infant protocol and blood glucose stabilization.
- **NICU Telemetry**: 5 vital readings showing stable physiological glucose transition. Discharged healthy.

---

## Patient 5: `P-SYN-005` (Chloe Dupont) — Scenario E: Severe Preterm Birth with Acute NICU Telemetry & Alerts

### 1. Patient & Maternal Profile
- **Patient ID**: `P-SYN-005` (Code: `SYN-PAT-005`)
- **Maternal Age**: 29 years | **BMI**: 23.0 kg/m² | **MAP**: 85 mmHg
- **Medical History**: History of prior cervical cerclage, normal baseline health.

### 2. Pregnancy Progression
- **Pregnancy ID**: `105` | **Conception**: Jul 10, 2025 | **EDD**: Apr 16, 2026
- **First Trimester Scan (GA 12.1w, Sep 18, 2025)**:
  - CRL: 57.5 mm | NT: 1.3 mm | Nasal Bone: Present
  - Serum Markers: PAPP-A 1.05 MoM, PlGF 58.0 pg/mL (normal)
  - Uterine Artery Doppler: PI 1.15 (normal).
  - Predicted 20w EFW Percentile: **50.0%** (Risk: 0.10, `LOW`).
- **Second Trimester Scan (GA 22.0w, Nov 26, 2025)**:
  - Actual EFW: 475 g | Actual EFW Percentile: **48.0%** (Variance: **-2.0%**)
  - Status: `NORMAL_ANTEPARTUM` (Optimal somatic growth).

### 3. Acute Obstetric Complication
- **Acute PPROM (Feb 18, 2026)**: Preterm premature rupture of membranes occurred acutely at **32.0 weeks**.
- **Precipitous Delivery (Feb 19, 2026)**: Spontaneous preterm labor leading to delivery at **32.1 weeks**.
- **Newborn (`SYN-NB-1005`)**: Weight: **1,620 g** | Length: 41.0 cm | Status: `very_preterm_infant`.

### 4. Intensive NICU Course & Multimodal Telemetry
- **NICU Admission (`2004`)**: Level III NICU admission for moderate-to-severe **Respiratory Distress Syndrome (RDS)**.
- **High-Frequency Telemetry (11 time-series records)**:
  - Hours 0–2: Initial stabilization on nasal CPAP (HR 144 bpm, SpO2 95%).
  - Hours 3–4: **Acute Desaturation Episode** (SpO2 drops to **83.0%**, HR elevates to **174 bpm**, RR 64/min).
  - Hours 5–6: Surfactant administration and oxygen titration (SpO2 recovers to 89–96%).
- **AI Deterioration Alerts & Explainability**:
  - Model Output (`4005`): NICU-Autoencoder anomaly score **0.94** (reconstruction error spike).
  - Model Output (`4006`): Multimodal Fusion model deterioration risk **0.86**.
  - Alert (`5004`): `acute_neonatal_hypoxemia` (Severity: `high`, Risk: 0.88), acknowledged immediately by NICU fellow (`DOC-NEO-01`).
- **Outcome**: Successful extubation, transition to room air, discharged in good health after 35 days (Mar 25, 2026).

---

## Patient 6: `P-SYN-006` (Grace Tan) — Scenario F: Active / Ongoing Pregnancy Cohort

### 1. Patient & Maternal Profile
- **Patient ID**: `P-SYN-006` (Code: `SYN-PAT-006`)
- **Maternal Age**: 30 years | **BMI**: 21.8 kg/m² | **MAP**: 84 mmHg
- **Medical History**: Healthy primigravida.

### 2. Active Gestation Milestones
- **Pregnancy ID**: `106` | **Conception**: May 1, 2026 | **EDD**: Feb 5, 2027 (Active gestation).
- **First Trimester Scan (GA 12.3w, Jul 10, 2026)**:
  - CRL: 59.0 mm | NT: 1.3 mm | Nasal Bone: Present
  - Serum Markers: PAPP-A 1.20 MoM, PlGF 65.0 pg/mL
  - Predicted 20w EFW Percentile: **55.0%** (Risk: 0.06, `LOW`).
- **Second Trimester Scan (GA 20.2w, Sep 4, 2026)**:
  - Actual EFW: 355 g | Actual EFW Percentile: **54.0%** (Variance: **-1.0%**)
  - Status: `NORMAL_ACTIVE` (Optimal growth trajectory).
- **Postnatal Records**: Intentionally **NULL** (No newborn, no NICU records; demonstrates handling of ongoing active cases).

