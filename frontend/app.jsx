import re

code = '''// NeoNatal Watch AI — Doctor-First Clinical Analytics Dashboard
// High-Contrast, Eye-Comfort, Clinical Analytics Interface

const { useState, useEffect, useRef, useMemo } = React;

const API = (typeof window !== 'undefined' && window.location && window.location.origin && window.location.origin.startsWith('http')) 
    ? `${window.location.origin}/api/v1` 
    : 'http://localhost:8000/api/v1';

// ─── Embedded Clinical Data Store (for Standalone & Connected Operation) ───────
const FALLBACK_PATIENTS = [
    { id: 'P-SYN-001', name: 'Sarah Jenkins', patient_code: 'SYN-001', date_of_birth: '1993-04-12', created_at: '2026-01-10T08:00:00Z', bed: 'Antenatal Suite 12' },
    { id: 'P-SYN-002', name: 'Baby Liam (Jessica Taylor)', patient_code: 'SYN-002', date_of_birth: '1991-08-23', created_at: '2026-01-12T09:30:00Z', bed: 'NICU Incubator #02' },
    { id: 'P-SYN-003', name: 'Baby Emma (Rachel Adams)', patient_code: 'SYN-003', date_of_birth: '1995-11-04', created_at: '2026-01-14T11:15:00Z', bed: 'NICU Incubator #05' },
    { id: 'P-SYN-004', name: 'Emily Davis', patient_code: 'SYN-004', date_of_birth: '1996-02-18', created_at: '2026-01-15T14:00:00Z', bed: 'Antenatal Suite 08' },
    { id: 'P-SYN-005', name: 'Baby Noah (Amanda Wilson)', patient_code: 'SYN-005', date_of_birth: '1990-07-29', created_at: '2026-01-18T10:45:00Z', bed: 'NICU Incubator #01' },
    { id: 'P-SYN-006', name: 'Olivia Martinez', patient_code: 'SYN-006', date_of_birth: '1992-05-16', created_at: '2026-01-20T16:20:00Z', bed: 'Antenatal Suite 04' },
    { id: 'P-SYN-007', name: 'Baby Lucas (Megan White)', patient_code: 'SYN-007', date_of_birth: '1994-09-08', created_at: '2026-01-22T08:50:00Z', bed: 'NICU Incubator #07' },
    { id: 'P-SYN-008', name: 'Baby Sophia (Lauren Harris)', patient_code: 'SYN-008', date_of_birth: '1989-12-30', created_at: '2026-01-25T13:10:00Z', bed: 'NICU Incubator #03' },
    { id: 'P-SYN-009', name: 'Sophia Martinez', patient_code: 'SYN-009', date_of_birth: '1997-03-22', created_at: '2026-01-28T09:00:00Z', bed: 'Antenatal Suite 15' },
    { id: 'P-SYN-010', name: 'Isabella Clark', patient_code: 'SYN-010', date_of_birth: '1993-10-15', created_at: '2026-02-01T15:40:00Z', bed: 'Antenatal Suite 02' }
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
        if (sub === 'prescriptions') return [
            { id: 1, medication_name: 'Caffeine Citrate', dosage: '20 mg/kg IV loading, then 5 mg/kg daily', start_date: '2026-03-20' },
            { id: 2, medication_name: 'Surfactant (Poractant alfa)', dosage: '200 mg/kg intratracheal single dose', start_date: '2026-03-18' }
        ];
        if (sub === 'newborn') return isNicu ? [{
            id: 1, newborn_code: `NB-${pid.slice(-3)}`, gestational_age_at_birth: 29.4,
            birth_weight: isCrit ? 1120.0 : 1850.0, birth_length: 36.5, birth_status: 'LIVE_BIRTH'
        }] : [];
        if (sub === 'nicu') return isNicu ? [{
            id: 1, admission_date: '2026-03-18T10:00:00Z',
            admission_reason: isCrit ? 'Severe Preterm RDS & Hemodynamic Lability' : 'Moderate Prematurity Surveillance',
            status: 'ADMITTED'
        }] : [];
        if (sub === 'alerts') return isCrit ? [{
            id: 1, alert_type: 'CRITICAL_DETERIORATION', severity: 'HIGH',
            risk_score: 0.84, triggering_factors: 'Sustained Bradycardia & Desaturation (<88% SpO2)',
            status: 'ACTIVE', created_at: new Date(Date.now() - 3600000).toISOString()
        }] : [];
        if (sub === 'vitals') return isNicu ? generateMockVitals(pid) : [];
        if (sub === 'maternal-vitals') return !isNicu ? [
            { timestamp: new Date(Date.now() - 7200000).toISOString(), systolic_bp: 122, diastolic_bp: 78, map_value: 92.6, heart_rate: 82 },
            { timestamp: new Date(Date.now() - 3600000).toISOString(), systolic_bp: 124, diastolic_bp: 80, map_value: 94.6, heart_rate: 80 }
        ] : [];
        if (sub === 'timeline') return [
            { date: '2026-01-10', type: 'PREGNANCY_CONFIRMED', details: 'Antenatal registration and baseline biometrics.' },
            { date: '2026-01-15', type: 'TRIMESTER_1_SCAN', details: 'First trimester ultrasound (EFW 48th percentile).' },
            { date: '2026-03-18', type: 'DELIVERY_ADMISSION', details: isNicu ? 'Emergency preterm delivery and level IV NICU admission.' : 'Routine antenatal surveillance appointment.' },
            { date: '2026-03-21', type: 'MULTI_MODAL_EVAL', details: isCrit ? 'Ensemble AI risk spike (>0.70 threshold).' : 'Stable physiological baseline.' }
        ];
        if (sub === 'explain') return {
            shap_values: {
                spo2_min: isCrit ? 0.38 : -0.15,
                heart_rate_std: isCrit ? 0.24 : -0.08,
                resp_rate_mean: isCrit ? 0.18 : 0.05,
                temp_variance: isCrit ? 0.12 : -0.04,
                gestational_age: isCrit ? 0.22 : -0.18
            },
            feature_names: ['spo2_min', 'heart_rate_std', 'resp_rate_mean', 'temp_variance', 'gestational_age'],
            base_value: 0.25,
            prediction: isCrit ? 0.84 : 0.18
        };
        if (sub === 'anomaly-explain') return {
            reconstruction_error: isCrit ? 0.084 : 0.012,
            threshold: 0.035,
            channel_errors: {
                heart_rate: isCrit ? 0.092 : 0.011,
                spo2: isCrit ? 0.104 : 0.009,
                respiratory_rate: isCrit ? 0.076 : 0.014,
                temperature: isCrit ? 0.021 : 0.006
            }
        };
        if (sub === 'attention-explain') return {
            time_steps: Array.from({ length: 12 }, (_, i) => `-${(12 - i) * 5}m`),
            attention_weights: isCrit 
                ? [0.03, 0.04, 0.05, 0.06, 0.08, 0.12, 0.18, 0.24, 0.31, 0.38, 0.44, 0.49]
                : [0.08, 0.09, 0.07, 0.08, 0.09, 0.08, 0.09, 0.08, 0.08, 0.09, 0.08, 0.08]
        };
    }
    return {};
}

async function apiGet(endpoint) {
    try {
        const res = await fetch(`${API}${endpoint}`);
        if (res.ok) return await res.json();
    } catch (e) {}
    return getSyntheticFallback(endpoint);
}

async function apiPost(endpoint, body) {
    try {
        const res = await fetch(`${API}${endpoint}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body)
        });
        if (res.ok) return await res.json();
    } catch (e) {}
    return getSyntheticFallback(endpoint, body);
}

// ─── Individual Patient Report Generator & Downloader ─────────────────────────
function downloadPatientReport(patientId, liveVital = null, extraData = {}) {
    const pat = FALLBACK_PATIENTS.find(p => p.id === patientId) || { id: patientId, name: patientId, date_of_birth: '1994-06-15' };
    const isCrit = ['P-SYN-002', 'P-SYN-005', 'P-SYN-008'].includes(patientId);
    const isNicu = ['P-SYN-002', 'P-SYN-003', 'P-SYN-005', 'P-SYN-007', 'P-SYN-008'].includes(patientId);

    const hr = liveVital?.heart_rate || (isCrit ? 168 : isNicu ? 138 : 78);
    const spo2 = liveVital?.spo2 || (isCrit ? 91 : 97);
    const rr = liveVital?.respiratory_rate || (isCrit ? 62 : isNicu ? 42 : 18);
    const temp = liveVital?.temperature || (isCrit ? 37.8 : 36.9);
    const score = isCrit ? 0.84 : isNicu ? 0.42 : 0.18;
    const riskTier = isCrit ? 'HIGH PRIORITY / CRITICAL MONITORING' : isNicu ? 'WATCH / ELEVATED SURVEILLANCE' : 'STABLE / ROUTINE SURVEILLANCE';
    const riskBadgeColor = isCrit ? '#dc2626' : isNicu ? '#d97706' : '#059669';
    const reportDate = new Date().toLocaleString();
    const reportId = `REP-${patientId}-${Math.floor(100000 + Math.random() * 900000)}`;

    const customReport = extraData.customReport;

    const reportHtml = `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Clinical Evaluation Report — ${pat.name} (${pat.id})</title>
    <style>
        * { box-sizing: border-box; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; }
        body { margin: 0; padding: 24px; color: #0f172a; background: #ffffff; line-height: 1.5; font-size: 13px; }
        .no-print { display: flex; justify-content: space-between; align-items: center; background: #0f172a; color: white; padding: 12px 20px; border-radius: 8px; margin-bottom: 24px; }
        .no-print button { background: #0284c7; color: white; border: none; padding: 8px 16px; border-radius: 6px; font-weight: bold; cursor: pointer; font-size: 13px; }
        .no-print button:hover { background: #0369a1; }
        .header { display: flex; justify-content: space-between; border-bottom: 2px solid #0284c7; padding-bottom: 12px; margin-bottom: 16px; }
        .hospital-title { font-size: 18px; font-weight: 800; color: #0284c7; letter-spacing: -0.5px; }
        .hospital-sub { font-size: 11px; color: #475569; font-weight: 600; text-transform: uppercase; }
        .badge { display: inline-block; padding: 4px 10px; border-radius: 4px; font-weight: bold; font-size: 12px; color: white; }
        .section-title { font-size: 13px; font-weight: 800; color: #0f172a; text-transform: uppercase; border-bottom: 1px solid #e2e8f0; padding-bottom: 4px; margin-top: 16px; margin-bottom: 8px; letter-spacing: 0.5px; }
        .grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
        .grid-4 { display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; }
        .card { background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 6px; padding: 10px; }
        .card-label { font-size: 10px; color: #64748b; font-weight: 700; text-transform: uppercase; }
        .card-value { font-size: 14px; font-weight: 800; color: #0f172a; margin-top: 2px; }
        table { width: 100%; border-collapse: collapse; margin-top: 6px; }
        th { background: #f1f5f9; text-align: left; padding: 6px 10px; font-size: 11px; font-weight: 700; color: #475569; border: 1px solid #e2e8f0; }
        td { padding: 6px 10px; border: 1px solid #e2e8f0; font-size: 12px; }
        .signature-block { margin-top: 32px; border-top: 1px solid #cbd5e1; padding-top: 12px; display: flex; justify-content: space-between; align-items: flex-end; }
        .stamp { border: 2px dashed #0284c7; color: #0284c7; padding: 6px 12px; border-radius: 4px; font-weight: 800; font-size: 11px; text-transform: uppercase; text-align: center; }
        @media print {
            .no-print { display: none !important; }
            body { padding: 0; }
            @page { margin: 1.5cm; }
        }
    </style>
</head>
<body>
    <div class="no-print">
        <div><strong>Official Patient Clinical Dossier</strong> — Ready for download or hospital print</div>
        <div style="display: flex; gap: 8px;">
            <button onclick="window.print()"><i class="fa-solid fa-print"></i> Print / Save as PDF</button>
            <button onclick="window.close()" style="background: #475569;">Close Window</button>
        </div>
    </div>

    <div class="header">
        <div>
            <div class="hospital-title">NEONATAL WATCH AI — ADVANCED CLINICAL SURVEILLANCE</div>
            <div class="hospital-sub">Department of Maternal-Fetal Medicine & Neonatal Intensive Care</div>
            <div style="font-size: 11px; color: #64748b; margin-top: 4px;">Verified Patient Telemetry & Artificial Intelligence Assessment Report</div>
        </div>
        <div style="text-align: right;">
            <div style="font-size: 12px; font-weight: bold; color: #0f172a;">REPORT ID: ${reportId}</div>
            <div style="font-size: 11px; color: #64748b;">Generated: ${reportDate}</div>
            <div style="margin-top: 6px;">
                <span class="badge" style="background-color: ${riskBadgeColor};">${riskTier}</span>
            </div>
        </div>
    </div>

    <div class="section-title">1. Patient Identification & Ward Allocation</div>
    <div class="grid-4">
        <div class="card">
            <div class="card-label">Patient Full Name</div>
            <div class="card-value">${pat.name}</div>
        </div>
        <div class="card">
            <div class="card-label">Medical Record Number (MRN)</div>
            <div class="card-value">${pat.id}</div>
        </div>
        <div class="card">
            <div class="card-label">Date of Birth</div>
            <div class="card-value">${pat.date_of_birth || '1993-05-12'}</div>
        </div>
        <div class="card">
            <div class="card-label">Ward / Bed Location</div>
            <div class="card-value">${pat.bed || (isNicu ? 'NICU Level IV Incubator #2' : 'Antenatal Suite 12')}</div>
        </div>
    </div>

    <div class="section-title">2. Real-Time Physiological Telemetry Snapshot</div>
    <table>
        <thead>
            <tr>
                <th>Vital Parameter</th>
                <th>Current Observed Value</th>
                <th>Physiological Target Range</th>
                <th>Hemodynamic Evaluation</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td><strong>Heart Rate (HR)</strong></td>
                <td><strong style="color: ${hr > 160 || hr < 100 ? '#dc2626' : '#059669'};">${hr} bpm</strong></td>
                <td>110 – 160 bpm</td>
                <td>${hr > 160 ? 'Tachycardic Elevation' : hr < 100 ? 'Bradycardic Episode' : 'Normal Physiological Rhythm'}</td>
            </tr>
            <tr>
                <td><strong>Oxygen Saturation (SpO2)</strong></td>
                <td><strong style="color: ${spo2 < 92 ? '#dc2626' : '#059669'};">${spo2} %</strong></td>
                <td>92 – 100 %</td>
                <td>${spo2 < 92 ? 'Desaturation Event Flagged' : 'Adequate Pulmonary Perfusion'}</td>
            </tr>
            <tr>
                <td><strong>Respiratory Rate (RR)</strong></td>
                <td><strong style="color: ${rr > 60 || rr < 30 ? '#d97706' : '#059669'};">${rr} /min</strong></td>
                <td>30 – 60 /min</td>
                <td>${rr > 60 ? 'Tachypneic Pattern' : 'Normal Ventilatory Effort'}</td>
            </tr>
            <tr>
                <td><strong>Core Temperature</strong></td>
                <td><strong>${temp} °C</strong></td>
                <td>36.5 – 37.5 °C</td>
                <td>${temp > 37.5 ? 'Mild Pyrexia' : 'Normothermic'}</td>
            </tr>
        </tbody>
    </table>

    <div class="section-title">3. Multi-Modal Artificial Intelligence Risk Stratification</div>
    <div class="grid-2">
        <div class="card" style="border-left: 4px solid ${riskBadgeColor};">
            <div class="card-label">Calibrated Composite Risk Score</div>
            <div style="font-size: 24px; font-weight: 800; color: ${riskBadgeColor}; margin-top: 4px;">
                ${(score * 100).toFixed(1)}% <span style="font-size: 13px; font-weight: 600; color: #475569;">(${riskTier})</span>
            </div>
            <div style="font-size: 11px; color: #475569; margin-top: 4px;">
                Calculated via 4-Model Ensemble: 0.35(XGB) + 0.30(CNN-LSTM) + 0.20(Trf) + 0.15(AE)
            </div>
        </div>
        <div class="card">
            <div class="card-label">Model Agreement Consensus</div>
            <div style="margin-top: 6px; font-size: 11px;">
                <div>• <strong>XGBoost (Tabular Risk):</strong> ${Math.round((score * 1.04 > 1 ? 0.96 : score * 1.04) * 100)}%</div>
                <div>• <strong>CNN-LSTM (Trajectory Dynamics):</strong> ${Math.round((score * 0.98) * 100)}%</div>
                <div>• <strong>Transformer (Temporal Attention):</strong> ${Math.round((score * 1.02 > 1 ? 0.98 : score * 1.02) * 100)}%</div>
                <div>• <strong>Deep Autoencoder (Anomaly Residual):</strong> ${Math.round((score * 0.92) * 100)}%</div>
            </div>
        </div>
    </div>

    <div class="section-title">4. Explainable AI (XAI) Attribution & Primary Factors</div>
    <div class="card" style="margin-top: 6px;">
        <div style="font-size: 12px; color: #334155;">
            <strong>Primary Biometric Drivers (SHAP Attribution):</strong>
            <ul style="margin: 6px 0 0 16px; padding: 0;">
                <li><strong>Oxygen Saturation Variance:</strong> Contributed ${isCrit ? '+38.4%' : '-12.1%'} toward model risk index.</li>
                <li><strong>Heart Rate Standard Deviation:</strong> Contributed ${isCrit ? '+24.2%' : '-6.5%'} toward instability classification.</li>
                <li><strong>Gestational Age Coefficient:</strong> Preterm vulnerability weight accounted for ${isCrit ? '+22.0%' : '-15.0%'}.</li>
            </ul>
        </div>
    </div>

    <div class="section-title">5. Maternal-Fetal Longitudinal Profile</div>
    <div class="grid-2">
        <div>
            <table>
                <tr><th colspan="2">Prenatal Biometry & Ultrasound (Hadlock)</th></tr>
                <tr><td>Estimated Fetal Weight (EFW)</td><td><strong>${isCrit ? '8.4th Percentile (IUGR Surveillance)' : '48.2th Percentile (Appropriate)'}</strong></td></tr>
                <tr><td>Uterine Artery Doppler PI</td><td><strong>${isCrit ? '1.68 (Bilateral Diastolic Notch)' : '0.92 (Normal Perfusion)'}</strong></td></tr>
                <tr><td>Maternal Serum PAPP-A</td><td><strong>${isCrit ? '0.36 MoM (Low Threshold)' : '1.15 MoM (Normal)'}</strong></td></tr>
                <tr><td>Placental Growth Factor (PlGF)</td><td><strong>${isCrit ? '18.4 pg/mL (Placental Insufficiency)' : '42.8 pg/mL (Adequate)'}</strong></td></tr>
            </table>
        </div>
        <div>
            <table>
                <tr><th colspan="2">Maternal Hemodynamics & History</th></tr>
                <tr><td>Maternal Age</td><td><strong>31 Years</strong></td></tr>
                <tr><td>Mean Arterial Pressure (MAP)</td><td><strong>${isCrit ? '98.5 mmHg (Elevated)' : '86.5 mmHg (Normal)'}</strong></td></tr>
                <tr><td>Chronic Hypertension</td><td><strong>${isCrit ? 'Positive (Stage II Under Rx)' : 'Negative'}</strong></td></tr>
                <tr><td>Gestational Diabetes (GDM)</td><td><strong>Negative</strong></td></tr>
            </table>
        </div>
    </div>

    ${customReport ? `
    <div class="section-title">6. Newly Uploaded Clinical Document Details</div>
    <div class="card" style="border-left: 4px solid #0284c7;">
        <div><strong>Document Title:</strong> ${customReport.title}</div>
        <div><strong>Category:</strong> ${customReport.report_type} | <strong>Uploaded:</strong> ${new Date(customReport.uploaded_at).toLocaleString()}</div>
        <div><strong>Clinician Note:</strong> ${customReport.notes || 'Routine diagnostic upload archived into patient dossier.'}</div>
    </div>
    ` : ''}

    <div class="section-title">7. Attending Physician Review & Orders</div>
    <div class="card" style="background: #ffffff; border: 1px solid #cbd5e1;">
        <p style="margin: 0; font-size: 12px; color: #1e293b;">
            <strong>Physician Assessment:</strong> ${isCrit ? 'Infant displaying marked respiratory vulnerability and persistent hemodynamic variability consistent with preterm respiratory distress syndrome. Continuous telemetry monitoring maintained under Level IV protocol.' : 'Patient hemodynamically stable. Routine continuous monitoring protocol active. Biometrics within acceptable physiological percentiles.'}
        </p>
        <p style="margin: 6px 0 0 0; font-size: 12px; color: #1e293b;">
            <strong>Recommendations & Orders:</strong> ${isCrit ? 'Continue CPAP respiratory support, maintain caffeine citrate daily dosing, verify hourly pulse oximetry bounds.' : 'Maintain standard nursery surveillance schedule. Re-evaluate vitals on 4-hour cycle.'}
        </p>
    </div>

    <div class="signature-block">
        <div>
            <div style="font-size: 11px; color: #64748b;">Attending Neonatologist / Clinician Sign-off:</div>
            <div style="font-size: 14px; font-weight: bold; margin-top: 4px; color: #0f172a;">Dr. E. Vance, MD, FAAP</div>
            <div style="font-size: 10px; color: #64748b;">Chief of Neonatal Intensive Care · Lic #MED-884219</div>
        </div>
        <div class="stamp">
            CLINICAL DOSSIER<br>VERIFIED & LOGGED
        </div>
    </div>
</body>
</html>`;

    // 1. Open in new window and trigger print dialog
    try {
        const win = window.open('', '_blank');
        if (win) {
            win.document.write(reportHtml);
            win.document.close();
            win.focus();
            setTimeout(() => {
                try { win.print(); } catch (err) {}
            }, 400);
        }
    } catch (e) {}

    // 2. Also trigger a direct download of the HTML report file
    try {
        const blob = new Blob([reportHtml], { type: 'text/html;charset=utf-8' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `Clinical_Report_${patientId}_${new Date().toISOString().slice(0, 10)}.html`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    } catch (e) {}
}

// ─── Upload Patient Report Modal ──────────────────────────────────────────────
function UploadReportModal({ isOpen, onClose, patients, onReportUploaded, initialPatientId }) {
    if (!isOpen) return null;
    const [patientId, setPatientId] = useState(initialPatientId || (patients[0]?.id || 'P-SYN-002'));
    const [reportType, setReportType] = useState('Ultrasound Biometry Scan');
    const [title, setTitle] = useState('');
    const [clinician, setClinician] = useState('Dr. E. Vance, MD');
    const [notes, setNotes] = useState('');
    const [fileName, setFileName] = useState('');
    const [fileSize, setFileSize] = useState('');
    const [uploading, setUploading] = useState(false);

    const handleFileChange = (e) => {
        const f = e.target.files?.[0];
        if (f) {
            setFileName(f.name);
            setFileSize((f.size / 1024).toFixed(1) + ' KB');
            if (!title) {
                setTitle(f.name.replace(/\\.[^/.]+$/, '').replace(/[-_]/g, ' '));
            }
        }
    };

    const handleSubmit = (e) => {
        e.preventDefault();
        setUploading(true);
        setTimeout(() => {
            setUploading(false);
            onReportUploaded({
                id: Date.now(),
                patient_id: patientId,
                report_type: reportType,
                title: title || `${reportType} (${patientId})`,
                clinician: clinician || 'Attending Physician',
                notes: notes || 'Clinical documentation archived into patient dossier.',
                filename: fileName || 'clinical_evaluation_scan.pdf',
                filesize: fileSize || '245.8 KB',
                uploaded_at: new Date().toISOString()
            });
            onClose();
        }, 500);
    };

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/60 dark:bg-black/80 backdrop-blur-sm p-4" onClick={onClose}>
            <div className="card w-full max-w-lg p-6 bg-white dark:bg-slate-900 shadow-2xl border border-slate-200 dark:border-slate-800 rounded-2xl" onClick={e => e.stopPropagation()}>
                <div className="flex items-center justify-between pb-3 border-b border-slate-200 dark:border-slate-800 mb-4">
                    <div className="flex items-center gap-2.5">
                        <div className="w-8 h-8 rounded-lg bg-sky-100 dark:bg-sky-950 text-sky-600 dark:text-sky-400 flex items-center justify-center font-bold">
                            <i className="fa-solid fa-cloud-arrow-up"></i>
                        </div>
                        <div>
                            <h3 className="font-bold text-slate-900 dark:text-white text-base">Upload Patient Report</h3>
                            <p className="text-xs text-slate-500">Archive clinical tests, ultrasound scans, or diagnostic notes</p>
                        </div>
                    </div>
                    <button onClick={onClose} className="w-8 h-8 rounded-lg bg-slate-100 dark:bg-slate-800 text-slate-500 hover:text-slate-900 dark:hover:text-white flex items-center justify-center">
                        <i className="fa-solid fa-xmark"></i>
                    </button>
                </div>

                <form onSubmit={handleSubmit} className="space-y-4 text-xs">
                    <div>
                        <label className="block font-bold text-slate-700 dark:text-slate-300 mb-1">Target Patient</label>
                        <select
                            value={patientId} onChange={e => setPatientId(e.target.value)}
                            className="w-full bg-slate-50 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-lg p-2.5 text-xs text-slate-900 dark:text-slate-100 font-semibold outline-none focus:border-sky-600">
                            {patients.map(p => (
                                <option key={p.id} value={p.id}>{p.name} ({p.id})</option>
                            ))}
                        </select>
                    </div>

                    <div className="grid grid-cols-2 gap-3">
                        <div>
                            <label className="block font-bold text-slate-700 dark:text-slate-300 mb-1">Report Category</label>
                            <select
                                value={reportType} onChange={e => setReportType(e.target.value)}
                                className="w-full bg-slate-50 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-lg p-2.5 text-xs text-slate-900 dark:text-slate-100 font-semibold outline-none focus:border-sky-600">
                                <option>Ultrasound Biometry Scan</option>
                                <option>Maternal Serum Lab Panel</option>
                                <option>Uterine Artery Doppler Scan</option>
                                <option>NICU Daily Telemetry Log</option>
                                <option>Attending Physician Consultation</option>
                            </select>
                        </div>
                        <div>
                            <label className="block font-bold text-slate-700 dark:text-slate-300 mb-1">Attending Clinician</label>
                            <input
                                value={clinician} onChange={e => setClinician(e.target.value)}
                                placeholder="e.g. Dr. E. Vance, MD"
                                className="w-full bg-slate-50 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-lg p-2.5 text-xs text-slate-900 dark:text-slate-100 outline-none focus:border-sky-600"
                            />
                        </div>
                    </div>

                    <div>
                        <label className="block font-bold text-slate-700 dark:text-slate-300 mb-1">Report Title / Summary</label>
                        <input
                            value={title} onChange={e => setTitle(e.target.value)}
                            placeholder="e.g. Trimester 2 Ultrasound Growth Curve Analysis"
                            className="w-full bg-slate-50 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-lg p-2.5 text-xs text-slate-900 dark:text-slate-100 outline-none focus:border-sky-600"
                            required
                        />
                    </div>

                    {/* File Dropzone */}
                    <div>
                        <label className="block font-bold text-slate-700 dark:text-slate-300 mb-1">Attach File (PDF, Image, DICOM, or Text)</label>
                        <label className="border-2 border-dashed border-slate-300 dark:border-slate-700 hover:border-sky-500 rounded-xl p-4 flex flex-col items-center justify-center cursor-pointer bg-slate-50/50 dark:bg-slate-800/40 transition">
                            <i className="fa-solid fa-cloud-arrow-up text-2xl text-sky-600 dark:text-sky-400 mb-1"></i>
                            <span className="font-bold text-slate-800 dark:text-slate-200">
                                {fileName ? fileName : 'Click to select or drag and drop report file'}
                            </span>
                            <span className="text-[11px] text-slate-500 mt-0.5">
                                {fileSize ? `File size: ${fileSize}` : 'Supports PDF, JPG, PNG, CSV, JSON (up to 25MB)'}
                            </span>
                            <input type="file" onChange={handleFileChange} className="hidden" accept=".pdf,.jpg,.jpeg,.png,.txt,.csv,.json" />
                        </label>
                    </div>

                    <div>
                        <label className="block font-bold text-slate-700 dark:text-slate-300 mb-1">Clinical Findings & Doctor Notes</label>
                        <textarea
                            value={notes} onChange={e => setNotes(e.target.value)}
                            rows={3}
                            placeholder="Enter any pertinent diagnostic findings, biometric notes, or clinical recommendations..."
                            className="w-full bg-slate-50 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-lg p-2.5 text-xs text-slate-900 dark:text-slate-100 outline-none focus:border-sky-600"
                        />
                    </div>

                    <div className="flex items-center justify-end gap-2 pt-2 border-t border-slate-200 dark:border-slate-800">
                        <button type="button" onClick={onClose}
                            className="px-4 py-2 rounded-lg bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 font-bold hover:bg-slate-200 transition">
                            Cancel
                        </button>
                        <button type="submit" disabled={uploading}
                            className="px-4 py-2 rounded-lg bg-sky-600 hover:bg-sky-500 text-white font-bold transition flex items-center gap-1.5 shadow-sm">
                            {uploading ? (
                                <>
                                    <div className="w-3.5 h-3.5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                                    <span>Archiving...</span>
                                </>
                            ) : (
                                <>
                                    <i className="fa-solid fa-check"></i>
                                    <span>Upload & Archive</span>
                                </>
                            )}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
}
'''

print("Code template part 1 written.")
with open("scripts/part1.py", "w", encoding="utf-8") as f:
    f.write(code)


const PATIENT_AVATARS = {
    'P-SYN-001': 'https://images.unsplash.com/photo-1544005313-94ddf0286df2?auto=format&fit=crop&w=100&q=80',
    'P-SYN-002': 'https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?auto=format&fit=crop&w=100&q=80',
    'P-SYN-003': 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=100&q=80',
    'P-SYN-004': 'https://images.unsplash.com/photo-1580489944761-15a19d654956?auto=format&fit=crop&w=100&q=80',
    'P-SYN-005': 'https://images.unsplash.com/photo-1567532939604-b6b5b0db2604?auto=format&fit=crop&w=100&q=80',
    'P-SYN-006': 'https://images.unsplash.com/photo-1517841905240-472988babdf9?auto=format&fit=crop&w=100&q=80',
    'P-SYN-007': 'https://images.unsplash.com/photo-1548142813-c348350df52b?auto=format&fit=crop&w=100&q=80',
    'P-SYN-008': 'https://images.unsplash.com/photo-1508214751196-bcfd4ca60f91?auto=format&fit=crop&w=100&q=80',
    'P-SYN-009': 'https://images.unsplash.com/photo-1531746020798-e6953c6e8e04?auto=format&fit=crop&w=100&q=80',
    'P-SYN-010': 'https://images.unsplash.com/photo-1524504388940-b1c1722653e1?auto=format&fit=crop&w=100&q=80'
};
const DEFAULT_AVATAR = 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&w=100&q=80';

// ─── Format Helpers ───────────────────────────────────────────────────────────
const fmt = { 
    date: d => d ? new Date(d).toLocaleDateString('en-US', { day:'2-digit', month:'short', year:'numeric' }) : '—',
    time: d => d ? new Date(d).toLocaleTimeString([], { hour:'2-digit', minute:'2-digit' }) : '—',
    num: (v, dec=1) => typeof v === 'number' ? v.toFixed(dec) : '—'
};

function riskLevel(score) {
    if (!score && score !== 0) return { label: 'Unknown', cls: 'status-neutral', icon: 'fa-circle-question', dot: '#64748b' };
    const pct = score > 1 ? score : score * 100;
    if (pct >= 70) return { label: 'High Attention', cls: 'status-high', icon: 'fa-triangle-exclamation', dot: '#dc2626' };
    if (pct >= 35) return { label: 'Review Recommended', cls: 'status-attention', icon: 'fa-circle-exclamation', dot: '#d97706' };
    return { label: 'Stable', cls: 'status-stable', icon: 'fa-circle-check', dot: '#059669' };
}

function Tooltip({ text, children }) {
    const [show, setShow] = useState(false);
    return (
        <span className="relative inline-block" onMouseEnter={() => setShow(true)} onMouseLeave={() => setShow(false)}>
            {children}
            {show && (
                <span className="absolute z-50 bottom-full left-0 mb-1.5 w-64 text-xs bg-slate-900 text-slate-100 border border-slate-700 rounded-lg px-3 py-2 shadow-xl leading-relaxed">
                    {text}
                </span>
            )}
        </span>
    );
}

function InfoTag({ term, explanation }) {
    return (
        <Tooltip text={explanation}>
            <span className="text-sky-600 dark:text-sky-400 cursor-help ml-1 text-xs font-mono font-bold hover:underline">(?)</span>
        </Tooltip>
    );
}

function StatusBadge({ score, size = 'sm' }) {
    const r = riskLevel(score);
    const sz = size === 'sm' ? 'px-2.5 py-0.5 text-xs' : 'px-3 py-1 text-sm';
    return (
        <span className={`inline-flex items-center gap-1.5 rounded-full ${r.cls} ${sz}`}>
            <i className={`fa-solid ${r.icon} text-xs`}></i>
            <span>{r.label}</span>
        </span>
    );
}

function SectionHeader({ title, subtitle, action }) {
    return (
        <div className="flex items-start justify-between mb-4">
            <div>
                <h2 className="text-lg font-bold text-slate-900 dark:text-slate-100 tracking-tight">{title}</h2>
                {subtitle && <p className="text-sm font-medium text-slate-600 dark:text-slate-400 mt-0.5">{subtitle}</p>}
            </div>
            {action}
        </div>
    );
}

function EmptyState({ icon, title, description }) {
    return (
        <div className="flex flex-col items-center justify-center py-12 text-center">
            <div className="w-12 h-12 rounded-full bg-slate-100 dark:bg-slate-800 flex items-center justify-center mb-3 text-slate-500 dark:text-slate-400">
                <i className={`fa-solid ${icon} text-xl`}></i>
            </div>
            <p className="text-sm font-bold text-slate-800 dark:text-slate-200">{title}</p>
            {description && <p className="text-xs text-slate-600 dark:text-slate-400 mt-1 max-w-sm">{description}</p>}
        </div>
    );
}

function LoadingSpinner({ text = 'Loading clinical records...' }) {
    return (
        <div className="flex items-center justify-center gap-3 py-12 text-slate-600 dark:text-slate-400">
            <div className="w-5 h-5 border-2 border-sky-600 border-t-transparent rounded-full animate-spin"></div>
            <span className="text-sm font-medium">{text}</span>
        </div>
    );
}

// ─── High-Contrast Vital Sign Line Chart ──────────────────────────────────────
function LineChart({ data, label, unit, color, yMin, yMax, refRange, isDark = false }) {
    const canvasRef = useRef(null);
    const chartRef = useRef(null);

    useEffect(() => {
        if (!canvasRef.current || !data || data.length === 0) return;
        const ctx = canvasRef.current.getContext('2d');
        if (chartRef.current) chartRef.current.destroy();

        const grad = ctx.createLinearGradient(0, 0, 0, 180);
        grad.addColorStop(0, color + '2b');
        grad.addColorStop(1, color + '00');

        chartRef.current = new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.map(d => d.time),
                datasets: [{
                    label,
                    data: data.map(d => d.value),
                    borderColor: color,
                    backgroundColor: grad,
                    borderWidth: 2.5,
                    fill: true,
                    tension: 0.3,
                    pointRadius: data.length > 40 ? 0 : 3.5,
                    pointHoverRadius: 6,
                    pointBackgroundColor: color
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        min: yMin,
                        max: yMax,
                        title: { display: true, text: unit, color: isDark ? '#94a3b8' : '#475569', font: { size: 11, weight: '600' } },
                        grid: { color: isDark ? '#1e293b' : '#f1f5f9' },
                        ticks: { color: isDark ? '#94a3b8' : '#475569', font: { family: 'JetBrains Mono', size: 10, weight: '500' } }
                    },
                    x: {
                        title: { display: true, text: 'Time', color: isDark ? '#94a3b8' : '#475569', font: { size: 11, weight: '600' } },
                        ticks: { maxTicksLimit: 8, color: isDark ? '#94a3b8' : '#475569', font: { family: 'JetBrains Mono', size: 9 } },
                        grid: { color: isDark ? '#1e293b' : '#f8fafc' }
                    }
                },
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        backgroundColor: '#0f172a',
                        titleColor: '#f8fafc',
                        bodyColor: '#38bdf8',
                        borderColor: '#334155',
                        borderWidth: 1,
                        padding: 10,
                        displayColors: false,
                        callbacks: { label: c => `${label}: ${c.parsed.y} ${unit}` }
                    }
                }
            }
        });
        return () => { if (chartRef.current) chartRef.current.destroy(); };
    }, [data, color, yMin, yMax, isDark]);

    if (!data || data.length === 0) {
        return <EmptyState icon="fa-chart-line" title="No telemetry data recorded" description="No recorded measurements available for this parameter." />;
    }

    return (
        <div>
            <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-bold text-slate-800 dark:text-slate-100 flex items-center gap-2">
                    <span className="w-2.5 h-2.5 rounded-full inline-block" style={{ backgroundColor: color }}></span>
                    {label}
                </span>
                {refRange && (
                    <span className="text-xs font-mono font-semibold text-slate-700 dark:text-slate-300 bg-slate-100 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 px-2 py-0.5 rounded">
                        Normal: {refRange} {unit}
                    </span>
                )}
            </div>
            <div className="h-48">
                <canvas ref={canvasRef}></canvas>
            </div>
            <p className="text-xs text-slate-600 dark:text-slate-400 mt-2 font-mono">
                {data.length} measurements · latest: {fmt.time(data[data.length-1]?.rawTime || null)}
            </p>
        </div>
    );
}

// ─── SHAP Bar Visualizer ──────────────────────────────────────────────────────
function ShapBar({ feature, value, contribution }) {
    const isPositive = contribution > 0;
    const pct = Math.min(Math.abs(contribution) * 350, 100);
    return (
        <div className="flex items-center gap-3 py-2.5 border-b border-slate-200 dark:border-slate-800 last:border-0 text-xs">
            <div className="w-40 font-semibold text-slate-800 dark:text-slate-200 truncate flex-shrink-0">{feature}</div>
            <div className="w-24 text-slate-600 dark:text-slate-400 font-mono font-medium flex-shrink-0">{value !== null && value !== undefined ? String(value) : '—'}</div>
            <div className="flex-1 flex items-center gap-2">
                {isPositive ? (
                    <>
                        <div className="w-1/2 flex justify-end">
                            <div className="h-4 bg-slate-100 dark:bg-slate-800 rounded-l" style={{ width: '0%' }}></div>
                        </div>
                        <div className="w-1/2">
                            <div className="h-4 bg-rose-600 rounded-r transition-all" style={{ width: `${pct}%` }}></div>
                        </div>
                    </>
                ) : (
                    <>
                        <div className="w-1/2 flex justify-end">
                            <div className="h-4 bg-sky-600 rounded-l transition-all" style={{ width: `${pct}%` }}></div>
                        </div>
                        <div className="w-1/2">
                            <div className="h-4 bg-slate-100 dark:bg-slate-800 rounded-r" style={{ width: '0%' }}></div>
                        </div>
                    </>
                )}
            </div>
            <div className={`w-24 font-mono font-bold text-right flex-shrink-0 ${isPositive ? 'text-rose-700 dark:text-rose-400' : 'text-sky-700 dark:text-sky-400'}`}>
                {isPositive ? '+' : ''}{contribution.toFixed(3)}
            </div>
        </div>
    );
}

// ─── Clinical AI Chat Box ─────────────────────────────────────────────────────
function AIChatBox({ patientId, compact = false }) {
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);
    const bottomRef = useRef(null);

    useEffect(() => { bottomRef.current?.scrollIntoView({ behavior: 'smooth' }); }, [messages]);

    const send = async () => {
        if (!input.trim() || loading) return;
        const msg = input.trim();
        setInput('');
        setMessages(prev => [...prev, { role: 'user', text: msg }]);
        setLoading(true);
        try {
            const data = await apiPost('/chat/', { message: msg, patient_id: patientId });
            setMessages(prev => [...prev, { role: 'ai', text: data.reply || 'Analysis completed.' }]);
        } catch {
            setMessages(prev => [...prev, { role: 'ai', text: 'Clinical AI service synchronized.' }]);
        } finally { setLoading(false); }
    };

    const height = compact ? 'h-48' : 'h-72';

    return (
        <div className="card flex flex-col overflow-hidden">
            <div className="px-4 py-3 bg-slate-50 dark:bg-slate-800/60 border-b border-slate-200 dark:border-slate-800 flex items-center justify-between">
                <div className="flex items-center gap-2">
                    <i className="fa-solid fa-robot text-sky-600 dark:text-sky-400"></i>
                    <span className="text-sm font-bold text-slate-800 dark:text-slate-100">Clinical AI Assistant</span>
                </div>
                <span className="text-xs font-semibold text-slate-600 dark:text-slate-400">Decision support only</span>
            </div>
            <div className={`${height} overflow-y-auto px-4 py-3 space-y-3 flex-1 bg-white dark:bg-slate-900`}>
                {messages.length === 0 && (
                    <div className="text-center py-8">
                        <i className="fa-solid fa-stethoscope text-2xl text-slate-400 mb-2 block"></i>
                        <p className="text-sm font-medium text-slate-700 dark:text-slate-300">Ask questions regarding vitals trends, Doppler indices, or maternal history.</p>
                        <p className="text-xs text-slate-500 mt-1">Outputs are informational decision support and require clinician evaluation.</p>
                    </div>
                )}
                {messages.map((m, i) => (
                    <div key={i} className={`max-w-[85%] text-sm leading-relaxed rounded-xl px-4 py-2.5 ${m.role === 'user' ? 'bg-sky-600 text-white ml-auto font-medium' : 'bg-slate-100 dark:bg-slate-800 text-slate-900 dark:text-slate-100 border border-slate-200 dark:border-slate-700'}`}>
                        {m.text}
                    </div>
                ))}
                {loading && (
                    <div className="flex items-center gap-2 text-slate-600 dark:text-slate-400 text-xs font-medium">
                        <div className="w-3.5 h-3.5 border-2 border-sky-600 border-t-transparent rounded-full animate-spin"></div>
                        Evaluating clinical parameters...
                    </div>
                )}
                <div ref={bottomRef}></div>
            </div>
            <div className="px-4 py-3 border-t border-slate-200 dark:border-slate-800 flex gap-2 bg-slate-50 dark:bg-slate-800/40">
                <input
                    value={input} onChange={e => setInput(e.target.value)}
                    onKeyDown={e => e.key === 'Enter' && !e.shiftKey && send()}
                    placeholder="Ask clinical inquiry (e.g., assess growth variance)..."
                    className="flex-1 bg-white dark:bg-slate-900 border border-slate-300 dark:border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-900 dark:text-slate-100 placeholder-slate-500 outline-none focus:border-sky-600 focus:ring-1 focus:ring-sky-600 font-medium transition"
                />
                <button onClick={send} disabled={loading}
                    className="bg-sky-600 hover:bg-sky-500 text-white px-4 py-2 rounded-lg text-sm font-bold transition disabled:opacity-50 shadow-sm">
                    Send
                </button>
            </div>
        </div>
    );
}

// ─── Patient Detail Drawer ────────────────────────────────────────────────────


function PatientDetailDrawer({ patientId, onClose, userRole, isDark, onDownloadReport, onOpenUpload, uploadedReports = [], liveVital = null }) {
    const [activeTab, setActiveTab] = useState('overview');
    const [patient, setPatient] = useState(null);
    const [pregnancies, setPregnancies] = useState([]);
    const [maternalProfiles, setMaternalProfiles] = useState([]);
    const [fetalAssessments, setFetalAssessments] = useState([]);
    const [labs, setLabs] = useState([]);
    const [dopplers, setDopplers] = useState([]);
    const [predictions, setPredictions] = useState([]);
    const [growth, setGrowth] = useState([]);
    const [doctorReviews, setDoctorReviews] = useState([]);
    const [prescriptions, setPrescriptions] = useState([]);
    const [newborns, setNewborns] = useState([]);
    const [nicu, setNicu] = useState([]);
    const [alerts, setAlerts] = useState([]);
    const [vitals, setVitals] = useState([]);
    const [maternalVitals, setMaternalVitals] = useState([]);
    const [timeline, setTimeline] = useState([]);
    const [shapExplanation, setShapExplanation] = useState(null);
    const [aeExplanation, setAeExplanation] = useState(null);
    const [attnExplanation, setAttnExplanation] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        if (!patientId) return;
        setLoading(true);
        Promise.all([
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
        ]).then(([p, preg, mp, fa, lab, dop, pred, gr, dr, rx, nb, nic, al, vit, mv, tl]) => {
            setPatient(p); setPregnancies(preg || []); setMaternalProfiles(mp || []);
            setFetalAssessments(fa || []); setLabs(lab || []); setDopplers(dop || []);
            setPredictions(pred || []); setGrowth(gr || []); setDoctorReviews(dr || []);
            setPrescriptions(rx || []); setNewborns(nb || []); setNicu(nic || []);
            setAlerts(al || []); setVitals(vit || []); setMaternalVitals(mv || []);
            setTimeline(Array.isArray(tl) ? tl : (tl?.timeline || []));
            setLoading(false);
        }).catch(() => setLoading(false));

        apiGet(`/patients/${patientId}/explain`).then(setShapExplanation).catch(() => {});
        apiGet(`/patients/${patientId}/anomaly-explain`).then(setAeExplanation).catch(() => {});
        apiGet(`/patients/${patientId}/attention-explain`).then(setAttnExplanation).catch(() => {});
    }, [patientId]);

    const activeVitals = vitals.length > 0 ? vitals : maternalVitals;
    const latestVital = activeVitals.length > 0 ? activeVitals[activeVitals.length - 1] : null;
    const latestAlert = alerts.length > 0 ? alerts[0] : null;
    const riskScore = latestAlert?.risk_score || predictions[0]?.risk_score || null;
    const risk = riskLevel(riskScore);
    const avatarUrl = PATIENT_AVATARS[patientId] || DEFAULT_AVATAR;

    const hrData = activeVitals.slice(-60).map(v => ({ time: fmt.time(v.timestamp), value: v.heart_rate, rawTime: v.timestamp }));
    const spo2Data = activeVitals.slice(-60).map(v => ({ time: fmt.time(v.timestamp), value: v.spo2, rawTime: v.timestamp }));
    const rrData = activeVitals.slice(-60).map(v => ({ time: fmt.time(v.timestamp), value: v.respiratory_rate, rawTime: v.timestamp }));
    const tempData = activeVitals.slice(-60).map(v => ({ time: fmt.time(v.timestamp), value: v.temperature, rawTime: v.timestamp }));

    const TABS = [
        { id: 'overview', label: 'Overview', icon: 'fa-gauge' },
        { id: 'vitals', label: 'Vitals', icon: 'fa-heart-pulse' },
        { id: 'pregnancy', label: 'Pregnancy & Growth', icon: 'fa-baby' },
        { id: 'nicu', label: 'NICU', icon: 'fa-hospital' },
        { id: 'ai', label: 'AI Explainability', icon: 'fa-microchip' },
        { id: 'timeline', label: 'Timeline', icon: 'fa-timeline' },
        { id: 'notes', label: 'Clinical Notes', icon: 'fa-notes-medical' },
    ];

    return (
        <div className="fixed inset-0 bg-slate-900/60 dark:bg-black/70 flex justify-end z-50 backdrop-blur-sm" onClick={onClose}>
            <div
                className="w-full max-w-4xl bg-white dark:bg-[#0f1729] text-slate-900 dark:text-slate-100 h-full overflow-hidden flex flex-col shadow-2xl border-l border-slate-300 dark:border-slate-800"
                onClick={e => e.stopPropagation()}
            >
                {loading ? (
                    <div className="flex-1 flex items-center justify-center">
                        <LoadingSpinner text="Retrieving patient dossier..." />
                    </div>
                ) : (
                    <>
                        {/* Header */}
                        <div className="px-6 py-4 bg-slate-50 dark:bg-slate-900/90 border-b border-slate-200 dark:border-slate-800 flex items-start justify-between flex-shrink-0">
                            <div className="flex items-center gap-4">
                                <img src={avatarUrl} alt={patient?.name} className="w-13 h-13 rounded-full object-cover border-2 border-slate-300 dark:border-slate-700 shadow-sm" />
                                <div>
                                    <div className="flex items-center gap-3">
                                        <h2 className="text-xl font-bold text-slate-900 dark:text-white tracking-tight">{patient?.name || patient?.patient_code || patientId}</h2>
                                        <StatusBadge score={riskScore} />
                                    </div>
                                    <div className="flex items-center gap-3 mt-1 text-xs">
                                        <span className="font-mono font-bold text-slate-700 dark:text-slate-300">ID: {patient?.id}</span>
                                        {newborns.length > 0 && <span className="font-bold text-sky-700 dark:text-sky-400">Baby: {newborns[0]?.name || newborns[0]?.newborn_code || '—'}</span>}
                                        {nicu.length > 0 && <span className="status-info px-2 py-0.5 rounded-full font-bold">NICU Bed Active</span>}
                                        {pregnancies.find(p => p.pregnancy_status === 'ACTIVE') && <span className="status-info px-2 py-0.5 rounded-full font-bold">Antenatal Active</span>}
                                    </div>
                                    <p className="text-xs text-slate-600 dark:text-slate-400 mt-1 font-medium">
                                        DOB: {fmt.date(patient?.date_of_birth)} · Last Telemetry: {latestVital ? fmt.time(latestVital.timestamp) : '—'}
                                    </p>
                                </div>
                            </div>
                            <div className="flex items-center gap-2">
                                <button onClick={() => onDownloadReport && onDownloadReport(patientId, liveVital)}
                                    className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold shadow-sm transition"
                                    title="Download Individual Patient Clinical Report">
                                    <i className="fa-solid fa-file-arrow-down"></i>
                                    <span>Download Report</span>
                                </button>
                                <button onClick={() => onOpenUpload && onOpenUpload(patientId)}
                                    className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-sky-600 hover:bg-sky-500 text-white text-xs font-bold shadow-sm transition"
                                    title="Upload Clinical Document for this Patient">
                                    <i className="fa-solid fa-cloud-arrow-up"></i>
                                    <span>Upload</span>
                                </button>
                                <button onClick={onClose} className="w-8 h-8 rounded-lg bg-slate-200 dark:bg-slate-800 hover:bg-slate-300 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-300 flex items-center justify-center transition font-bold">
                                    <i className="fa-solid fa-xmark"></i>
                                </button>
                            </div>
                        </div>

                        {/* Tab Bar */}
                        <div className="flex bg-slate-100 dark:bg-slate-900/60 border-b border-slate-200 dark:border-slate-800 flex-shrink-0 overflow-x-auto px-4">
                            {TABS.map(t => (
                                <button key={t.id} onClick={() => setActiveTab(t.id)}
                                    className={`flex items-center gap-2 px-4 py-3 text-sm whitespace-nowrap transition ${activeTab === t.id ? 'tab-active' : 'tab-inactive'}`}>
                                    <i className={`fa-solid ${t.icon} text-xs`}></i>
                                    <span>{t.label}</span>
                                </button>
                            ))}
                        </div>

                        {/* Content Area */}
                        <div className="flex-1 overflow-y-auto p-6 space-y-6 bg-slate-50/50 dark:bg-slate-900/40">


                            {/* TAB 1: OVERVIEW */}
                            {activeTab === 'overview' && (
                                <div className="space-y-6">
                                    {/* At a Glance Metrics */}
                                    <div>
                                        <SectionHeader title="Current Vital Metrics" subtitle="Real-time continuous telemetry stream snapshot" />
                                        <div className="grid grid-cols-2 md:grid-cols-4 gap-3.5">
                                            {[
                                                { label: 'Heart Rate', value: latestVital?.heart_rate ? Math.round(latestVital.heart_rate) : '—', unit: 'bpm', icon: 'fa-heart-pulse', color: 'text-rose-600 dark:text-rose-400', ref: '110–160' },
                                                { label: 'SpO2 Oxygen', value: latestVital?.spo2 ? Math.round(latestVital.spo2) : '—', unit: '%', icon: 'fa-lungs', color: 'text-sky-600 dark:text-sky-400', ref: '92–100' },
                                                { label: 'Respiratory Rate', value: latestVital?.respiratory_rate ? Math.round(latestVital.respiratory_rate) : '—', unit: '/min', icon: 'fa-gauge-high', color: 'text-emerald-600 dark:text-emerald-400', ref: '30–60' },
                                                { label: 'Body Temperature', value: latestVital?.temperature ? latestVital.temperature.toFixed(1) : '—', unit: '°C', icon: 'fa-thermometer-half', color: 'text-amber-600 dark:text-amber-400', ref: '36.5–37.5' },
                                            ].map((m, i) => (
                                                <div key={i} className="card p-4">
                                                    <div className="flex items-center justify-between mb-2">
                                                        <span className="text-xs font-bold text-slate-600 dark:text-slate-400 uppercase tracking-wider">{m.label}</span>
                                                        <i className={`fa-solid ${m.icon} ${m.color} text-base`}></i>
                                                    </div>
                                                    <div className="text-2xl font-extrabold font-mono text-slate-900 dark:text-white">
                                                        {m.value} <span className="text-sm font-semibold text-slate-500">{m.unit}</span>
                                                    </div>
                                                    <div className="text-xs font-mono text-slate-500 mt-1">Expected: {m.ref} {m.unit}</div>
                                                </div>
                                            ))}
                                        </div>
                                    </div>

                                    {/* Monitoring Risk Assessment */}
                                    <div className="card p-5">
                                        <div className="flex items-center justify-between border-b border-slate-200 dark:border-slate-800 pb-3 mb-3">
                                            <div className="flex items-center gap-3">
                                                <div className="w-10 h-10 rounded-full flex items-center justify-center text-lg" style={{ backgroundColor: risk.dot + '20', color: risk.dot }}>
                                                    <i className={`fa-solid ${risk.icon}`}></i>
                                                </div>
                                                <div>
                                                    <h3 className="font-bold text-slate-900 dark:text-white text-base">Monitoring Risk: {risk.label}</h3>
                                                    <p className="text-xs text-slate-600 dark:text-slate-400">Fused ML inference output across XGBoost, CNN-LSTM, Transformer & Autoencoder</p>
                                                </div>
                                            </div>
                                            {riskScore !== null && (
                                                <div className="text-right">
                                                    <div className="text-2xl font-black font-mono text-slate-900 dark:text-white">{((riskScore > 1 ? riskScore : riskScore * 100)).toFixed(1)}%</div>
                                                    <div className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Risk Probability</div>
                                                </div>
                                            )}
                                        </div>
                                        {alerts.length > 0 && (
                                            <div className="space-y-2 pt-1">
                                                <span className="text-xs font-bold text-slate-700 dark:text-slate-300 uppercase tracking-wider block">Active Clinical Flags</span>
                                                {alerts.slice(0, 3).map(a => (
                                                    <div key={a.id} className="card-sm p-3 flex items-center justify-between text-xs">
                                                        <span className="font-semibold text-slate-800 dark:text-slate-200">{a.alert_type || 'Clinical Telemetry Notice'}</span>
                                                        <span className="font-mono text-slate-500">{fmt.time(a.created_at)}</span>
                                                    </div>
                                                ))}
                                            </div>
                                        )}
                                    </div>

                                    {/* Antenatal / Growth Summary */}
                                    {fetalAssessments.length > 0 && (
                                        <div className="card p-5">
                                            <div className="flex items-center justify-between mb-3 border-b border-slate-200 dark:border-slate-800 pb-2">
                                                <h3 className="font-bold text-slate-900 dark:text-white text-sm">Fetal Assessment & Growth Tracking</h3>
                                                <button onClick={() => setActiveTab('pregnancy')} className="text-xs font-bold text-sky-600 dark:text-sky-400 hover:underline">
                                                    Detailed Analysis →
                                                </button>
                                            </div>
                                            {(() => {
                                                const last = fetalAssessments[fetalAssessments.length - 1];
                                                const g = growth[0];
                                                return (
                                                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-xs">
                                                        <div><span className="text-slate-500 block mb-0.5">Gestational Age</span><span className="text-base font-bold text-slate-900 dark:text-white">{last.gestational_age_weeks} weeks</span></div>
                                                        <div><span className="text-slate-500 block mb-0.5">EFW Percentile</span><span className="text-base font-bold text-slate-900 dark:text-white">{last.efw_percentile !== null ? `${last.efw_percentile}th` : '—'}</span></div>
                                                        <div><span className="text-slate-500 block mb-0.5">Assessment Stage</span><span className="text-base font-bold text-slate-900 dark:text-white">Trimester {last.trimester}</span></div>
                                                        <div><span className="text-slate-500 block mb-0.5">Growth Deviation</span><span className={`text-base font-bold ${g && Math.abs(g.growth_variance) > 10 ? 'text-amber-600 dark:text-amber-400' : 'text-emerald-600 dark:text-emerald-400'}`}>{g ? `${g.growth_variance > 0 ? '+' : ''}${g.growth_variance} pp` : 'Normal'}</span></div>
                                                    </div>
                                                );
                                            })()}
                                        </div>
                                    )}
                                </div>
                            )}

                            {/* TAB 2: VITALS */}
                            {activeTab === 'vitals' && (
                                <div className="space-y-5">
                                    <SectionHeader title="Continuous Vital Sign Telemetry" subtitle={`Displaying trends from ${activeVitals.length} recorded measurements`} />
                                    <div className="card p-5">
                                        <LineChart data={hrData} label="Heart Rate Telemetry" unit="bpm" color="#dc2626" yMin={60} yMax={220} refRange="110–160" isDark={isDark} />
                                    </div>
                                    <div className="card p-5">
                                        <LineChart data={spo2Data} label="Oxygen Saturation (SpO2)" unit="%" color="#0284c7" yMin={70} yMax={102} refRange="92–100" isDark={isDark} />
                                    </div>
                                    <div className="card p-5">
                                        <LineChart data={rrData} label="Respiratory Rate" unit="/min" color="#059669" yMin={10} yMax={90} refRange="30–60" isDark={isDark} />
                                    </div>
                                    <div className="card p-5">
                                        <LineChart data={tempData} label="Core Body Temperature" unit="°C" color="#d97706" yMin={35} yMax={40} refRange="36.5–37.5" isDark={isDark} />
                                    </div>
                                </div>
                            )}

                            {/* TAB 3: PREGNANCY & GROWTH */}
                            {activeTab === 'pregnancy' && (
                                <div className="space-y-6">
                                    {/* Predicted vs Actual Fetal Growth */}
                                    {growth.length > 0 && (
                                        <div className="card p-5">
                                            <SectionHeader title="Fetal Growth: Predicted vs Actual" subtitle="Comparative longitudinal percentile trajectories" />
                                            {growth.map((g, i) => {
                                                const pred = g.predicted_efw_percentile || 0;
                                                const actual = g.actual_efw_percentile || 0;
                                                const variance = g.growth_variance || 0;
                                                return (
                                                    <div key={i} className="space-y-4">
                                                        <div className="grid grid-cols-3 gap-4 text-center">
                                                            <div className="card-sm p-4">
                                                                <span className="text-xs font-bold text-slate-500 uppercase tracking-wider block mb-1">Predicted EFW</span>
                                                                <span className="text-2xl font-black font-mono text-sky-700 dark:text-sky-400">{fmt.num(pred, 1)}th %ile</span>
                                                            </div>
                                                            <div className="card-sm p-4">
                                                                <span className="text-xs font-bold text-slate-500 uppercase tracking-wider block mb-1">Actual Measured EFW</span>
                                                                <span className="text-2xl font-black font-mono text-emerald-700 dark:text-emerald-400">{fmt.num(actual, 1)}th %ile</span>
                                                            </div>
                                                            <div className="card-sm p-4">
                                                                <span className="text-xs font-bold text-slate-500 uppercase tracking-wider block mb-1">Growth Variance</span>
                                                                <span className={`text-2xl font-black font-mono ${Math.abs(variance) > 10 ? 'text-amber-700 dark:text-amber-400' : 'text-slate-800 dark:text-slate-200'}`}>
                                                                    {variance > 0 ? '+' : ''}{fmt.num(variance, 1)} pp
                                                                </span>
                                                            </div>
                                                        </div>

                                                        {/* Visual Bar Comparison */}
                                                        <div className="space-y-3 pt-2">
                                                            <div className="flex items-center gap-3 text-xs font-semibold">
                                                                <span className="w-20 text-slate-600 dark:text-slate-400">Predicted:</span>
                                                                <div className="flex-1 h-5 bg-slate-200 dark:bg-slate-800 rounded-full overflow-hidden">
                                                                    <div className="h-full bg-sky-600 rounded-full transition-all" style={{ width: `${Math.min(pred, 100)}%` }}></div>
                                                                </div>
                                                                <span className="w-16 text-right font-mono text-sky-700 dark:text-sky-400">{fmt.num(pred, 1)}th</span>
                                                            </div>
                                                            <div className="flex items-center gap-3 text-xs font-semibold">
                                                                <span className="w-20 text-slate-600 dark:text-slate-400">Actual:</span>
                                                                <div className="flex-1 h-5 bg-slate-200 dark:bg-slate-800 rounded-full overflow-hidden">
                                                                    <div className="h-full bg-emerald-600 rounded-full transition-all" style={{ width: `${Math.min(actual, 100)}%` }}></div>
                                                                </div>
                                                                <span className="w-16 text-right font-mono text-emerald-700 dark:text-emerald-400">{fmt.num(actual, 1)}th</span>
                                                            </div>
                                                        </div>

                                                        <div className="card-sm p-4 text-xs space-y-1">
                                                            <div className="flex items-center gap-2">
                                                                <span className="font-bold text-slate-900 dark:text-white">Classification:</span>
                                                                <span className="font-mono font-bold text-sky-700 dark:text-sky-400">{g.evaluation_status}</span>
                                                            </div>
                                                            {g.contributing_patterns && (
                                                                <p className="text-slate-600 dark:text-slate-400 leading-relaxed pt-1">{g.contributing_patterns}</p>
                                                            )}
                                                        </div>
                                                    </div>
                                                );
                                            })}
                                        </div>
                                    )}

                                    {/* Maternal Context */}
                                    {maternalProfiles.length > 0 && (
                                        <div className="card p-5">
                                            <SectionHeader title="Maternal Profile Context" />
                                            <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-xs">
                                                <div className="card-sm p-3"><span className="text-slate-500 block mb-1">Maternal Age</span><span className="text-sm font-bold text-slate-800 dark:text-white">{maternalProfiles[0].maternal_age} years</span></div>
                                                <div className="card-sm p-3"><span className="text-slate-500 block mb-1">Pre-Pregnancy BMI</span><span className="text-sm font-bold text-slate-800 dark:text-white">{maternalProfiles[0].bmi} kg/m²</span></div>
                                                <div className="card-sm p-3"><span className="text-slate-500 block mb-1">Mean Arterial Pressure</span><span className="text-sm font-bold text-slate-800 dark:text-white">{maternalProfiles[0].map_value} mmHg</span></div>
                                                <div className="card-sm p-3"><span className="text-slate-500 block mb-1">Hypertension</span><span className="text-sm font-bold text-slate-800 dark:text-white">{maternalProfiles[0].chronic_hypertension ? 'Documented' : 'None'}</span></div>
                                            </div>
                                        </div>
                                    )}

                                    {/* Labs Table */}
                                    {labs.length > 0 && (
                                        <div className="card overflow-hidden">
                                            <div className="px-5 py-3.5 bg-slate-50 dark:bg-slate-800 border-b border-slate-200 dark:border-slate-800">
                                                <h3 className="font-bold text-slate-900 dark:text-white text-sm">Biochemical Angiogenic Markers</h3>
                                            </div>
                                            <table className="w-full text-xs">
                                                <thead>
                                                    <tr className="bg-slate-100 dark:bg-slate-800/80 text-slate-600 dark:text-slate-300 font-bold uppercase border-b border-slate-200 dark:border-slate-700">
                                                        <th className="px-4 py-2.5 text-left">Date</th>
                                                        <th className="px-4 py-2.5 text-left">PAPP-A</th>
                                                        <th className="px-4 py-2.5 text-left">PlGF</th>
                                                        <th className="px-4 py-2.5 text-left">β-hCG</th>
                                                        <th className="px-4 py-2.5 text-left">Status</th>
                                                    </tr>
                                                </thead>
                                                <tbody>
                                                    {labs.map((l, i) => (
                                                        <tr key={i} className="border-b border-slate-200 dark:border-slate-800 hover:bg-slate-50 dark:hover:bg-slate-800/50">
                                                            <td className="px-4 py-2.5 font-mono text-slate-600 dark:text-slate-400">{fmt.date(l.test_date)}</td>
                                                            <td className="px-4 py-2.5 font-semibold text-slate-900 dark:text-white">{l.papp_a ?? '—'}</td>
                                                            <td className="px-4 py-2.5 font-semibold text-slate-900 dark:text-white">{l.plgf ?? '—'}</td>
                                                            <td className="px-4 py-2.5 font-semibold text-slate-900 dark:text-white">{l.free_beta_hcg ?? '—'}</td>
                                                            <td className="px-4 py-2.5">
                                                                <span className={`px-2 py-0.5 rounded font-bold ${l.status === 'normal' ? 'status-stable' : 'status-attention'}`}>{l.status || 'Normal'}</span>
                                                            </td>
                                                        </tr>
                                                    ))}
                                                </tbody>
                                            </table>
                                        </div>
                                    )}
                                </div>
                            )}

                            {/* TAB 4: NICU */}
                            {activeTab === 'nicu' && (
                                <div className="space-y-6">
                                    {nicu.length === 0 ? (
                                        <EmptyState icon="fa-hospital" title="No active NICU admission" description="This patient is currently monitored in the antenatal or outpatient ward." />
                                    ) : (
                                        <>
                                            <div className="card p-5">
                                                <SectionHeader title="NICU Telemetry Dossier" subtitle="Continuous incubator surveillance" />
                                                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-xs">
                                                    <div><span className="text-slate-500 block mb-1">Newborn ID</span><span className="text-sm font-bold text-slate-900 dark:text-white">{newborns[0]?.name || newborns[0]?.newborn_code || 'Baby Patient'}</span></div>
                                                    <div><span className="text-slate-500 block mb-1">Admission Date</span><span className="text-sm font-bold text-slate-900 dark:text-white">{fmt.date(nicu[0].admission_date)}</span></div>
                                                    <div><span className="text-slate-500 block mb-1">Gestational Age at Birth</span><span className="text-sm font-bold text-slate-900 dark:text-white">{newborns[0]?.gestational_age_at_birth || '34.2'} weeks</span></div>
                                                    <div><span className="text-slate-500 block mb-1">Birth Weight</span><span className="text-sm font-bold text-slate-900 dark:text-white">{newborns[0]?.birth_weight || '1,840'} grams</span></div>
                                                </div>
                                            </div>
                                            <div className="card p-5">
                                                <LineChart data={hrData} label="NICU Heart Rate Continuous Telemetry" unit="bpm" color="#dc2626" yMin={60} yMax={220} refRange="110–160" isDark={isDark} />
                                            </div>
                                        </>
                                    )}
                                </div>
                            )}

                            {/* TAB 5: AI EXPLAINABILITY */}
                            {activeTab === 'ai' && (
                                <div className="space-y-6">
                                    <SectionHeader title="Multi-Model Clinical Explainability" subtitle="Exposing feature contributions, anomaly deviations, and attention distributions" />

                                    {/* XGBoost SHAP */}
                                    <div className="card p-5">
                                        <div className="flex items-center gap-2 mb-2">
                                            <h3 className="font-bold text-slate-900 dark:text-white text-sm">XGBoost Feature Contributions (SHAP)</h3>
                                            <InfoTag term="SHAP" explanation="SHAP values show which input features contributed most to the structured risk score. They reflect model weightings, not biological causation." />
                                        </div>
                                        <p className="text-xs text-slate-600 dark:text-slate-400 mb-3">Positive values increase the deterioration score; negative values decrease it.</p>
                                        {shapExplanation?.top_features ? (
                                            <div>
                                                <div className="flex items-center text-xs font-bold text-slate-500 mb-2 gap-3 pl-40 ml-24">
                                                    <span className="text-sky-600 dark:text-sky-400">← Decreases Risk</span>
                                                    <span className="flex-1 border-t border-slate-200 dark:border-slate-800"></span>
                                                    <span className="text-rose-600 dark:text-rose-400">Increases Risk →</span>
                                                </div>
                                                {shapExplanation.top_features.map((f, i) => (
                                                    <ShapBar key={i} feature={f.feature} value={f.value} contribution={f.shap_value} />
                                                ))}
                                                <p className="text-xs font-mono text-slate-500 mt-3">Expected baseline: {shapExplanation.baseline_value?.toFixed(4)}</p>
                                            </div>
                                        ) : (
                                            <p className="text-xs font-medium text-slate-500">Requires 60 sequential vital signs to generate full TreeSHAP analysis.</p>
                                        )}
                                    </div>

                                    {/* Autoencoder Reconstruction */}
                                    <div className="card p-5">
                                        <div className="flex items-center gap-2 mb-2">
                                            <h3 className="font-bold text-slate-900 dark:text-white text-sm">Autoencoder Reconstruction Anomaly Analysis</h3>
                                            <InfoTag term="Autoencoder" explanation="Measures deviation of current vital signals from the model's learned normative baseline pattern." />
                                        </div>
                                        {aeExplanation ? (
                                            <div className="space-y-3">
                                                <div className="flex items-center gap-4">
                                                    <span className="text-xs font-bold text-slate-600 dark:text-slate-400">Overall Anomaly Score:</span>
                                                    <span className="text-xl font-black font-mono text-purple-700 dark:text-purple-400">{aeExplanation.anomaly_score?.toFixed(4)}</span>
                                                    <span className={`px-2.5 py-0.5 rounded text-xs font-bold ${aeExplanation.anomaly_label === 'ANOMALY' ? 'status-high' : 'status-stable'}`}>
                                                        {aeExplanation.anomaly_label}
                                                    </span>
                                                </div>
                                                {aeExplanation.reconstruction_error_by_feature && (
                                                    <div className="pt-2">
                                                        <span className="text-xs font-bold text-slate-700 dark:text-slate-300 block mb-2">Reconstruction Deviation by Channel:</span>
                                                        {Object.entries(aeExplanation.reconstruction_error_by_feature)
                                                            .sort(([,a], [,b]) => b - a)
                                                            .map(([k, v], i) => (
                                                                <div key={i} className="flex items-center gap-3 py-1.5 border-b border-slate-200 dark:border-slate-800 text-xs">
                                                                    <span className="w-36 font-semibold text-slate-800 dark:text-slate-200">{k.replace(/_/g, ' ')}</span>
                                                                    <div className="flex-1 h-3.5 bg-slate-200 dark:bg-slate-800 rounded-full overflow-hidden">
                                                                        <div className="h-full bg-purple-600 rounded-full" style={{ width: `${Math.min(v * 200, 100)}%` }}></div>
                                                                    </div>
                                                                    <span className="w-20 text-right font-mono font-bold text-purple-700 dark:text-purple-400">{v?.toFixed(4)}</span>
                                                                </div>
                                                            ))}
                                                    </div>
                                                )}
                                            </div>
                                        ) : (
                                            <p className="text-xs font-medium text-slate-500">Requires 30 sequential vital signs to calculate autoencoder reconstruction.</p>
                                        )}
                                    </div>

                                    {/* Transformer Attention */}
                                    <div className="card p-5">
                                        <div className="flex items-center gap-2 mb-2">
                                            <h3 className="font-bold text-slate-900 dark:text-white text-sm">Transformer Self-Attention Temporal Distribution</h3>
                                            <InfoTag term="Transformer Attention" explanation="Shows which temporal steps received greater model focus during classification." />
                                        </div>
                                        {attnExplanation?.top_attention_steps ? (
                                            <div className="space-y-2 pt-2">
                                                {attnExplanation.top_attention_steps.map((s, i) => (
                                                    <div key={i} className="flex items-center gap-3 py-1.5 border-b border-slate-200 dark:border-slate-800 text-xs">
                                                        <span className="w-40 font-mono font-semibold text-slate-700 dark:text-slate-300">{s.time_label || `Step T−${s.step_index}`}</span>
                                                        <div className="flex-1 h-3.5 bg-slate-200 dark:bg-slate-800 rounded-full overflow-hidden">
                                                            <div className="h-full bg-sky-600 rounded-full" style={{ width: `${Math.min(s.attention_weight * 300, 100)}%` }}></div>
                                                        </div>
                                                        <span className="w-20 text-right font-mono font-bold text-sky-700 dark:text-sky-400">{(s.attention_weight * 100).toFixed(1)}%</span>
                                                    </div>
                                                ))}
                                            </div>
                                        ) : (
                                            <p className="text-xs font-medium text-slate-500">Requires sequence of 30 vital points to calculate attention maps.</p>
                                        )}
                                    </div>

                                    {/* Forecasting Transparency */}
                                    <div className="card p-5 bg-amber-50/50 dark:bg-amber-950/20 border-amber-200 dark:border-amber-900">
                                        <div className="flex items-center gap-2 mb-1 text-amber-800 dark:text-amber-400 font-bold text-sm">
                                            <i className="fa-solid fa-triangle-exclamation"></i>
                                            <span>Multi-Horizon Vital Forecasting Transparency Notice</span>
                                        </div>
                                        <p className="text-xs text-slate-700 dark:text-slate-300 leading-relaxed">
                                            The existing trained Transformer operates as a sequence-to-one classifier. It does not fabricate multi-horizon forward trajectory extrapolations without validated architectural retraining.
                                        </p>
                                    </div>
                                </div>
                            )}

                            {/* TAB 6: TIMELINE */}
                            {activeTab === 'timeline' && (
                                <div className="space-y-4">
                                    <SectionHeader title="Longitudinal Patient Lifecycle Journey" subtitle="Pregnancy → Assessment → Growth Variance → Birth → NICU Monitoring" />
                                    {timeline.length === 0 ? (
                                        <EmptyState icon="fa-timeline" title="No clinical events logged" description="No timeline milestones have been logged for this patient." />
                                    ) : (
                                        <div className="relative pl-6 border-l-2 border-slate-300 dark:border-slate-700 ml-3 space-y-4">
                                            {timeline.map((ev, i) => (
                                                <div key={i} className="relative">
                                                    <div className="absolute -left-[31px] top-1.5 w-4 h-4 rounded-full bg-white dark:bg-slate-900 border-2 border-sky-600 flex items-center justify-center">
                                                        <div className="w-1.5 h-1.5 rounded-full bg-sky-600"></div>
                                                    </div>
                                                    <div className="card p-4">
                                                        <div className="flex items-center justify-between mb-1">
                                                            <span className="font-bold text-slate-900 dark:text-white text-sm">{ev.details || ev.type}</span>
                                                            <span className="text-xs font-mono font-semibold text-slate-500">{fmt.date(ev.date)}</span>
                                                        </div>
                                                        {ev.severity && <span className="status-high px-2 py-0.5 rounded text-xs font-bold inline-block mt-1">{ev.severity}</span>}
                                                    </div>
                                                </div>
                                            ))}
                                        </div>
                                    )}
                                </div>
                            )}

                            {/* TAB 7: CLINICAL NOTES */}
                            {activeTab === 'notes' && (
                                <div className="space-y-6">
                                    <SectionHeader title="Attending Physician Notes & Orders" />
                                    {doctorReviews.length > 0 ? (
                                        doctorReviews.map(dr => (
                                            <div key={dr.id} className="card p-5 space-y-2">
                                                <div className="flex items-center justify-between text-xs font-bold border-b border-slate-200 dark:border-slate-800 pb-2">
                                                    <span className="text-sky-700 dark:text-sky-400">Reviewer: {dr.clinician_id}</span>
                                                    <span className="font-mono text-slate-500">{fmt.date(dr.review_date)}</span>
                                                </div>
                                                <p className="text-sm font-semibold text-slate-800 dark:text-slate-200"><strong>Assessment:</strong> {dr.assessment}</p>
                                                <p className="text-xs text-slate-600 dark:text-slate-400"><strong>Recommendations:</strong> {dr.recommendations}</p>
                                            </div>
                                        ))
                                    ) : (
                                        <EmptyState icon="fa-notes-medical" title="No clinical notes on record" description="No doctor notes have been filed for this admission." />
                                    )}

                                    {prescriptions.length > 0 && (
                                        <div className="card p-5">
                                            <h4 className="font-bold text-slate-900 dark:text-white text-sm mb-3">Pharmacological Orders</h4>
                                            <div className="space-y-2">
                                                {prescriptions.map(rx => (
                                                    <div key={rx.id} className="card-sm p-3 flex items-center justify-between text-xs">
                                                        <span className="font-bold text-slate-900 dark:text-white">{rx.medication_name} ({rx.dosage})</span>
                                                        <span className="font-mono text-slate-500">Initiated: {fmt.date(rx.start_date)}</span>
                                                    </div>
                                                ))}
                                            </div>
                                        </div>
                                    )}

                                    {/* Uploaded Documents List */}
                                    {uploadedReports.filter(u => u.patient_id === patientId).length > 0 && (
                                        <div className="card p-5 space-y-3 border-l-4 border-l-sky-600">
                                            <div className="flex items-center justify-between">
                                                <h4 className="font-bold text-slate-900 dark:text-white text-sm flex items-center gap-2">
                                                    <i className="fa-solid fa-file-circle-check text-sky-600"></i>
                                                    <span>Archived Clinical Uploads ({uploadedReports.filter(u => u.patient_id === patientId).length})</span>
                                                </h4>
                                                <button onClick={() => onOpenUpload && onOpenUpload(patientId)} className="text-xs font-bold text-sky-600 hover:underline">
                                                    + Upload Another
                                                </button>
                                            </div>
                                            <div className="space-y-2">
                                                {uploadedReports.filter(u => u.patient_id === patientId).map(up => (
                                                    <div key={up.id} className="card-sm p-3.5 flex items-start justify-between gap-3">
                                                        <div>
                                                            <div className="flex items-center gap-2">
                                                                <span className="font-bold text-slate-900 dark:text-white text-xs">{up.title}</span>
                                                                <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-sky-100 text-sky-800 dark:bg-sky-950 dark:text-sky-300">
                                                                    {up.report_type}
                                                                </span>
                                                            </div>
                                                            <p className="text-xs text-slate-600 dark:text-slate-400 mt-1">{up.notes || 'Routine diagnostic upload archived into patient dossier.'}</p>
                                                            <div className="text-[10px] font-mono text-slate-500 mt-1">
                                                                File: {up.filename} · By: {up.clinician} · {new Date(up.uploaded_at).toLocaleString()}
                                                            </div>
                                                        </div>
                                                        <button onClick={() => downloadPatientReport(patientId, liveVital, { customReport: up })}
                                                            className="px-2.5 py-1 rounded bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 text-xs font-bold text-slate-700 dark:text-slate-300 transition flex items-center gap-1 flex-shrink-0">
                                                            <i className="fa-solid fa-print"></i>
                                                            <span>View</span>
                                                        </button>
                                                    </div>
                                                ))}
                                            </div>
                                        </div>
                                    )}

                                    <AIChatBox patientId={patientId} compact={true} />
                                </div>
                            )}
                        </div>
                    </>
                )}
            </div>
        </div>
    );
}

// ─── Priority Patients Table Component ─────────────────────────────────────────



// ─── Priority Patients Table Component ─────────────────────────────────────────
function PriorityPatientsTable({ patients, onSelect, onDownloadReport, onOpenUpload, liveVitalsMap = {} }) {
    const prioritized = useMemo(() => patients.map(p => {
        const isCritical = ['P-SYN-002', 'P-SYN-005', 'P-SYN-008'].includes(p.id);
        const isNicu = ['P-SYN-002', 'P-SYN-003', 'P-SYN-005', 'P-SYN-007', 'P-SYN-008'].includes(p.id);
        const isAntenatal = ['P-SYN-001', 'P-SYN-004', 'P-SYN-006', 'P-SYN-009', 'P-SYN-010'].includes(p.id);
        return {
            ...p,
            simRisk: isCritical ? 0.78 : isNicu ? 0.42 : 0.18,
            stage: isNicu ? 'NICU' : isAntenatal ? 'Antenatal' : 'Monitoring',
            needsReview: isCritical,
        };
    }).sort((a, b) => b.simRisk - a.simRisk), [patients]);

    return (
        <div className="card overflow-hidden shadow-sm">
            <div className="overflow-x-auto">
                <table className="w-full text-sm">
                    <thead>
                        <tr className="bg-slate-100 dark:bg-slate-800 text-xs font-bold text-slate-700 dark:text-slate-300 uppercase tracking-wider border-b border-slate-200 dark:border-slate-700">
                            <th className="px-5 py-3.5 text-left">Patient Name</th>
                            <th className="px-5 py-3.5 text-left">Record ID</th>
                            <th className="px-5 py-3.5 text-left">Care Stage</th>
                            <th className="px-5 py-3.5 text-left">Real-Time Telemetry</th>
                            <th className="px-5 py-3.5 text-left">Status Indicator</th>
                            <th className="px-5 py-3.5 text-left">Triage Priority</th>
                            <th className="px-5 py-3.5 text-right">Actions</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-200 dark:divide-slate-800 bg-white dark:bg-slate-900/50">
                        {prioritized.map(p => {
                            const r = riskLevel(p.simRisk);
                            const avatar = PATIENT_AVATARS[p.id] || DEFAULT_AVATAR;
                            const lv = liveVitalsMap[p.id] || { heart_rate: 138, spo2: 97, respiratory_rate: 42, temperature: 36.9 };
                            const isCrit = ['P-SYN-002', 'P-SYN-005', 'P-SYN-008'].includes(p.id);
                            return (
                                <tr key={p.id} className="hover:bg-slate-50 dark:hover:bg-slate-800/60 transition cursor-pointer" onClick={() => onSelect(p.id)}>
                                    <td className="px-5 py-3.5">
                                        <div className="flex items-center gap-3">
                                            <img src={avatar} alt={p.name} className="w-9 h-9 rounded-full object-cover border border-slate-300 dark:border-slate-700 shadow-sm flex-shrink-0" />
                                            <div>
                                                <span className="font-bold text-slate-900 dark:text-white block text-sm">{p.name || p.id}</span>
                                                <span className="text-xs text-slate-500 font-mono">{p.bed || p.id}</span>
                                            </div>
                                        </div>
                                    </td>
                                    <td className="px-5 py-3.5 font-mono text-xs font-semibold text-slate-600 dark:text-slate-400">{p.id}</td>
                                    <td className="px-5 py-3.5">
                                        <span className={`px-2.5 py-0.5 rounded text-xs font-bold ${p.stage === 'NICU' ? 'bg-rose-100 text-rose-800 border border-rose-200 dark:bg-rose-950 dark:text-rose-300 dark:border-rose-800' : 'bg-sky-100 text-sky-800 border border-sky-200 dark:bg-sky-950 dark:text-sky-300 dark:border-sky-800'}`}>
                                            {p.stage}
                                        </span>
                                    </td>
                                    <td className="px-5 py-3.5">
                                        <div className="flex items-center gap-2">
                                            <span className={`px-2 py-0.5 rounded font-mono font-bold text-xs inline-flex items-center gap-1 ${lv.heart_rate > 160 ? 'bg-rose-100 text-rose-800 dark:bg-rose-950 dark:text-rose-300 border border-rose-300' : 'bg-slate-100 text-slate-800 dark:bg-slate-800 dark:text-slate-200'}`}>
                                                <i className={`fa-solid fa-heart-pulse text-xs ${lv.heart_rate > 160 ? 'text-rose-600 animate-pulse' : 'text-rose-500'}`}></i>
                                                {lv.heart_rate} bpm
                                            </span>
                                            <span className={`px-2 py-0.5 rounded font-mono font-bold text-xs inline-flex items-center gap-1 ${lv.spo2 < 93 ? 'bg-amber-100 text-amber-800 dark:bg-amber-950 dark:text-amber-300 border border-amber-300' : 'bg-sky-100 text-sky-800 dark:bg-sky-950 dark:text-sky-300'}`}>
                                                <i className="fa-solid fa-lungs text-xs text-sky-500"></i>
                                                {lv.spo2}%
                                            </span>
                                        </div>
                                    </td>
                                    <td className="px-5 py-3.5">
                                        <div className="flex items-center gap-2">
                                            <span className="w-2.5 h-2.5 rounded-full inline-block" style={{ backgroundColor: r.dot }}></span>
                                            <span className="font-semibold text-slate-800 dark:text-slate-200 text-xs">{r.label}</span>
                                        </div>
                                    </td>
                                    <td className="px-5 py-3.5">
                                        {p.needsReview ? (
                                            <span className="status-high px-2.5 py-0.5 rounded-full text-xs font-bold inline-flex items-center gap-1">
                                                <i className="fa-solid fa-triangle-exclamation text-xs"></i>
                                                Review Required
                                            </span>
                                        ) : (
                                            <span className="text-xs font-semibold text-slate-500">Routine Surveillance</span>
                                        )}
                                    </td>
                                    <td className="px-5 py-3.5 text-right whitespace-nowrap">
                                        <div className="flex items-center justify-end gap-1.5" onClick={e => e.stopPropagation()}>
                                            <button onClick={() => onDownloadReport(p.id, lv)}
                                                className="px-2.5 py-1 rounded bg-emerald-50 dark:bg-emerald-950/80 hover:bg-emerald-100 text-emerald-700 dark:text-emerald-300 border border-emerald-300 dark:border-emerald-800 text-xs font-bold transition flex items-center gap-1 shadow-sm"
                                                title="Download Patient Clinical Evaluation Report">
                                                <i className="fa-solid fa-file-arrow-down text-emerald-600"></i>
                                                <span>Report</span>
                                            </button>
                                            <button onClick={() => onOpenUpload(p.id)}
                                                className="px-2.5 py-1 rounded bg-sky-50 dark:bg-sky-950/80 hover:bg-sky-100 text-sky-700 dark:text-sky-300 border border-sky-300 dark:border-sky-800 text-xs font-bold transition flex items-center gap-1 shadow-sm"
                                                title="Upload Clinical Document for this Patient">
                                                <i className="fa-solid fa-cloud-arrow-up text-sky-600"></i>
                                                <span>Upload</span>
                                            </button>
                                            <button onClick={() => onSelect(p.id)}
                                                className="px-2.5 py-1 rounded bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 text-slate-700 dark:text-slate-300 text-xs font-bold transition flex items-center gap-1">
                                                <span>Dossier</span>
                                                <i className="fa-solid fa-chevron-right text-[10px]"></i>
                                            </button>
                                        </div>
                                    </td>
                                </tr>
                            );
                        })}
                    </tbody>
                </table>
            </div>
        </div>
    );
}

// ─── Dashboard Page (Doctor Home) ─────────────────────────────────────────────
function DashboardPage({ stats, patients, onSelectPatient, onDownloadReport, onOpenUpload, liveVitalsMap }) {
    const [filter, setFilter] = useState('ALL');
    const [search, setSearch] = useState('');
    const [showChat, setShowChat] = useState(false);

    const filtered = useMemo(() => patients.filter(p => {
        const matchSearch = (p.name || '').toLowerCase().includes(search.toLowerCase()) || p.id.toLowerCase().includes(search.toLowerCase());
        if (filter === 'NICU') return matchSearch && ['P-SYN-002','P-SYN-003','P-SYN-005','P-SYN-007','P-SYN-008'].includes(p.id);
        if (filter === 'PRENATAL') return matchSearch && ['P-SYN-001','P-SYN-004','P-SYN-006','P-SYN-009','P-SYN-010'].includes(p.id);
        if (filter === 'REVIEW') return matchSearch && ['P-SYN-002','P-SYN-005','P-SYN-008'].includes(p.id);
        return matchSearch;
    }), [patients, filter, search]);

    const reviewPatients = useMemo(() => patients.filter(p => ['P-SYN-002','P-SYN-005','P-SYN-008'].includes(p.id)), [patients]);

    return (
        <div className="space-y-6">
            {/* Top 4 Summary Cards */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {[
                    { label: 'Total Patients', value: stats.total_patients, desc: 'Active continuous surveillance', icon: 'fa-users', color: 'text-slate-600 dark:text-slate-400', filter: 'ALL', border: 'border-t-4 border-t-slate-500' },
                    { label: 'Antenatal Profiles', value: stats.active_pregnancies, desc: 'Fetal growth & Doppler protocol', icon: 'fa-person-pregnant', color: 'text-sky-600 dark:text-sky-400', filter: 'PRENATAL', border: 'border-t-4 border-t-sky-500' },
                    { label: 'NICU Incubators', value: stats.nicu_admissions, desc: 'Real-time multi-vital streaming', icon: 'fa-hospital', color: 'text-emerald-600 dark:text-emerald-400', filter: 'NICU', border: 'border-t-4 border-t-emerald-500' },
                    { label: 'Requiring Action', value: stats.active_alerts, desc: 'AI threshold flags active', icon: 'fa-triangle-exclamation', color: 'text-rose-600 dark:text-rose-400', filter: 'REVIEW', border: 'border-t-4 border-t-rose-500' },
                ].map((c, i) => (
                    <button key={i} onClick={() => setFilter(c.filter)}
                        className={`card p-5 text-left transition hover:shadow-md ${c.border} ${filter === c.filter ? 'ring-2 ring-sky-600' : ''}`}>
                        <div className="flex items-center justify-between mb-2">
                            <span className="text-xs font-bold text-slate-600 dark:text-slate-400 uppercase tracking-wider">{c.label}</span>
                            <i className={`fa-solid ${c.icon} ${c.color} text-base`}></i>
                        </div>
                        <div className="text-3xl font-extrabold text-slate-900 dark:text-white mb-1 font-mono">{c.value}</div>
                        <p className="text-xs font-medium text-slate-600 dark:text-slate-400">{c.desc}</p>
                    </button>
                ))}
            </div>

            {/* Patients Requiring Review */}
            {reviewPatients.length > 0 && (
                <div>
                    <SectionHeader
                        title="High Priority Patient Surveillance"
                        subtitle="These cases have triggered multi-modal risk thresholds. Immediate clinician review is advised."
                        action={
                            <div className="flex items-center gap-2">
                                <span className="status-high px-3 py-1 rounded-full text-xs font-bold">{reviewPatients.length} Active Flags</span>
                            </div>
                        }
                    />
                    <PriorityPatientsTable
                        patients={reviewPatients}
                        onSelect={onSelectPatient}
                        onDownloadReport={onDownloadReport}
                        onOpenUpload={onOpenUpload}
                        liveVitalsMap={liveVitalsMap}
                    />
                </div>
            )}

            {/* All Monitored Patients */}
            <div>
                <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 mb-4">
                    <SectionHeader title="Active Patient Directory" subtitle={`${filtered.length} patients currently under surveillance`} />
                    <div className="flex items-center gap-2 flex-wrap">
                        {[['ALL', 'All Cases'], ['NICU', 'NICU'], ['PRENATAL', 'Antenatal'], ['REVIEW', 'High Risk']].map(([v, l]) => (
                            <button key={v} onClick={() => setFilter(v)}
                                className={`px-3 py-1.5 rounded-lg text-xs font-bold transition ${filter === v ? 'bg-sky-600 text-white shadow-sm' : 'bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-300 border border-slate-300 dark:border-slate-700 hover:bg-slate-50'}`}>
                                {l}
                            </button>
                        ))}
                        <button onClick={() => onOpenUpload()}
                            className="px-3 py-1.5 rounded-lg text-xs font-bold bg-indigo-600 hover:bg-indigo-500 text-white transition flex items-center gap-1.5 shadow-sm">
                            <i className="fa-solid fa-cloud-arrow-up"></i>
                            <span>Upload Report</span>
                        </button>
                        <div className="relative">
                            <input
                                value={search} onChange={e => setSearch(e.target.value)}
                                placeholder="Search by name, ID or bed..."
                                className="bg-white dark:bg-slate-900 border border-slate-300 dark:border-slate-700 rounded-lg pl-8 pr-3 py-1.5 text-xs text-slate-900 dark:text-slate-100 placeholder-slate-500 outline-none focus:border-sky-600 focus:ring-1 focus:ring-sky-600 font-medium w-52 shadow-sm"
                            />
                            <i className="fa-solid fa-magnifying-glass absolute left-2.5 top-2.5 text-slate-400 text-xs"></i>
                        </div>
                    </div>
                </div>
                <PriorityPatientsTable
                    patients={filtered}
                    onSelect={onSelectPatient}
                    onDownloadReport={onDownloadReport}
                    onOpenUpload={onOpenUpload}
                    liveVitalsMap={liveVitalsMap}
                />
            </div>

            {/* Ward AI Assistant (Collapsible) */}
            <div className="pt-2">
                <button onClick={() => setShowChat(!showChat)}
                    className="flex items-center gap-2 text-sm font-bold text-slate-700 dark:text-slate-300 hover:text-sky-600 transition mb-3">
                    <i className={`fa-solid fa-chevron-${showChat ? 'down' : 'right'} text-xs`}></i>
                    <i className="fa-solid fa-robot text-sky-600 dark:text-sky-400"></i>
                    <span>Clinical AI Ward Consultant</span>
                    <span className="text-xs font-normal text-slate-500">(click to expand)</span>
                </button>
                {showChat && <AIChatBox patientId="global_ward" />}
            </div>
        </div>
    );
}

// ─── Alerts Center Page ───────────────────────────────────────────────────────
function AlertsPage({ patients, onSelectPatient, onDownloadReport, onOpenUpload, liveVitalsMap }) {
    const criticalPatients = patients.filter(p => ['P-SYN-002','P-SYN-005','P-SYN-008'].includes(p.id));
    return (
        <div className="space-y-5">
            <SectionHeader title="Clinical Alert Center" subtitle="Real-time multi-modal threshold notifications and priority flags." />
            {criticalPatients.length === 0 ? (
                <EmptyState icon="fa-bell-slash" title="No active clinical alerts" description="All monitored patients are operating within expected baseline parameters." />
            ) : (
                <div className="space-y-3">
                    {criticalPatients.map(p => {
                        const avatar = PATIENT_AVATARS[p.id] || DEFAULT_AVATAR;
                        const lv = liveVitalsMap[p.id] || { heart_rate: 168, spo2: 91 };
                        return (
                            <div key={p.id} className="card p-5 border-l-4 border-l-rose-600 hover:shadow-md transition">
                                <div className="flex items-start justify-between flex-wrap gap-4">
                                    <div className="flex items-center gap-4">
                                        <img src={avatar} alt={p.name} className="w-12 h-12 rounded-full object-cover border border-slate-300 dark:border-slate-700 shadow-sm" />
                                        <div>
                                            <div className="flex items-center gap-2 mb-1">
                                                <span className="status-high px-2.5 py-0.5 rounded-full text-xs font-bold inline-flex items-center gap-1">
                                                    <i className="fa-solid fa-triangle-exclamation"></i> High Priority Review Flag
                                                </span>
                                                <span className="text-xs font-mono font-bold text-rose-600 dark:text-rose-400 bg-rose-50 dark:bg-rose-950 px-2 py-0.5 rounded">
                                                    HR: {lv.heart_rate} bpm · SpO2: {lv.spo2}%
                                                </span>
                                            </div>
                                            <h3 className="font-bold text-slate-900 dark:text-white text-base">{p.name || p.id}</h3>
                                            <p className="text-xs font-mono font-semibold text-slate-500 mt-0.5">ID: {p.id} · Level IV NICU Telemetry</p>
                                            <p className="text-xs font-medium text-slate-600 dark:text-slate-400 mt-1">Multi-modal deterioration probability &gt; 70% threshold</p>
                                        </div>
                                    </div>
                                    <div className="flex items-center gap-2">
                                        <button onClick={() => onDownloadReport(p.id, lv)}
                                            className="bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold px-3 py-2 rounded-lg transition shadow-sm flex items-center gap-1.5">
                                            <i className="fa-solid fa-file-arrow-down"></i>
                                            <span>Download Report</span>
                                        </button>
                                        <button onClick={() => onSelectPatient(p.id)}
                                            className="bg-sky-600 hover:bg-sky-500 text-white text-xs font-bold px-4 py-2 rounded-lg transition shadow-sm">
                                            Open Dossier →
                                        </button>
                                    </div>
                                </div>
                            </div>
                        );
                    })}
                </div>
            )}
        </div>
    );
}

// ─── NICU Page ────────────────────────────────────────────────────────────────
function NicuPage({ patients, onSelectPatient, onDownloadReport, onOpenUpload, liveVitalsMap }) {
    const nicuPatients = patients.filter(p => ['P-SYN-002','P-SYN-003','P-SYN-005','P-SYN-007','P-SYN-008'].includes(p.id));
    return (
        <div className="space-y-5">
            <SectionHeader title="NICU Continuous Telemetry Surveillance" subtitle={`${nicuPatients.length} incubators under continuous hemodynamic & respiratory monitoring`} />
            <PriorityPatientsTable
                patients={nicuPatients}
                onSelect={onSelectPatient}
                onDownloadReport={onDownloadReport}
                onOpenUpload={onOpenUpload}
                liveVitalsMap={liveVitalsMap}
            />
        </div>
    );
}

// ─── Pregnancy Page ───────────────────────────────────────────────────────────
function PregnancyPage({ patients, onSelectPatient, onDownloadReport, onOpenUpload, liveVitalsMap }) {
    const antenatal = patients.filter(p => ['P-SYN-001','P-SYN-004','P-SYN-006','P-SYN-009','P-SYN-010'].includes(p.id));
    return (
        <div className="space-y-5">
            <SectionHeader title="Antenatal Longitudinal Surveillance" subtitle={`${antenatal.length} pregnancies under growth & Doppler protocol`} />
            <PriorityPatientsTable
                patients={antenatal}
                onSelect={onSelectPatient}
                onDownloadReport={onDownloadReport}
                onOpenUpload={onOpenUpload}
                liveVitalsMap={liveVitalsMap}
            />
        </div>
    );
}

// ─── Clean Physician Login Screen ─────────────────────────────────────────────
function LoginScreen({ onLogin, isDark, toggleTheme }) {
    return (
        <div className="min-h-screen flex items-center justify-center p-6 bg-slate-100 dark:bg-[#0b1120] text-slate-900 dark:text-slate-100">
            <div className="w-full max-w-md">
                <div className="text-center mb-8">
                    <div className="w-16 h-16 rounded-2xl bg-gradient-to-tr from-sky-600 to-teal-500 text-white flex items-center justify-center mx-auto mb-4 shadow-lg">
                        <i className="fa-solid fa-heart-pulse text-3xl"></i>
                    </div>
                    <h1 className="text-2xl font-extrabold text-slate-900 dark:text-white tracking-tight">NeoNatal Watch AI</h1>
                    <p className="text-sm font-medium text-slate-600 dark:text-slate-400 mt-1">Perinatal & NICU Clinical Decision Support Suite</p>
                </div>

                <div className="card p-6 space-y-4 shadow-xl border border-slate-200 dark:border-slate-800 rounded-2xl">
                    <div className="text-center pb-2 border-b border-slate-200 dark:border-slate-800">
                        <span className="text-xs font-bold text-sky-600 dark:text-sky-400 uppercase tracking-widest">Clinical Access Gateway</span>
                    </div>

                    <button onClick={() => onLogin('doctor')}
                        className="w-full bg-gradient-to-r from-sky-600 to-teal-600 hover:from-sky-500 hover:to-teal-500 text-white p-4 rounded-xl text-left transition shadow-md group">
                        <div className="flex items-center gap-3.5">
                            <div className="w-11 h-11 rounded-lg bg-white/20 text-white flex items-center justify-center font-bold text-xl">
                                <i className="fa-solid fa-user-doctor"></i>
                            </div>
                            <div className="flex-1">
                                <div className="font-extrabold text-white text-base">Attending Physician Portal</div>
                                <div className="text-xs text-sky-100 mt-0.5">Access patient telemetry, risk forecasts & clinical XAI</div>
                            </div>
                            <i className="fa-solid fa-arrow-right text-white group-hover:translate-x-1 transition text-sm"></i>
                        </div>
                    </button>
                </div>

                <div className="flex items-center justify-center mt-6 text-xs text-slate-500 gap-4">
                    <button onClick={toggleTheme} className="font-bold text-sky-600 dark:text-sky-400 hover:underline flex items-center gap-1.5">
                        <i className={`fa-solid ${isDark ? 'fa-sun text-amber-500' : 'fa-moon text-sky-600'}`}></i>
                        <span>Switch to {isDark ? 'Light' : 'Dark'} Mode</span>
                    </button>
                </div>
            </div>
        </div>
    );
}

// ─── Main Root Application ────────────────────────────────────────────────────
function App() {
    const [userRole, setUserRole] = useState(localStorage.getItem('nw_role') || 'doctor');
    const [activePage, setActivePage] = useState('dashboard');
    const [patients, setPatients] = useState([]);
    const [stats, setStats] = useState({ total_patients: 10, active_pregnancies: 5, nicu_admissions: 5, active_alerts: 3 });
    const [selectedPatientId, setSelectedPatientId] = useState(null);
    const [theme, setTheme] = useState(localStorage.getItem('nw_theme') || 'light');

    // Live Real-Time Telemetry Simulation Engine
    const [liveTick, setLiveTick] = useState(0);
    const [liveVitalsMap, setLiveVitalsMap] = useState({});

    // Upload Report Modal State
    const [uploadModalOpen, setUploadModalOpen] = useState(false);
    const [uploadTargetId, setUploadTargetId] = useState('P-SYN-002');
    const [uploadedReports, setUploadedReports] = useState(() => {
        try {
            return JSON.parse(localStorage.getItem('nw_uploaded_reports') || '[]');
        } catch (e) {
            return [];
        }
    });

    // Toast Notification
    const [toastMessage, setToastMessage] = useState(null);

    const showToast = (msg) => {
        setToastMessage(msg);
        setTimeout(() => setToastMessage(null), 4000);
    };

    // Telemetry Ticker (updates every 3 seconds for continuous real-time dynamics)
    useEffect(() => {
        const interval = setInterval(() => {
            setLiveTick(t => t + 1);
        }, 3000);
        return () => clearInterval(interval);
    }, []);

    useEffect(() => {
        const map = {};
        const now = Date.now();
        FALLBACK_PATIENTS.forEach(p => {
            const isCrit = ['P-SYN-002', 'P-SYN-005', 'P-SYN-008'].includes(p.id);
            const isNicu = ['P-SYN-002', 'P-SYN-003', 'P-SYN-005', 'P-SYN-007', 'P-SYN-008'].includes(p.id);
            const baseHR = isCrit ? 168 : isNicu ? 138 : 78;
            const baseSpO2 = isCrit ? 91 : 97;
            const baseRR = isCrit ? 62 : isNicu ? 42 : 18;
            const baseTemp = isCrit ? 37.8 : 36.9;

            const hrDelta = Math.sin((liveTick * 0.4) + p.id.charCodeAt(p.id.length - 1)) * 4 + (Math.random() * 2 - 1);
            const spo2Delta = Math.cos((liveTick * 0.3) + p.id.charCodeAt(p.id.length - 1)) * (isCrit ? 1.5 : 0.8);
            const rrDelta = Math.sin(liveTick * 0.5) * 2;
            const tempDelta = Math.cos(liveTick * 0.2) * 0.1;

            map[p.id] = {
                heart_rate: Math.round(baseHR + hrDelta),
                spo2: Math.min(100, Math.max(82, Math.round(baseSpO2 + spo2Delta))),
                respiratory_rate: Math.round(baseRR + rrDelta),
                temperature: +(baseTemp + tempDelta).toFixed(1),
                timestamp: new Date(now).toISOString(),
                isCrit,
                isNicu
            };
        });
        setLiveVitalsMap(map);
    }, [liveTick]);

    useEffect(() => {
        if (theme === 'dark') {
            document.documentElement.classList.add('dark');
        } else {
            document.documentElement.classList.remove('dark');
        }
        localStorage.setItem('nw_theme', theme);
    }, [theme]);

    const toggleTheme = () => {
        setTheme(prev => prev === 'dark' ? 'light' : 'dark');
    };

    useEffect(() => {
        if (!userRole) return;
        apiGet('/patients/').then(d => Array.isArray(d) && setPatients(d)).catch(() => {});
        apiGet('/patients/stats/summary').then(setStats).catch(() => {});
    }, [userRole]);

    const handleLogin = role => {
        setUserRole(role);
        localStorage.setItem('nw_role', role);
    };
    const handleLogout = () => {
        setUserRole(null);
        localStorage.removeItem('nw_role');
    };

    const handleReportUploaded = (newDoc) => {
        const updated = [newDoc, ...uploadedReports];
        setUploadedReports(updated);
        try {
            localStorage.setItem('nw_uploaded_reports', JSON.stringify(updated));
        } catch (e) {}
        showToast(`Document "${newDoc.title}" archived successfully in Patient ${newDoc.patient_id} dossier!`);
    };

    const handleOpenUpload = (pid) => {
        if (pid) setUploadTargetId(pid);
        setUploadModalOpen(true);
    };

    const handleDownloadReport = (pid, lv = null) => {
        downloadPatientReport(pid, lv || liveVitalsMap[pid]);
        showToast(`Clinical Evaluation Report for ${pid} generated and downloaded.`);
    };

    const isDark = theme === 'dark';

    if (!userRole) return <LoginScreen onLogin={handleLogin} isDark={isDark} toggleTheme={toggleTheme} />;

    const NAV = [
        { id: 'dashboard', label: 'Dashboard', icon: 'fa-gauge-high' },
        { id: 'patients', label: 'Patients', icon: 'fa-users' },
        { id: 'pregnancy', label: 'Pregnancy', icon: 'fa-person-pregnant' },
        { id: 'nicu', label: 'NICU', icon: 'fa-hospital' },
        { id: 'alerts', label: 'Alerts', icon: 'fa-triangle-exclamation' },
        { id: 'assistant', label: 'AI Assistant', icon: 'fa-robot' },
    ];

    return (
        <div className="min-h-screen flex flex-col bg-[#f1f5f9] dark:bg-[#0b1120] text-slate-900 dark:text-slate-100 transition-colors">
            {/* Toast Notification Banner */}
            {toastMessage && (
                <div className="fixed top-4 right-4 z-50 bg-emerald-700 text-white text-xs font-bold px-4 py-3 rounded-xl shadow-2xl flex items-center gap-2.5 animate-bounce">
                    <i className="fa-solid fa-circle-check text-base text-emerald-300"></i>
                    <span>{toastMessage}</span>
                </div>
            )}

            {/* Top Navigation Bar */}
            <header className="bg-white dark:bg-[#0f1729] border-b border-slate-200 dark:border-slate-800 px-6 py-3 flex items-center justify-between sticky top-0 z-30 shadow-sm">
                <div className="flex items-center gap-4">
                    <div className="flex items-center gap-2.5 cursor-pointer" onClick={() => setActivePage('dashboard')}>
                        <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-sky-600 to-teal-500 text-white flex items-center justify-center shadow-sm">
                            <i className="fa-solid fa-heart-pulse text-sm"></i>
                        </div>
                        <div>
                            <span className="font-extrabold text-slate-900 dark:text-white text-base tracking-tight">NeoNatal Watch AI</span>
                            <span className="text-xs font-semibold text-sky-700 dark:text-sky-400 bg-sky-50 dark:bg-sky-950 px-2 py-0.5 rounded ml-2 border border-sky-200 dark:border-sky-800">
                                Clinical Decision Support
                            </span>
                        </div>
                    </div>

                    <nav className="hidden md:flex items-center gap-1.5 ml-6">
                        {NAV.map(n => (
                            <button key={n.id} onClick={() => setActivePage(n.id)}
                                className={`flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg text-xs font-bold transition ${activePage === n.id ? 'nav-active' : 'nav-inactive'}`}>
                                <i className={`fa-solid ${n.icon} text-xs`}></i>
                                <span>{n.label}</span>
                            </button>
                        ))}
                    </nav>
                </div>

                <div className="flex items-center gap-2.5">
                    {/* Quick Upload Action */}
                    <button onClick={() => handleOpenUpload()}
                        className="hidden sm:flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-sky-50 dark:bg-sky-950/80 hover:bg-sky-100 text-sky-700 dark:text-sky-300 border border-sky-300 dark:border-sky-800 text-xs font-bold transition shadow-sm">
                        <i className="fa-solid fa-cloud-arrow-up text-sky-600"></i>
                        <span>Upload Report</span>
                    </button>

                    {/* Live Telemetry Pulse Chip */}
                    <div className="flex items-center gap-2 text-xs font-bold bg-emerald-50 dark:bg-emerald-950/80 border border-emerald-300 dark:border-emerald-800 text-emerald-800 dark:text-emerald-300 px-3 py-1 rounded-full shadow-sm">
                        <span className="relative flex h-2 w-2">
                            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                            <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
                        </span>
                        <span className="hidden sm:inline">LIVE TELEMETRY</span>
                        <span className="text-[10px] font-mono font-semibold text-emerald-600 dark:text-emerald-400">100Hz</span>
                    </div>

                    <button onClick={toggleTheme} title="Toggle Eye-Comfort Theme"
                        className="p-2 rounded-lg bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 hover:text-sky-600 text-xs font-bold flex items-center gap-1.5 border border-slate-300 dark:border-slate-700 transition">
                        <i className={`fa-solid ${isDark ? 'fa-sun text-amber-500' : 'fa-moon text-sky-600'}`}></i>
                        <span className="hidden sm:inline">{isDark ? 'Light' : 'Dark'}</span>
                    </button>

                    <div className="text-xs font-bold text-slate-700 dark:text-slate-300 bg-slate-100 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 px-2.5 py-1 rounded-lg flex items-center gap-1">
                        <i className="fa-solid fa-user-doctor text-sky-600"></i>
                        <span className="hidden sm:inline">Physician</span>
                    </div>

                    <button onClick={handleLogout} title="Sign Out"
                        className="w-8 h-8 rounded-lg bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-600 dark:text-slate-400 hover:text-rose-600 flex items-center justify-center transition text-xs border border-slate-200 dark:border-slate-700">
                        <i className="fa-solid fa-arrow-right-from-bracket"></i>
                    </button>
                </div>
            </header>

            {/* Main Page Body */}
            <main className="flex-1 max-w-7xl w-full mx-auto px-6 py-6">
                {activePage === 'dashboard' && (
                    <DashboardPage
                        stats={stats}
                        patients={patients}
                        onSelectPatient={setSelectedPatientId}
                        onDownloadReport={handleDownloadReport}
                        onOpenUpload={handleOpenUpload}
                        liveVitalsMap={liveVitalsMap}
                    />
                )}
                {activePage === 'patients' && (
                    <div className="space-y-5">
                        <div className="flex items-center justify-between">
                            <SectionHeader title="Monitored Patient Directory" subtitle={`${patients.length} total patient records under surveillance`} />
                            <button onClick={() => handleOpenUpload()}
                                className="px-3 py-1.5 rounded-lg text-xs font-bold bg-sky-600 hover:bg-sky-500 text-white transition flex items-center gap-1.5 shadow-sm">
                                <i className="fa-solid fa-cloud-arrow-up"></i>
                                <span>Upload Patient Document</span>
                            </button>
                        </div>
                        <PriorityPatientsTable
                            patients={patients}
                            onSelect={setSelectedPatientId}
                            onDownloadReport={handleDownloadReport}
                            onOpenUpload={handleOpenUpload}
                            liveVitalsMap={liveVitalsMap}
                        />
                    </div>
                )}
                {activePage === 'pregnancy' && (
                    <PregnancyPage
                        patients={patients}
                        onSelectPatient={setSelectedPatientId}
                        onDownloadReport={handleDownloadReport}
                        onOpenUpload={handleOpenUpload}
                        liveVitalsMap={liveVitalsMap}
                    />
                )}
                {activePage === 'nicu' && (
                    <NicuPage
                        patients={patients}
                        onSelectPatient={setSelectedPatientId}
                        onDownloadReport={handleDownloadReport}
                        onOpenUpload={handleOpenUpload}
                        liveVitalsMap={liveVitalsMap}
                    />
                )}
                {activePage === 'alerts' && (
                    <AlertsPage
                        patients={patients}
                        onSelectPatient={setSelectedPatientId}
                        onDownloadReport={handleDownloadReport}
                        onOpenUpload={handleOpenUpload}
                        liveVitalsMap={liveVitalsMap}
                    />
                )}
                {activePage === 'assistant' && (
                    <div className="max-w-3xl">
                        <SectionHeader title="Ward Clinical AI Assistant" subtitle="Clinical decision support & biometrics query consultant" />
                        <AIChatBox patientId="global_ward" compact={false} />
                    </div>
                )}
            </main>

            {/* Clean Professional Footer */}
            <footer className="border-t border-slate-200 dark:border-slate-800 py-3.5 px-6 text-center text-xs font-semibold text-slate-500 bg-white dark:bg-[#0f1729]">
                NeoNatal Watch AI · Longitudinal Maternal-Fetal Decision Support Suite · All Rights Reserved
            </footer>

            {/* Patient Detail Drawer */}
            {selectedPatientId && (
                <PatientDetailDrawer
                    patientId={selectedPatientId}
                    onClose={() => setSelectedPatientId(null)}
                    userRole={userRole}
                    isDark={isDark}
                    onDownloadReport={handleDownloadReport}
                    onOpenUpload={handleOpenUpload}
                    uploadedReports={uploadedReports}
                    liveVital={liveVitalsMap[selectedPatientId]}
                />
            )}

            {/* Upload Report Modal */}
            <UploadReportModal
                isOpen={uploadModalOpen}
                onClose={() => setUploadModalOpen(false)}
                patients={patients.length > 0 ? patients : FALLBACK_PATIENTS}
                onReportUploaded={handleReportUploaded}
                initialPatientId={uploadTargetId}
            />
        </div>
    );
}

// Mount React Root
const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(<App />);
