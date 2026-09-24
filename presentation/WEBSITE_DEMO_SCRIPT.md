# NeoNatal Watch AI — Live Website Demonstration Script & Talking Points

Use this guide while sharing your screen or presenting the live website:
👉 **URL:** [https://bhavan-06.github.io/neo_natal_watch_ai/](https://bhavan-06.github.io/neo_natal_watch_ai/) (or your local `localhost:8000`)

---

## 🎯 Step 1: Landing on the Dashboard (Header & Overview)

### What to Point to on Screen:
1. Top navigation bar with the **NeoNatal Watch AI** title and heartbeat pulse icon.
2. The yellow **Safety Disclaimer Bar**: *"ACADEMIC PROTOTYPE — FOR CLINICAL DECISION SUPPORT & RESEARCH ONLY"*.
3. The top **KPI Stat Cards**:
   - **Total Patients** (10 monitored)
   - **Active Pregnancies** (5 prenatal surveillance)
   - **NICU Admissions** (5 high-acuity infants)
   - **Active Alerts** (3 priority warnings)
4. The **Dark Mode Toggle** (sun/moon icon on top right).

### What to Say to Evaluators:
> *"Here is the live NeoNatal Watch AI clinical interface. Notice immediately that the design follows strict healthcare ergonomics: we use a soft Slate palette with high-contrast typography that eliminates eye strain and complies with WCAG AAA accessibility."*
>
> *"At the very top, we prominently display our clinical governance disclaimer—clarifying that this platform is an academic decision-support tool designed to assist doctors, not replace clinical judgment."*
>
> *"The four metric cards give attending physicians instant situational awareness across both prenatal and neonatal wards."*

---

## 🎯 Step 2: Patient Triage & Priority Table

### What to Point to on Screen:
1. The **Patient Registry List** (showing patients `P-SYN-001` through `P-SYN-010`).
2. The color-coded **Risk Badges**:
   - **Red ("HIGH RISK")**: e.g., `P-SYN-002` (Baby Liam), `P-SYN-005` (Baby Noah).
   - **Amber ("WATCH")**: e.g., `P-SYN-003` (Baby Emma), `P-SYN-007` (Baby Lucas).
   - **Green ("LOW RISK / STABLE")**: e.g., `P-SYN-001` (Sarah Jenkins), `P-SYN-004` (Emily Davis).
3. The quick clinical indicators: Gestational Age, Patient ID, Bed number, and latest vital snapshot.

### What to Say to Evaluators:
> *"In a busy hospital, doctors cannot inspect every patient with equal urgency. Our dashboard automatically triages patients by priority."*
>
> *"Patients are ranked by their real-time multi-modal risk score. For instance, **Baby Liam (P-SYN-002)** is flagged as **HIGH RISK** because of concurrent oxygen desaturation and heart rate variability, immediately drawing the clinician's attention."*

---

## 🎯 Step 3: Deep Patient Inspection (The 7-Tab Drawer)

👉 **Action on Screen:** Click on **`P-SYN-002` (Baby Liam)** or **`P-SYN-005` (Baby Noah)** to slide open the comprehensive patient drawer.

### 🔹 Tab 1: Clinical Overview & Risk Breakdown
- **What to Show:** The composite Risk Score gauge (e.g., `0.84 HIGH`), along with the individual model score contributions:
  - `XGBoost Score: 0.88` (Weight: 35%)
  - `CNN-LSTM Score: 0.82` (Weight: 30%)
  - `Transformer Score: 0.85` (Weight: 20%)
  - `Autoencoder Anomaly Score: 0.78` (Weight: 15%)
- **What to Say:**
  > *"When we open Baby Liam's record, we don't just see a black-box number. We see the mathematical breakdown of our **calibrated 4-model ensemble**. All four independent algorithms agree that this infant is at critical risk."*

---

### 🔹 Tab 2: Prenatal & Maternal Record (Care Continuity)
- **What to Show:** Maternal demographics, Mean Arterial Pressure (MAP), Hadlock Ultrasound Biometry (BPD, HC, AC, FL), and Uterine Artery Doppler PI.
- **What to Say:**
  > *"This tab showcases our core innovation: **Care Continuity**. Here, the neonatologist can review the mother's prenatal trajectory.*
  >
  > *"We see maternal hypertension and an elevated Uterine Artery Doppler Pulsatility Index of 1.68 with bilateral diastolic notching, proving that the baby experienced placental insufficiency weeks before birth."*

---

### 🔹 Tab 3: Newborn Birth & NICU Admission Status
- **What to Show:** Gestational age at delivery (e.g., 29.4 weeks), birth weight (e.g., 1,120g), APGAR scores (5 at 1 min, 7 at 5 mins), and admission diagnosis.
- **What to Say:**
  > *"Here we see delivery metrics: very low birth weight and preterm delivery at 29 weeks, directly explaining the infant's respiratory vulnerability."*

---

### 🔹 Tab 4: Continuous Telemetry (Live Vitals Chart)
- **What to Show:** The multi-vital interactive **Chart.js graphs**:
  - Heart Rate curve (showing dips below 100 bpm bradycardia)
  - SpO2 curve (showing desaturation dips to 88-91%)
  - Respiratory Rate & Core Temperature curves
- **What to Say:**
  > *"Tab 4 displays our continuous NICU telemetry feed. The charts render 60-minute sliding windows of continuous physiological parameters. Doctors can hover over any time point to inspect exact measurements and identify acute trend changes."*

---

### 🔹 Tab 5: Multi-Modal Explainable AI (XAI) ⭐ *Most Important Tab*
- **What to Show:** 
  1. **SHAP Feature Attribution Bars**: Horizontal bar chart showing feature contributions (e.g., `SpO2_min: +38%`, `HR_std: +24%`).
  2. **Autoencoder Residuals**: Deviation per vital channel (SpO2 deviation vs HR deviation).
  3. **Transformer Attention Map**: Temporal heatmap highlighting the exact critical minutes.
- **What to Say:**
  > *"This is the core scientific strength of our project: **Tri-Modal Explainability**. We answer three questions for the doctor:"*
  > 1. *"**Which feature?** SHAP tells us the minimum SpO2 drop contributed +38% to the risk."*
  > 2. *"**Which organ channel?** The Autoencoder isolates oxygen saturation as the primary abnormal residual."*
  > 3. *"**When in time?** The Transformer attention heatmap pinpoints the critical 5-minute precursor window where the desaturation began."*
  > *"This eliminates alarm fatigue and gives clinicians immediate biological justification."*

---

### 🔹 Tab 6: Doctor Reviews & Prescriptions
- **What to Show:** Clinical assessment notes, attending physician findings, medication orders (e.g., Surfactant, Caffeine Citrate).
- **What to Say:**
  > *"Doctors can log clinical findings and prescribe treatments directly in this tab. Every review and alarm acknowledgment is saved with clinician timestamps into our relational database."*

---

### 🔹 Tab 7: Longitudinal Clinical Timeline
- **What to Show:** The chronological timeline linking Maternal First Trimester $\rightarrow$ Ultrasound $\rightarrow$ Delivery $\rightarrow$ NICU Admission $\rightarrow$ Current Alarms.
- **What to Say:**
  > *"Tab 7 unifies the entire life history of the patient on a single vertical timeline, ensuring that critical medical history is never lost across shift changes."*

---

## 🎯 Step 4: AI Clinical Assistant (Live Chatbot)

👉 **Action on Screen:** Click the **AI Assistant** icon in the bottom-right corner or on the patient drawer.

### What to Demonstrate:
- Type or show an inquiry:  
  💬 *"Summarize latest vitals and risk factors for Baby Liam."*
- Show the assistant's structured response detailing current vitals, elevated risk factors, and recommended monitoring protocol.

### What to Say to Evaluators:
> *"We also integrated an **Embedded Clinical AI Assistant**. Nurses and doctors can quickly ask questions in plain language without digging through medical charts. The assistant pulls verified records directly from the database to answer within seconds."*

---

## 🎯 Step 5: Admin Dashboard / Master Control

👉 **Action on Screen:** Click **"Admin View"** in the top navigation bar.

### What to Point to on Screen:
1. System telemetry health and WebSocket connection status.
2. Active ML model checkpoints (`xgboost_v1.json`, `cnn_lstm.pt`, `transformer.pt`, `autoencoder.pt`).
3. User role management (Physician, NICU Nurse, System Administrator) and audit logs.

### What to Say to Evaluators:
> *"The Admin View acts as the master control center for hospital IT and department heads. It verifies that all four machine learning models are active in memory, monitors streaming pipeline health, and enforces role-based clinical security."*

---

## 🎯 Step 6: Concluding the Website Walkthrough

### Final Closing Statement:
> *"To summarize: NeoNatal Watch AI provides a complete, clinician-first surveillance system. It unites prenatal history with high-acuity NICU telemetry, fuses four specialized AI models with sub-second latency, and provides transparent, tri-modal explainability to protect our most vulnerable patients.*
>
> *The entire system is live right now at **`bhavan-06.github.io/neo_natal_watch_ai`**, verified with 200 automated unit and integration tests. Thank you!"*
