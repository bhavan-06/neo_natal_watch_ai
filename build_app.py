import sys
content = """const { useState, useEffect, useRef, useCallback } = React;

const API = 'http://localhost:8000/api/v1';

// Chart.js helper component
function VitalChart({ data, label, color, yMin, yMax, normalRange }) {
    const canvasRef = useRef(null);
    const chartRef = useRef(null);

    useEffect(() => {
        if (!canvasRef.current) return;
        const ctx = canvasRef.current.getContext('2d');
        
        if (chartRef.current) {
            chartRef.current.destroy();
        }

        chartRef.current = new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.map(d => d.time),
                datasets: [{
                    label: label,
                    data: data.map(d => d.value),
                    borderColor: color,
                    backgroundColor: color + '33',
                    fill: true,
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: { min: yMin, max: yMax }
                },
                plugins: {
                    legend: { display: false }
                }
            }
        });

        return () => {
            if (chartRef.current) chartRef.current.destroy();
        };
    }, [data, label, color, yMin, yMax]);

    return (
        <div style={{ height: '200px' }}>
            <div className="flex justify-between items-center mb-2">
                <span className="text-xs font-bold text-slate-500">{label}</span>
                <span className="text-xs text-slate-400">Normal: {normalRange}</span>
            </div>
            <canvas ref={canvasRef}></canvas>
        </div>
    );
}

function AIChatBox({ patientId }) {
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState('');

    const send = async () => {
        if (!input.trim()) return;
        const msg = input;
        setInput('');
        setMessages(prev => [...prev, { role: 'user', text: msg }]);
        try {
            const res = await fetch(`${API}/chat/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: msg, patient_id: patientId })
            });
            const data = await res.json();
            setMessages(prev => [...prev, { role: 'ai', text: data.reply }]);
        } catch (e) {
            setMessages(prev => [...prev, { role: 'ai', text: 'Error connecting to AI.' }]);
        }
    };

    return (
        <div className="flex flex-col h-64 border rounded bg-slate-50 mt-4">
            <div className="p-2 bg-slate-200 font-bold text-xs text-slate-600">AI Assistant</div>
            <div className="flex-1 overflow-y-auto p-2 space-y-2 text-sm">
                {messages.map((m, i) => (
                    <div key={i} className={`p-2 rounded max-w-[80%] ${m.role === 'user' ? 'bg-sky-100 self-end ml-auto text-sky-800' : 'bg-white border text-slate-700'}`}>
                        {m.text}
                    </div>
                ))}
            </div>
            <div className="flex p-2 border-t bg-white">
                <input value={input} onChange={e => setInput(e.target.value)} onKeyPress={e => e.key === 'Enter' && send()} placeholder="Ask about this patient..." className="flex-1 border rounded px-2 py-1 text-sm outline-none" />
                <button onClick={send} className="ml-2 bg-sky-600 text-white px-3 py-1 rounded text-sm hover:bg-sky-700">Send</button>
            </div>
        </div>
    );
}

function PatientDetailModal({ patientId, onClose }) {
    const [patient, setPatient] = useState(null);
    const [timeline, setTimeline] = useState([]);
    const [pregnancies, setPregnancies] = useState([]);
    const [fetalAssessments, setFetalAssessments] = useState([]);
    const [growth, setGrowth] = useState([]);
    const [newborns, setNewborns] = useState([]);
    const [nicu, setNicu] = useState([]);
    const [predictions, setPredictions] = useState([]);
    const [vitals, setVitals] = useState([]);

    useEffect(() => {
        if (!patientId) return;
        fetch(API + '/patients/' + patientId).then(r => r.json()).then(setPatient);
        fetch(API + '/patients/' + patientId + '/timeline').then(r => r.json()).then(setTimeline);
        fetch(API + '/patients/' + patientId + '/pregnancy').then(r => r.json()).then(setPregnancies);
        fetch(API + '/patients/' + patientId + '/fetal-assessments').then(r => r.json()).then(setFetalAssessments);
        fetch(API + '/patients/' + patientId + '/growth-analysis').then(r => r.json()).then(setGrowth);
        fetch(API + '/patients/' + patientId + '/newborn').then(r => r.json()).then(setNewborns);
        fetch(API + '/patients/' + patientId + '/nicu').then(r => r.json()).then(setNicu);
        fetch(API + '/patients/' + patientId + '/predictions').then(r => r.json()).then(setPredictions);
        
        // Setup NICU Live Stream if it is the live patient
        if (patientId === 'LIVE-PATIENT-001') {
            const evtSource = new EventSource(`${API}/stream/`);
            evtSource.onmessage = function(event) {
                const data = JSON.parse(event.data);
                setVitals(prev => [...prev.slice(-30), data]);
            };
            return () => evtSource.close();
        }
    }, [patientId]);

    if (!patient) return <div className='fixed inset-0 bg-slate-900/50 flex items-center justify-center z-50'><div className='bg-white p-8 rounded shadow text-slate-500'>Loading longitudinal data...</div></div>;

    const hrData = vitals.map(v => ({ time: new Date(v.timestamp).toLocaleTimeString(), value: v.heart_rate }));
    const spo2Data = vitals.map(v => ({ time: new Date(v.timestamp).toLocaleTimeString(), value: v.spo2 }));

    return (
        <div className='fixed inset-0 bg-slate-900/50 flex justify-end z-50'>
            <div className='w-full max-w-4xl bg-slate-50 h-full overflow-y-auto shadow-2xl animate-slide-in'>
                <div className='sticky top-0 bg-white border-b px-6 py-4 flex justify-between items-center z-10'>
                    <div>
                        <h2 className='text-xl font-bold text-slate-800'>{patient.name || patient.patient_code}</h2>
                        <div className='text-xs text-slate-500'>Longitudinal Record | ID: {patient.id}</div>
                    </div>
                    <button onClick={onClose} className='text-slate-400 hover:text-slate-700 text-3xl font-bold'>&times;</button>
                </div>
                <div className='p-6 space-y-6'>
                    
                    <div className='bg-white p-5 rounded-lg border shadow-sm'>
                        <h3 className='font-bold text-slate-700 border-b pb-2 mb-3'>1. PATIENT & MATERNAL PROFILE</h3>
                        <div className="grid grid-cols-2 gap-4 text-sm text-slate-600">
                            <div><strong>DOB:</strong> {patient.date_of_birth || 'Unknown'}</div>
                            <div><strong>Contact:</strong> {patient.contact_info || 'Unknown'}</div>
                        </div>
                    </div>

                    <div className='bg-white p-5 rounded-lg border shadow-sm'>
                        <h3 className='font-bold text-slate-700 border-b pb-2 mb-3'>2. PREGNANCY & FETAL ASSESSMENTS</h3>
                        {pregnancies.length > 0 ? pregnancies.map(p => (
                            <div key={p.id} className='mb-4 p-3 bg-slate-50 rounded border'>
                                <div className='font-semibold text-sky-700'>Pregnancy: {p.pregnancy_status || 'Active'}</div>
                                <div className='text-xs text-slate-500 mb-2'>Start: {p.pregnancy_start || 'N/A'} | EDD: {p.estimated_due_date || 'N/A'}</div>
                                <div className='pl-4 border-l-2 border-sky-200 mt-2 space-y-2'>
                                    {fetalAssessments.filter(f => f.pregnancy_id === p.id).map(f => (
                                        <div key={f.id} className='text-sm bg-white p-2 rounded shadow-sm'>
                                            <strong>Trimester {f.trimester}:</strong> EFW: {f.efw}g ({f.efw_percentile}th %ile), CRL: {f.crl}mm. 
                                            <div className="text-xs text-slate-400 mt-1">Date: {new Date(f.assessment_date).toLocaleDateString()}</div>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )) : <div className='text-sm text-slate-400'>No pregnancy data.</div>}
                    </div>

                    <div className='bg-white p-5 rounded-lg border shadow-sm'>
                        <h3 className='font-bold text-slate-700 border-b pb-2 mb-3'>3. PREDICTED VS ACTUAL & GROWTH ANALYSIS</h3>
                        {growth.length > 0 ? growth.map(g => (
                            <div key={g.id} className={`p-4 rounded border ${g.evaluation_status.includes('NORMAL') ? 'bg-emerald-50 border-emerald-200' : 'bg-amber-50 border-amber-200'} mb-2`}>
                                <div className="grid grid-cols-3 gap-2 text-center text-sm mb-3">
                                    <div className="bg-white p-2 rounded">
                                        <div className="text-xs text-slate-400">Predicted (2nd Tri EFW)</div>
                                        <div className="font-bold text-slate-700">{g.predicted_efw_percentile} %ile</div>
                                    </div>
                                    <div className="flex items-center justify-center font-bold text-xl text-slate-400">vs</div>
                                    <div className="bg-white p-2 rounded">
                                        <div className="text-xs text-slate-400">Actual (2nd Tri EFW)</div>
                                        <div className="font-bold text-slate-700">{g.actual_efw_percentile} %ile</div>
                                    </div>
                                </div>
                                <div className='text-sm'>
                                    <strong>Variance (Δ):</strong> {g.growth_variance} points<br/>
                                    <strong>Status:</strong> <span className='font-bold'>{g.evaluation_status}</span><br/>
                                    <strong>Contributing Patterns:</strong> {g.contributing_patterns || 'None identified.'}
                                </div>
                            </div>
                        )) : <div className='text-sm text-slate-400'>No growth variance analysis available yet.</div>}
                    </div>

                    <div className='bg-white p-5 rounded-lg border shadow-sm'>
                        <h3 className='font-bold text-slate-700 border-b pb-2 mb-3'>4. CLINICIAN REVIEWS & EVENTS</h3>
                        {timeline.length > 0 ? (
                            <ul className='space-y-2'>
                                {timeline.map((t, i) => (
                                    <li key={i} className='text-sm text-slate-600 flex items-start'>
                                        <span className={`px-2 py-0.5 rounded text-xs font-bold mr-2 mt-0.5 ${t.type === 'alert' ? 'bg-red-100 text-red-700' : 'bg-sky-100 text-sky-700'}`}>
                                            {t.type.toUpperCase()}
                                        </span>
                                        <div>
                                            <div className="text-slate-800">{t.details}</div>
                                            <div className="text-xs text-slate-400">{new Date(t.date).toLocaleString()}</div>
                                        </div>
                                    </li>
                                ))}
                            </ul>
                        ) : <div className='text-sm text-slate-400'>No clinical events.</div>}
                    </div>

                    <div className='bg-white p-5 rounded-lg border shadow-sm'>
                        <h3 className='font-bold text-slate-700 border-b pb-2 mb-3'>5. BIRTH, NEWBORN & NICU</h3>
                        {newborns.map(n => (
                            <div key={n.id} className='text-sm text-slate-600 mb-2 p-2 bg-slate-50 rounded'>
                                <strong>Newborn ID:</strong> {n.newborn_code} | <strong>Birth Date:</strong> {new Date(n.birth_date).toLocaleDateString()} | <strong>Weight:</strong> {n.birth_weight}g
                            </div>
                        ))}
                        {nicu.map(n => (
                            <div key={n.id} className='text-sm text-slate-600 mb-4 p-2 bg-sky-50 rounded text-sky-800 font-medium border border-sky-100'>
                                <strong>NICU Admission:</strong> {n.status} | <strong>Date:</strong> {new Date(n.admission_date).toLocaleDateString()}
                            </div>
                        ))}

                        {vitals.length > 0 && (
                            <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-4">
                                <div className="border p-2 rounded"><VitalChart data={hrData} label="Heart Rate (bpm)" color="#ef4444" yMin={80} yMax={200} normalRange="100-160" /></div>
                                <div className="border p-2 rounded"><VitalChart data={spo2Data} label="SpO2 (%)" color="#3b82f6" yMin={80} yMax={100} normalRange="92-100" /></div>
                            </div>
                        )}
                        
                        <AIChatBox patientId={patientId} />
                    </div>
                </div>
            </div>
        </div>
    );
}

function Dashboard() {
    const [patients, setPatients] = useState([]);
    const [selectedId, setSelectedId] = useState(null);

    useEffect(() => {
        fetch(API + '/patients/').then(r => r.json()).then(setPatients);
    }, []);

    return (
        <div className='min-h-screen bg-slate-50'>
            <header className='bg-white border-b px-6 py-4 sticky top-0 z-40 shadow-sm'>
                <div className='max-w-7xl mx-auto flex justify-between items-center'>
                    <div>
                        <h1 className='text-2xl font-bold text-slate-800'>NeoNatal Watch AI</h1>
                        <p className='text-xs font-semibold text-slate-400'>ACADEMIC / RESEARCH PROTOTYPE — NOT FOR CLINICAL USE</p>
                    </div>
                </div>
            </header>
            
            <main className='max-w-7xl mx-auto p-6'>
                <div className='grid grid-cols-2 md:grid-cols-4 gap-4 mb-8'>
                    <div className='bg-white p-5 rounded-lg border shadow-sm'>
                        <div className='text-slate-500 text-xs font-bold uppercase mb-1'>Total Patients</div>
                        <div className='text-3xl font-black text-slate-700'>{patients.length}</div>
                    </div>
                    <div className='bg-white p-5 rounded-lg border shadow-sm'>
                        <div className='text-slate-500 text-xs font-bold uppercase mb-1'>Active Pregnancies</div>
                        <div className='text-3xl font-black text-sky-600'>-</div>
                    </div>
                    <div className='bg-white p-5 rounded-lg border shadow-sm'>
                        <div className='text-slate-500 text-xs font-bold uppercase mb-1'>NICU Admissions</div>
                        <div className='text-3xl font-black text-amber-500'>-</div>
                    </div>
                    <div className='bg-white p-5 rounded-lg border shadow-sm'>
                        <div className='text-slate-500 text-xs font-bold uppercase mb-1'>Active Alerts</div>
                        <div className='text-3xl font-black text-red-500'>0</div>
                    </div>
                </div>
                
                <h2 className='text-lg font-bold text-slate-700 mb-4'>Patient Roster</h2>
                <div className='grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-4'>
                    <div className='bg-white rounded-lg border p-5 shadow-sm hover:shadow-md cursor-pointer border-l-4 border-l-sky-500 transition relative overflow-hidden' onClick={() => setSelectedId('LIVE-PATIENT-001')}>
                        <div className="absolute top-2 right-2 flex items-center gap-1">
                            <span className="w-2 h-2 rounded-full bg-red-500 animate-pulse"></span>
                            <span className="text-[10px] font-bold text-slate-400 uppercase">Live NICU</span>
                        </div>
                        <div className='font-bold text-slate-800 text-lg'>Live Demo Patient</div>
                        <div className='text-xs text-slate-500 mb-3'>ID: LIVE-PATIENT-001</div>
                        <div className='flex justify-between items-center mt-4 border-t pt-3'>
                            <span className='text-[10px] font-bold px-2 py-1 bg-amber-100 text-amber-700 rounded'>NICU ADMITTED</span>
                            <span className='text-xs text-sky-600 font-bold group-hover:underline'>View Profile &rarr;</span>
                        </div>
                    </div>

                    {patients.map(p => (
                        <div key={p.id} className='bg-white rounded-lg border p-5 shadow-sm hover:shadow-md cursor-pointer transition' onClick={() => setSelectedId(p.id)}>
                            <div className='font-bold text-slate-800 text-lg'>{p.name || p.patient_code}</div>
                            <div className='text-xs text-slate-500 mb-3'>ID: {p.id}</div>
                            <div className='flex justify-between items-center mt-4 border-t pt-3'>
                                <span className='text-[10px] font-bold px-2 py-1 bg-slate-100 text-slate-600 rounded'>HISTORICAL</span>
                                <span className='text-xs text-sky-600 font-bold'>View Profile &rarr;</span>
                            </div>
                        </div>
                    ))}
                </div>
            </main>
            
            {selectedId && <PatientDetailModal patientId={selectedId} onClose={() => setSelectedId(null)} />}
        </div>
    );
}

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(<Dashboard />);
"""
with open('frontend/app.jsx', 'w', encoding='utf-8') as f:
    f.write(content)

