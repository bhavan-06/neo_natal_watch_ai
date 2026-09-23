import re

with open('frontend/app.jsx', 'r', encoding='utf-8') as f:
    content = f.read()

fallback_code = """// ─── Embedded Synthetic Clinical Data Store (for GitHub Pages Static Hosting) ──
const FALLBACK_PATIENTS = [
    { id: 'P-SYN-001', name: 'Sarah Jenkins', patient_code: 'SYN-001', date_of_birth: '1993-04-12', created_at: '2026-01-10T08:00:00Z' },
    { id: 'P-SYN-002', name: 'Baby Liam (Jessica Taylor)', patient_code: 'SYN-002', date_of_birth: '1991-08-23', created_at: '2026-01-12T09:30:00Z' },
    { id: 'P-SYN-003', name: 'Baby Emma (Rachel Adams)', patient_code: 'SYN-003', date_of_birth: '1995-11-04', created_at: '2026-01-14T11:15:00Z' },
    { id: 'P-SYN-004', name: 'Emily Davis', patient_code: 'SYN-004', date_of_birth: '1996-02-18', created_at: '2026-01-15T14:00:00Z' },
    { id: 'P-SYN-005', name: 'Baby Noah (Amanda Wilson)', patient_code: 'SYN-005', date_of_birth: '1990-07-29', created_at: '2026-01-18T10:45:00Z' },
    { id: 'P-SYN-006', name: 'Olivia Martinez', patient_code: 'SYN-006', date_of_birth: '1992-05-16', created_at: '2026-01-20T16:20:00Z' },
    { id: 'P-SYN-007', name: 'Baby Lucas (Megan White)', patient_code: 'SYN-007', date_of_birth: '1994-09-08', created_at: '2026-01-22T08:50:00Z' },
    { id: 'P-SYN-008', name: 'Baby Sophia (Lauren Harris)', patient_code: 'SYN-008', date_of_birth: '1989-12-30', created_at: '2026-01-25T13:10:00Z' },
    { id: 'P-SYN-009', name: 'Sophia Martinez', patient_code: 'SYN-009', date_of_birth: '1997-03-22', created_at: '2026-01-28T09:00:00Z' },
    { id: 'P-SYN-010', name: 'Isabella Clark', patient_code: 'SYN-010', date_of_birth: '1993-10-15', created_at: '2026-02-01T15:40:00Z' }
];

function generateMockVitals(patientId) {
    const isCrit = ['P-SYN-002', 'P-SYN-005', 'P-SYN-008'].includes(patientId);
    const list = [];
    const now = Date.now();
    const baseHR = isCrit ? 168 : 138;
    const baseSpO2 = isCrit ? 91 : 97;
    const baseRR = isCrit ? 62 : 42;
    const baseTemp = isCrit ? 37.8 : 36.9;

    for (let i = 59; i >= 0; i--) {
        const t = new Date(now - i * 60000);
        list.push({
            timestamp: t.toISOString(),
            heart_rate: Math.round(baseHR + (Math.sin(i / 3.5) * 6) + (Math.random() * 3 - 1.5)),
            spo2: Math.min(100, Math.round(baseSpO2 + (Math.cos(i / 4.2) * 2) + (Math.random() * 2 - 1))),
            respiratory_rate: Math.round(baseRR + (Math.sin(i / 5) * 4) + (Math.random() * 2 - 1)),
            temperature: +(baseTemp + (Math.cos(i / 7) * 0.15) + (Math.random() * 0.1 - 0.05)).toFixed(1)
        });
    }
    return list;
}

function getSyntheticFallback(endpoint, body) {
    if (endpoint === '/patients/') return FALLBACK_PATIENTS;
    if (endpoint === '/patients/stats/summary') return { total_patients: 10, active_pregnancies: 5, nicu_admissions: 5, active_alerts: 3 };
    if (endpoint === '/chat/') return { reply: 'Clinical AI Assistant: The patient telemetry displays consistent hemodynamic parameters. All multi-modal indicators are within expected operational parameters for clinical review.' };

    const parts = endpoint.split('/').filter(Boolean);
    if (parts[0] === 'patients' && parts[1]) {
        const pid = parts[1];
        const sub = parts[2];
        const isCrit = ['P-SYN-002', 'P-SYN-005', 'P-SYN-008'].includes(pid);
        const isNicu = ['P-SYN-002', 'P-SYN-003', 'P-SYN-005', 'P-SYN-007', 'P-SYN-008'].includes(pid);
        const pat = FALLBACK_PATIENTS.find(p => p.id === pid) || { id: pid, name: pid, date_of_birth: '1994-06-15' };

        if (!sub) return pat;
        if (sub === 'pregnancy') return [{ id: 1, pregnancy_status: 'ACTIVE', gestational_age: 34.2, edd: '2026-10-20' }];
        if (sub === 'maternal-profile') return [{ maternal_age: 31, bmi: 23.6, map_value: 86.5, chronic_hypertension: isCrit ? 1 : 0, diabetes: 0 }];
        if (sub === 'fetal-assessments') return [
            { assessment_date: '2026-01-15', gestational_age_weeks: 12.4, trimester: 1, efw_percentile: 48.0, crl: 62.0, nt: 1.4 },
            { assessment_date: '2026-03-20', gestational_age_weeks: 20.2, trimester: 2, efw_percentile: 46.5, crl: 154.0, nt: 1.8 }
        ];
        if (sub === 'labs') return [
            { test_date: '2026-01-16', papp_a: 1.15, plgf: 42.8, free_beta_hcg: 1.02, status: 'normal' }
        ];
        if (sub === 'doppler') return [{ gestational_age: 20.2, uterine_artery_pi: 0.92, uterine_artery_status: 'normal', umbilical_artery_status: 'normal' }];
        if (sub === 'predictions') return [{ prediction_type: 'PRENATAL_EFW', predicted_value: 48.2, risk_score: isCrit ? 0.78 : 0.18 }];
        if (sub === 'growth-analysis') return [{
            predicted_efw_percentile: 48.2, actual_efw_percentile: 46.5, growth_variance: 1.7,
            evaluation_status: isCrit ? 'MONITORED_DEVIATION' : 'NORMAL_GROWTH_TRAJECTORY',
            contributing_patterns: 'Adequate longitudinal percentile trajectory within safe physiological limits.'
        }];
        if (sub === 'doctor-reviews') return [{
            id: 1, clinician_id: 'Dr. E. Vance, MD', review_date: '2026-03-21',
            assessment: 'Clinical monitoring protocol active. Vitals and growth velocity consistent with care plan.',
            recommendations: 'Continue standard biometrics surveillance.'
        }];
        if (sub === 'prescriptions') return [{ id: 1, medication_name: 'Prenatal Multivitamin Complex', dosage: '1 tablet QD', start_date: '2026-01-10' }];
        if (sub === 'newborn') return isNicu ? [{ id: 1, name: pat.name.split(' ')[0], newborn_code: 'NB-' + pid, birth_date: '2026-03-01', gestational_age_at_birth: 33.5, birth_weight: 1850 }] : [];
        if (sub === 'nicu') return isNicu ? [{ id: 1, status: 'Active Surveillance', admission_date: '2026-03-01', admission_reason: isCrit ? 'Respiratory distress & prematurity' : 'Preterm observation' }] : [];
        if (sub === 'alerts') return isCrit ? [
            { id: 1, alert_type: 'Multi-Modal Vital Deterioration Flag', risk_score: 0.78, created_at: new Date(Date.now() - 15 * 60000).toISOString() }
        ] : [];
        if (sub === 'vitals') return generateMockVitals(pid);
        if (sub === 'maternal-vitals') return generateMockVitals(pid);
        if (sub === 'timeline') return [
            { type: 'pregnancy_start', details: 'Antenatal Intake Recorded', date: '2026-01-10' },
            { type: 'fetal_assessment', details: 'Trimester 1 Ultrasound Assessment', date: '2026-01-15' },
            { type: 'fetal_assessment', details: 'Trimester 2 Growth Anomaly Scan', date: '2026-03-20' },
            ...(isNicu ? [
                { type: 'birth', details: 'Preterm Delivery Recorded', date: '2026-03-01' },
                { type: 'nicu_admission', details: 'NICU Incubator Telemetry Initiated', date: '2026-03-01' }
            ] : [])
        ];
        if (sub === 'explain') return {
            top_features: [
                { feature: 'Heart Rate (Rolling Std)', value: isCrit ? 12.4 : 5.8, shap_value: isCrit ? 0.21 : -0.08 },
                { feature: 'Gestational Age (weeks)', value: 33.5, shap_value: isCrit ? 0.16 : -0.12 },
                { feature: 'Mean Arterial Pressure', value: 88.0, shap_value: 0.09 },
                { feature: 'PlGF Angiogenic Marker', value: 38.5, shap_value: -0.07 },
                { feature: 'SpO2 Oxygen (Rolling Min)', value: isCrit ? 90.2 : 96.5, shap_value: isCrit ? 0.14 : -0.06 }
            ],
            baseline_value: 0.185
        };
        if (sub === 'anomaly-explain') return {
            anomaly_score: isCrit ? 0.0842 : 0.0215,
            anomaly_label: isCrit ? 'ANOMALY' : 'NORMAL',
            reconstruction_error_by_feature: {
                heart_rate: isCrit ? 0.0384 : 0.0082,
                spo2: isCrit ? 0.0271 : 0.0054,
                respiratory_rate: isCrit ? 0.0125 : 0.0049,
                temperature: 0.0062
            }
        };
        if (sub === 'attention-explain') return {
            top_attention_steps: [
                { step_index: 29, time_label: 'T−0 min (Current)', attention_weight: 0.185 },
                { step_index: 28, time_label: 'T−1 min', attention_weight: 0.142 },
                { step_index: 27, time_label: 'T−2 min', attention_weight: 0.118 },
                { step_index: 26, time_label: 'T−3 min', attention_weight: 0.094 },
                { step_index: 25, time_label: 'T−4 min', attention_weight: 0.082 },
                { step_index: 20, time_label: 'T−9 min', attention_weight: 0.065 },
                { step_index: 15, time_label: 'T−14 min', attention_weight: 0.052 }
            ]
        };
    }
    return [];
}

async function apiGet(endpoint) {
    try {
        const r = await fetch(API + endpoint);
        if (r.ok) return await r.json();
    } catch (e) {
        // Fallback to embedded synthetic clinical data for static GitHub Pages hosting
    }
    return getSyntheticFallback(endpoint);
}

async function apiPost(endpoint, body) {
    try {
        const r = await fetch(API + endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body)
        });
        if (r.ok) return await r.json();
    } catch (e) {
        // Fallback
    }
    return getSyntheticFallback(endpoint, body);
}
"""

api_marker = ": 'http://localhost:8000/api/v1';"
if api_marker in content:
    idx = content.find(api_marker) + len(api_marker)
    content = content[:idx] + "\n\n" + fallback_code + "\n" + content[idx:]

# Replace fetch calls
content = re.sub(
    r"const res = await fetch\(`\$\{API\}/chat/`[\s\S]*?const data = await res\.json\(\);",
    "const data = await apiPost('/chat/', { message: msg, patient_id: patientId });",
    content
)

old_drawer = """        Promise.all([
            fetch(`${API}/patients/${patientId}`).then(r => r.json()),
            fetch(`${API}/patients/${patientId}/pregnancy`).then(r => r.json()),
            fetch(`${API}/patients/${patientId}/maternal-profile`).then(r => r.json()),
            fetch(`${API}/patients/${patientId}/fetal-assessments`).then(r => r.json()),
            fetch(`${API}/patients/${patientId}/labs`).then(r => r.json()),
            fetch(`${API}/patients/${patientId}/doppler`).then(r => r.json()),
            fetch(`${API}/patients/${patientId}/predictions`).then(r => r.json()),
            fetch(`${API}/patients/${patientId}/growth-analysis`).then(r => r.json()),
            fetch(`${API}/patients/${patientId}/doctor-reviews`).then(r => r.json()),
            fetch(`${API}/patients/${patientId}/prescriptions`).then(r => r.json()),
            fetch(`${API}/patients/${patientId}/newborn`).then(r => r.json()),
            fetch(`${API}/patients/${patientId}/nicu`).then(r => r.json()),
            fetch(`${API}/patients/${patientId}/alerts`).then(r => r.json()),
            fetch(`${API}/patients/${patientId}/vitals`).then(r => r.json()),
            fetch(`${API}/patients/${patientId}/maternal-vitals`).then(r => r.json()),
            fetch(`${API}/patients/${patientId}/timeline`).then(r => r.json()),
        ])"""

new_drawer = """        Promise.all([
            apiGet(`/patients/${patientId}`),
            apiGet(`/patients/${patientId}/pregnancy`),
            apiGet(`/patients/${patientId}/maternal-profile`),
            apiGet(`/patients/${patientId}/fetal-assessments`),
            apiGet(`/patients/${patientId}/labs`),
            apiGet(`/patients/${patientId}/doppler`),
            apiGet(`/patients/${patientId}/predictions`),
            apiGet(`/patients/${patientId}/growth-analysis`),
            apiGet(`/patients/${patientId}/doctor-reviews`),
            apiGet(`/patients/${patientId}/prescriptions`),
            apiGet(`/patients/${patientId}/newborn`),
            apiGet(`/patients/${patientId}/nicu`),
            apiGet(`/patients/${patientId}/alerts`),
            apiGet(`/patients/${patientId}/vitals`),
            apiGet(`/patients/${patientId}/maternal-vitals`),
            apiGet(`/patients/${patientId}/timeline`),
        ])"""

content = content.replace(old_drawer, new_drawer)

content = content.replace(
    "fetch(`${API}/patients/${patientId}/explain`).then(r => r.ok ? r.json() : null).then(setShapExplanation).catch(() => {});",
    "apiGet(`/patients/${patientId}/explain`).then(setShapExplanation).catch(() => {});"
)
content = content.replace(
    "fetch(`${API}/patients/${patientId}/anomaly-explain`).then(r => r.ok ? r.json() : null).then(setAeExplanation).catch(() => {});",
    "apiGet(`/patients/${patientId}/anomaly-explain`).then(setAeExplanation).catch(() => {});"
)
content = content.replace(
    "fetch(`${API}/patients/${patientId}/attention-explain`).then(r => r.ok ? r.json() : null).then(setAttnExplanation).catch(() => {});",
    "apiGet(`/patients/${patientId}/attention-explain`).then(setAttnExplanation).catch(() => {});"
)

content = content.replace(
    "fetch(`${API}/patients/`).then(r => r.json()).then(d => Array.isArray(d) && setPatients(d)).catch(() => {});",
    "apiGet('/patients/').then(d => Array.isArray(d) && setPatients(d)).catch(() => {});"
)
content = content.replace(
    "fetch(`${API}/patients/stats/summary`).then(r => r.json()).then(setStats).catch(() => {});",
    "apiGet('/patients/stats/summary').then(setStats).catch(() => {});"
)

with open('frontend/app.jsx', 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated frontend/app.jsx successfully!")

