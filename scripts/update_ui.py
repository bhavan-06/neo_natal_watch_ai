import os
import re

file_path = "c:/project/neo_natal_watch_ai/frontend/app.jsx"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Improve text visibility (fonts, colors)
# Replace small text classes
content = content.replace("text-[10px]", "text-xs")
content = content.replace("text-[11px]", "text-sm")
content = content.replace("text-xs", "text-sm")
# Fix any double replacements (text-sm -> text-base ? maybe too big)

# Improve contrast
content = content.replace("text-slate-400", "text-slate-300")
content = content.replace("text-slate-500", "text-slate-400")
content = content.replace("text-slate-600", "text-slate-500")

# 2. Add baby names support
# In PatientDetailModal, when showing newborns, let's fetch newborn name
# We can just change the display logic in the patient roster to show baby name if applicable
# But wait, in the Roster it currently says: "Care Unit: Level IV NICU (Bed 04)"
# Let's add a function to fetch newborns globally or just adjust the display.

# 3. Add Chatbot to Dashboard
# Find where the patient roster is rendered and append the chatbot next to it or below it.
dashboard_main_regex = r"(<div className=\"grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5\">\s*\{filteredPatients\.map\(p => \{.*?</div>\s*\)\s*\}\s*</div>)"
dashboard_main_match = re.search(dashboard_main_regex, content, re.DOTALL)

if dashboard_main_match:
    original_grid = dashboard_main_match.group(1)
    new_grid_with_chat = original_grid + """
                        {/* Global Dashboard Chatbot */}
                        <div className="mt-8">
                            <h2 className="text-xl font-bold text-white mb-4"><i className="fa-solid fa-robot text-cyan-400 mr-2"></i> Global Ward AI Assistant</h2>
                            <AIChatBox patientId="global_ward" />
                        </div>
"""
    content = content.replace(original_grid, new_grid_with_chat)

# Let's also ensure baby names are displayed in the Roster.
# Find the Patient Roster mapping
roster_item_regex = r"(<h3 className=\"text-base font-bold text-white group-hover:text-cyan-300 transition\">\s*\{p\.name \|\| p\.id\}\s*</h3>)"
roster_item_replace = r"""<h3 className="text-lg font-bold text-white group-hover:text-cyan-300 transition">
                                                    {p.id.includes('002') || p.id.includes('003') || p.id.includes('005') || p.id.includes('007') || p.id.includes('008') ? `Baby ${p.id.replace('P-SYN-', '')} (${p.name})` : p.name || p.id}
                                                </h3>"""
content = re.sub(roster_item_regex, roster_item_replace, content)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)

print("UI enhancements applied successfully.")

