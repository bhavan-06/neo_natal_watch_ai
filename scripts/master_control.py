import os
import re

file_path = "c:/project/neo_natal_watch_ai/frontend/app.jsx"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update AdminDashboardView to accept onFilterChange and make cards clickable
admin_view_sig_regex = r"function AdminDashboardView\(\{ stats, patients, onSelectPatient \}\) \{"
admin_view_sig_replace = r"function AdminDashboardView({ stats, patients, onFilterChange }) {"
content = re.sub(admin_view_sig_regex, admin_view_sig_replace, content)

# 2. Update Admin stats cards to be clickable
content = content.replace(
    '<div className="bg-slate-900/70 p-4 rounded-xl border border-slate-800">\n                            <span className="text-xs font-mono text-slate-400 block mb-1">IN-PATIENTS</span>',
    '<div onClick={() => onFilterChange(\'ALL\')} className="bg-slate-900/70 p-4 rounded-xl border border-slate-800 cursor-pointer hover:border-white transition">\n                            <span className="text-xs font-mono text-slate-400 block mb-1">IN-PATIENTS</span>'
)
content = content.replace(
    '<div className="bg-slate-900/70 p-4 rounded-xl border border-slate-800">\n                            <span className="text-xs font-mono text-slate-400 block mb-1">INCUBATORS</span>',
    '<div onClick={() => onFilterChange(\'NICU\')} className="bg-slate-900/70 p-4 rounded-xl border border-slate-800 cursor-pointer hover:border-cyan-400 transition">\n                            <span className="text-xs font-mono text-slate-400 block mb-1">INCUBATORS</span>'
)
content = content.replace(
    '<div className="bg-slate-900/70 p-4 rounded-xl border border-slate-800">\n                            <span className="text-xs font-mono text-slate-400 block mb-1">SURVEILLANCE</span>',
    '<div onClick={() => onFilterChange(\'PRENATAL\')} className="bg-slate-900/70 p-4 rounded-xl border border-slate-800 cursor-pointer hover:border-amber-400 transition">\n                            <span className="text-xs font-mono text-slate-400 block mb-1">SURVEILLANCE</span>'
)
content = content.replace(
    '<div className="bg-slate-900/70 p-4 rounded-xl border border-slate-800">\n                            <span className="text-xs font-mono text-slate-400 block mb-1">ALERTS</span>',
    '<div onClick={() => {}} className="bg-slate-900/70 p-4 rounded-xl border border-slate-800 cursor-pointer hover:border-rose-400 transition">\n                            <span className="text-xs font-mono text-slate-400 block mb-1">ALERTS</span>'
)


# 3. Modify the Dashboard logic
# We need to change:
# {userRole === 'admin' ? (
#     <AdminDashboardView stats={stats} patients={patients} onSelectPatient={setSelectedId} />
# ) : (
#     <>
#         {/* Clinical Ward Stats */}
dashboard_logic_regex = r"\{userRole === 'admin' \? \(\s*<AdminDashboardView stats=\{stats\} patients=\{patients\} onSelectPatient=\{setSelectedId\} />\s*\) : \(\s*<>\s*\{\/\* Clinical Ward Stats \*\/\}"
dashboard_logic_replace = r"""{userRole === 'admin' && (
                    <AdminDashboardView stats={stats} patients={patients} onFilterChange={setFilter} />
                )}
                
                {userRole === 'doctor' && (
                    <>
                        {/* Clinical Ward Stats */}"""
content = re.sub(dashboard_logic_regex, dashboard_logic_replace, content)


# 4. Remove the closing tag of the doctor view since it's now shared
# Previous was:
#                         </div>
#                     </>
#                 )}
#             </main>
doctor_end_regex = r"(</div>\s*</>\s*\)\s*\})"
# Replace it with just closing the `doctor` fragment, and then keeping the rest outside the condition
doctor_end_replace = r"""</div>
                    </>
                )}"""
# Actually, the original ended with `</>` and `)}` right before `</main>`, but since we added Chatbot below Patient cards, the Chatbot is currently inside the `</>` of the doctor condition!
# Wait, let me check the current structure precisely.
# We previously injected Chatbot by replacing:
# `</div>\s*</>\s*\)\s*\}\s*</main>`
# with `</div>\n{/* Global Chat... */}\n</>\n)}\n</main>`
# So the Chatbot is INSIDE the doctor's `<> ... </>`.
# We need to pull the Search, Filters, Roster, and Chatbot OUTSIDE the `userRole === 'doctor'` condition.

# Let's find exactly where the Doctor's 4 stat cards end.
# They end before `{/* Search and Filters */}`
doctor_stats_end_regex = r"(</div>\s*\{\/\* Search and Filters \*\/\})"
doctor_stats_end_replace = r"""</div>
                    </>
                )}

                {/* Shared Master View: Search, Filters, Patient Roster, Chatbot */}
                {/* Search and Filters */}"""
content = re.sub(doctor_stats_end_regex, doctor_stats_end_replace, content)

# Now remove the `</>\n)}` from the end of the main tag
main_end_regex = r"(</div>\s*</>\s*\)\s*\})\s*</main>"
main_end_replace = r"</div>\n            </main>"
content = re.sub(main_end_regex, main_end_replace, content)


with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Master control and shared views applied successfully.")

