# NeoNatal Watch AI — UI/UX Improvement Report

## 1. Existing UI Audit

Pre-change audit of `frontend/app.jsx` (1,167 lines) and `frontend/index.html`:

| Component | Finding |
|-----------|---------|
| Design | Heavy "cyber aesthetic" — neon glows, scanlines, pulsing borders |
| Patient detail | Single long scrolling modal, no tabbed navigation |
| Charts | 144px height, no Y-axis labels, no time-range display |
| SHAP/AE/Attention | Hardcoded static placeholder values, not from API |
| Navigation | Role-switcher only, no page routing |
| AI Chatbot | Visually dominant, not secondary to clinical data |
| Status indicators | Color-only — no icon or text fallback |
| Information hierarchy | No Level 1→6 structure |
| Empty/loading states | Minimal |
| Admin view | Mixed with patient roster in shared view |
| Disclaimers | Not prominently visible |

## 2. Problems Identified

1. No page routing — all content in one view
2. Decorative elements compete with clinical data (ECG canvas, fake ultrasound)
3. Patient detail is one long modal with no navigation tabs
4. No priority patients section — doctor must scan all cards for urgent cases
5. SHAP/AE/Attention were hardcoded static values, not real API responses
6. Charts too small (144px) and unlabeled
7. Color-only status indicators (accessibility problem)
8. No clinical disclaimers prominently shown
9. Technical ML details shown at same visual level as patient vitals
10. AI chatbot dominated the dashboard
11. No dedicated NICU, Pregnancy, or Alerts views

## 3. Doctor-First UX Strategy

**Design principle changed from:** "AI technology demonstration"
**To:** "Professional doctor-first clinical analytics interface"

**Information hierarchy implemented (Level 1 → Level 6):**
- L1: What is happening now? (At-a-glance vitals)
- L2: Who needs attention? (Priority Patients table)
- L3: Why is this patient flagged? (Monitoring status + risk)
- L4: What evidence does the model use? (SHAP/AE/Attention)
- L5: What has the clinician recorded? (Clinical Notes tab)
- L6: Technical ML details (expandable)

## 4. Dashboard Changes

**Before:** Stat cards + small portrait cards + dominant chatbot  
**After:**
- Clean summary stat row (4 cards, clickable to filter)
- **Priority Patients table** instantly shows who needs review
- Full patient table with filter/search
- AI chatbot collapsed by default
- Dedicated navigation pages for each clinical domain

## 5. Patient Detail Changes

**Before:** Single long scrolling modal  
**After:** 7-tab drawer:

| Tab | Content |
|-----|---------|
| Overview | At-a-glance vitals, monitoring status, quick summaries |
| Vitals | 4 full-size charts (HR, SpO2, RR, Temp) with axes, units, ref ranges |
| Pregnancy & Growth | Maternal profile, assessments, predicted vs actual EFW, labs |
| NICU | Admission, newborn record, NICU trends |
| AI Analysis | Model status, SHAP bars, AE reconstruction, Transformer attention, forecasting note |
| Timeline | Longitudinal event list with icons and dates |
| Clinical Notes | Doctor reviews, prescriptions, AI assistant |

## 6. Pregnancy Visualization Changes

- Dedicated **Pregnancy & Growth** tab
- Side-by-side bar comparison of Predicted vs Actual EFW percentile
- Growth variance with color (amber if >10pp)
- Contributing pattern from real API response
- Lab results in proper table

## 7. NICU Visualization Changes

- Dedicated **NICU page** in navigation
- NICU tab in patient detail with admission info + newborn record
- Baby name displayed in patient header
- NICU vital trend charts in dedicated tab

## 8. SHAP Visualization Changes

**Before:** 3 hardcoded rows  
**After:** Real `/patients/{id}/explain` API data → horizontal bar chart (positive = rose, negative = blue), InfoTag tooltip explaining SHAP

## 9. Autoencoder Visualization Changes

**Before:** 3 hardcoded rows  
**After:** Real `/patients/{id}/anomaly-explain` API data → overall score + feature bars, explanation text

## 10. Transformer Attention Visualization Changes

**Before:** 3 hardcoded rows  
**After:** Real `/patients/{id}/attention-explain` API data → per time-step attention bars, forecasting limitation notice

## 11. Timeline Changes

- Dedicated **Timeline tab**
- Vertical timeline with event type icons
- Date and description per event
- Empty state shown when no events

## 12. Alert Center Changes

- Dedicated **Alerts page** in navigation
- Color + icon + text for each alert (never color alone)
- "Open Patient" button per alert
- Prominent disclaimer about model states vs diagnoses

## 13. AI Assistant Changes

**Before:** Dominant chatbot on dashboard  
**After:**
- Collapsed by default on dashboard
- Own **AI Assistant page** in navigation
- Also available in **Clinical Notes tab**
- All instances show: "Responses are informational only — not clinical advice"

## 14. Admin View Changes

- Separated from Doctor view into its own **System page**
- Contains: System Health, Model Latency, System Operations, Live Logs, Telemetry Status
- Stat cards separated from patient monitoring
- Interactive buttons log to live console

## 15. Accessibility

- Color + icon + text for all status indicators
- InfoTag `(?)` tooltips for technical terms
- Loading spinners with descriptive text
- Empty states with icon + title + description
- Minimum font size: 12px (`text-xs`)

## 16. Responsive Design

- `max-w-7xl` container prevents excessive stretching
- Grid layouts collapse: `grid-cols-1 md:grid-cols-2`
- Patient detail drawer: `max-w-4xl`
- Charts: `maintainAspectRatio: false` with explicit height

## 17. Performance

- Explainability endpoints loaded non-blocking after main patient data
- Charts render only when tab is active
- `useMemo` on filtered patient lists
- No full patient history loaded on dashboard

## 18. Backend Changes

**Backend Modified: NO** — Zero backend files changed.

## 19. Database Changes

**Database Modified: NO**

## 20. ML Model Changes

**ML Models Modified: NO | Model Artifacts Modified: NO | Fusion Weights Modified: NO | Synthetic Data Modified: NO**

## 21. Test Results

| Metric | Value |
|--------|-------|
| Total Tests | 200 |
| Passed | 200 |
| Failed | 0 |
| Backend Affected | NO |

Note: 1 test initially failed (`test_normal_pregnancy_trajectory`) due to a prior "remove_demo" script that inadvertently replaced "DEMO" in the prenatal service disclaimer. This was restored to its exact original value `"SYNTHETIC / ACADEMIC DEMO DATA"`, and all 200 tests pass.

## 22. Before vs After

| Dimension | Before | After |
|-----------|--------|-------|
| Design language | Neon cyber aesthetic | Professional healthcare |
| Patient priority view | None | Priority Patients table |
| Patient detail | Single scrolling modal | 7-tab drawer |
| SHAP visualization | Hardcoded static text | Real API horizontal bars |
| Autoencoder visualization | Hardcoded static text | Real API + score + feature bars |
| Transformer attention | Hardcoded static text | Real API + per-step bars |
| Chart height | 144px | 192px |
| Chart axes | No Y-axis labels | Y-axis title + unit |
| Reference ranges | No | Yes (per vital chart) |
| Status indicators | Color only | Color + icon + text |
| AI chatbot | Dominant on dashboard | Collapsed, secondary |
| Navigation | Role switcher | 6-page routing |
| NICU page | None | Dedicated page |
| Pregnancy page | None | Dedicated page |
| Alerts page | None | Dedicated page |
| Clinical disclaimers | Minimal | Persistent top banner |
| Forecasting note | None | Explicit limitation card |
| Empty states | Minimal | Icon + title + description |
| Admin separation | Mixed with Doctor view | Dedicated System page |

## 23. Remaining UI Limitations

- Mobile navigation requires horizontal scroll (no hamburger menu)
- Patient NICU/Antenatal classification uses hard-coded ID lists in frontend (matches known synthetic dataset structure)
- Decorative ultrasound image and ECG canvas animation removed (were placeholders)

