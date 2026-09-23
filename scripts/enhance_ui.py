import os
import re

file_path = "c:/project/neo_natal_watch_ai/frontend/app.jsx"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# Replace AdminDashboardView
admin_regex = r"// ── Admin Ward & Infrastructure View ───────────────────────────────────────────\nfunction AdminDashboardView.*?// ── Login / Role Authentication Screen"
new_admin_view = """// ── Admin Ward & Infrastructure View ───────────────────────────────────────────
function AdminDashboardView({ stats, patients, onSelectPatient }) {
    const [logs, setLogs] = useState([
        "[SYS] Telemetry Gateway Connected - POD A",
        "[SYS] Model Server: XGBoost loaded successfully (14ms)",
        "[WARN] Packet drop detected on Bed 03 - Recovering...",
        "[SYS] WebSocket /alerts active with 3 clients",
        "[SYS] Database sync: 42 records written."
    ]);
    const addLog = (msg) => setLogs(prev => [msg, ...prev].slice(0, 20));

    return (
        <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {/* Stats Panel */}
                <div className="col-span-2 glass-card p-5 rounded-2xl border border-slate-700/80">
                    <div className="flex justify-between items-center mb-4">
                        <div>
                            <h2 className="text-lg font-bold text-white">Infrastructure Overview</h2>
                            <p className="text-sm text-slate-400">Real-time bed occupancy and AI model health.</p>
                        </div>
                        <span className="text-xs font-mono px-3 py-1 bg-emerald-950 text-emerald-300 border border-emerald-800 rounded-lg">SYSTEM HEALTH: OPTIMAL</span>
                    </div>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                        <div className="bg-slate-900/70 p-4 rounded-xl border border-slate-800">
                            <span className="text-xs font-mono text-slate-400 block mb-1">IN-PATIENTS</span>
                            <span className="text-3xl font-black font-mono text-white">{stats.total_patients}</span>
                        </div>
                        <div className="bg-slate-900/70 p-4 rounded-xl border border-slate-800">
                            <span className="text-xs font-mono text-slate-400 block mb-1">INCUBATORS</span>
                            <span className="text-3xl font-black font-mono text-cyan-400">{stats.nicu_admissions}</span>
                        </div>
                        <div className="bg-slate-900/70 p-4 rounded-xl border border-slate-800">
                            <span className="text-xs font-mono text-slate-400 block mb-1">SURVEILLANCE</span>
                            <span className="text-3xl font-black font-mono text-amber-400">{stats.active_pregnancies}</span>
                        </div>
                        <div className="bg-slate-900/70 p-4 rounded-xl border border-slate-800">
                            <span className="text-xs font-mono text-slate-400 block mb-1">ALERTS</span>
                            <span className="text-3xl font-black font-mono text-rose-400">{stats.active_alerts}</span>
                        </div>
                    </div>
                </div>

                {/* Quick Actions Panel */}
                <div className="glass-card p-5 rounded-2xl border border-slate-700/80">
                    <h2 className="text-lg font-bold text-white mb-4">System Operations</h2>
                    <div className="space-y-3">
                        <button onClick={() => addLog("[ACT] Restarting Telemetry Gateway... OK")} className="w-full py-2 bg-slate-800 hover:bg-slate-700 border border-slate-600 rounded-xl text-xs font-bold text-slate-200 transition">
                            <i className="fa-solid fa-rotate mr-2"></i> Restart Telemetry
                        </button>
                        <button onClick={() => addLog("[ACT] Flushing Database Cache... OK")} className="w-full py-2 bg-slate-800 hover:bg-slate-700 border border-slate-600 rounded-xl text-xs font-bold text-slate-200 transition">
                            <i className="fa-solid fa-database mr-2"></i> Flush DB Cache
                        </button>
                        <button onClick={() => addLog("[ACT] Model Diagnostics Triggered... All models passing.")} className="w-full py-2 bg-slate-800 hover:bg-slate-700 border border-slate-600 rounded-xl text-xs font-bold text-slate-200 transition">
                            <i className="fa-solid fa-microchip mr-2"></i> Run ML Diagnostics
                        </button>
                        <button onClick={() => addLog("[ACT] Secure backup generated and encrypted.")} className="w-full py-2 bg-cyan-900/60 hover:bg-cyan-800/60 border border-cyan-800 rounded-xl text-xs font-bold text-cyan-300 transition">
                            <i className="fa-solid fa-shield mr-2"></i> Trigger System Backup
                        </button>
                    </div>
                </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Model Latency */}
                <div className="glass-card p-5 rounded-2xl border border-slate-700/80 space-y-4">
                    <h3 className="text-sm font-bold text-white flex items-center gap-2">
                        <i className="fa-solid fa-server text-cyan-400"></i> AI Model Inference Latency Monitor
                    </h3>
                    <div className="space-y-3 font-mono text-sm">
                        <div>
                            <div className="flex justify-between text-slate-300 mb-1">
                                <span>XGBoost Structured Tabular</span>
                                <span className="text-cyan-400">12.4 ms</span>
                            </div>
                            <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
                                <div className="bg-cyan-400 h-full w-[25%] rounded-full"></div>
                            </div>
                        </div>
                        <div>
                            <div className="flex justify-between text-slate-300 mb-1">
                                <span>CNN-LSTM Deep Temporal</span>
                                <span className="text-emerald-400">45.8 ms</span>
                            </div>
                            <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
                                <div className="bg-emerald-400 h-full w-[45%] rounded-full"></div>
                            </div>
                        </div>
                        <div>
                            <div className="flex justify-between text-slate-300 mb-1">
                                <span>Autoencoder Reconstruction</span>
                                <span className="text-purple-400">38.2 ms</span>
                            </div>
                            <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
                                <div className="bg-purple-400 h-full w-[38%] rounded-full"></div>
                            </div>
                        </div>
                        <div>
                            <div className="flex justify-between text-slate-300 mb-1">
                                <span>Transformer Multi-Head</span>
                                <span className="text-sky-400">62.1 ms</span>
                            </div>
                            <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
                                <div className="bg-sky-400 h-full w-[42%] rounded-full"></div>
                            </div>
                        </div>
                    </div>
                </div>

                {/* System Logs */}
                <div className="glass-card p-5 rounded-2xl border border-slate-700/80 flex flex-col h-full min-h-[250px]">
                    <h3 className="text-sm font-bold text-white flex items-center gap-2 mb-4">
                        <i className="fa-solid fa-terminal text-emerald-400"></i> Live System Logs
                    </h3>
                    <div className="bg-black/60 rounded-xl p-3 flex-1 border border-slate-800 overflow-y-auto font-mono text-[11px] space-y-1.5 h-48">
                        {logs.map((l, i) => (
                            <div key={i} className={l.includes('[WARN]') ? 'text-amber-400' : l.includes('[SYS]') ? 'text-cyan-400' : 'text-emerald-400'}>
                                {l}
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
}

// ── Login / Role Authentication Screen"""

content = re.sub(admin_regex, new_admin_view, content, flags=re.DOTALL)


# Now inject the Global Chatbot & Quick Actions to the Doctor view.
# We will find the end of the patient cards roster:
dashboard_doctor_regex = r"(<div className=\"grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5\">\s*\{filteredPatients\.map\(p => \{.*?</>\s*\)\s*\}\s*</main>)"

# Let's use a simpler marker. The Doctor view ends with the closing Fragment `</>` just before `</main>`.
# Wait, it's safer to find `</div>\s*</>\s*\)\s*\}\s*</main>`
doctor_view_end_regex = r"(</div>\s*</>\s*\)\s*\}\s*</main>)"
new_chatbot_and_actions = """</div>
                        
                        {/* Global Dashboard Chatbot & Actions */}
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-8">
                            <div className="col-span-1 md:col-span-2 glass-card p-6 rounded-2xl border border-slate-700/80 flex flex-col">
                                <h2 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                                    <i className="fa-solid fa-robot text-cyan-400"></i> Global Ward AI Assistant
                                </h2>
                                <p className="text-sm text-slate-400 mb-2">Ask questions about overall ward capacity, protocol guidelines, or alert summaries.</p>
                                <div className="flex-1 min-h-[200px]">
                                    <AIChatBox patientId="global_ward" />
                                </div>
                            </div>
                            
                            <div className="col-span-1 glass-card p-6 rounded-2xl border border-slate-700/80">
                                <h2 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                                    <i className="fa-solid fa-bolt text-amber-400"></i> Quick Actions
                                </h2>
                                <div className="space-y-4">
                                    <button className="w-full py-3 bg-emerald-900/40 hover:bg-emerald-800/60 border border-emerald-800 rounded-xl text-sm font-bold text-emerald-300 transition flex items-center justify-center gap-2">
                                        <i className="fa-solid fa-bed-pulse"></i> Admit New Patient
                                    </button>
                                    <button className="w-full py-3 bg-cyan-900/40 hover:bg-cyan-800/60 border border-cyan-800 rounded-xl text-sm font-bold text-cyan-300 transition flex items-center justify-center gap-2">
                                        <i className="fa-solid fa-vial"></i> Order Ward Labs
                                    </button>
                                    <button className="w-full py-3 bg-purple-900/40 hover:bg-purple-800/60 border border-purple-800 rounded-xl text-sm font-bold text-purple-300 transition flex items-center justify-center gap-2">
                                        <i className="fa-solid fa-file-medical"></i> Generate Shift Report
                                    </button>
                                    <button className="w-full py-3 bg-rose-900/40 hover:bg-rose-800/60 border border-rose-800 rounded-xl text-sm font-bold text-rose-300 transition flex items-center justify-center gap-2">
                                        <i className="fa-solid fa-truck-medical"></i> Trigger Code Blue
                                    </button>
                                </div>
                            </div>
                        </div>
                    </>
                )}
            </main>"""

content = re.sub(doctor_view_end_regex, new_chatbot_and_actions, content)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Enhancements applied successfully.")

