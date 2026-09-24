import os
import sys
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

def create_presentation():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    # Theme Colors
    COLOR_NAVY = RGBColor(15, 23, 42)        # #0F172A
    COLOR_DARK_BLUE = RGBColor(30, 41, 59)   # #1E293B
    COLOR_TEAL = RGBColor(2, 132, 199)       # #0284C7
    COLOR_TEAL_LIGHT = RGBColor(224, 242, 254) # #E0F2FE
    COLOR_CYAN = RGBColor(14, 165, 233)      # #0EA5E9
    COLOR_WHITE = RGBColor(255, 255, 255)
    COLOR_BG_LIGHT = RGBColor(241, 245, 249) # #F1F5F9
    COLOR_CARD_BG = RGBColor(255, 255, 255)  # #FFFFFF
    COLOR_CARD_BORDER = RGBColor(226, 232, 240) # #E2E8F0
    COLOR_TEXT_DARK = RGBColor(15, 23, 42)   # #0F172A
    COLOR_TEXT_MUTED = RGBColor(100, 116, 139) # #64748B
    COLOR_EMERALD = RGBColor(5, 150, 105)    # #059669
    COLOR_EMERALD_BG = RGBColor(236, 253, 245) # #ECFDF5
    COLOR_AMBER = RGBColor(217, 119, 6)      # #D97706
    COLOR_AMBER_BG = RGBColor(254, 243, 199) # #FEF3C7
    COLOR_ROSE = RGBColor(220, 38, 38)       # #DC2626
    COLOR_ROSE_BG = RGBColor(254, 226, 226)  # #FEE2E2

    def add_bg(slide, color):
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
        bg.fill.solid()
        bg.fill.fore_color.rgb = color
        bg.line.fill.background()
        return bg

    def add_header(slide, tag_text, title_text, subtitle_text):
        # Category Tag Pill
        tag_box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(0.5), Inches(3.2), Inches(0.35))
        tag_box.fill.solid()
        tag_box.fill.fore_color.rgb = COLOR_TEAL_LIGHT
        tag_box.line.color.rgb = COLOR_TEAL
        tag_box.line.width = Pt(1)
        tf_tag = tag_box.text_frame
        tf_tag.word_wrap = False
        p_tag = tf_tag.paragraphs[0]
        p_tag.text = tag_text.upper()
        p_tag.font.name = "Arial"
        p_tag.font.size = Pt(9.5)
        p_tag.font.bold = True
        p_tag.font.color.rgb = COLOR_TEAL
        p_tag.alignment = PP_ALIGN.CENTER

        # Title
        tb = slide.shapes.add_textbox(Inches(0.8), Inches(0.9), Inches(11.7), Inches(0.6))
        tf = tb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = title_text
        p.font.name = "Arial"
        p.font.size = Pt(22)
        p.font.bold = True
        p.font.color.rgb = COLOR_TEXT_DARK

        # Subtitle
        tb_sub = slide.shapes.add_textbox(Inches(0.8), Inches(1.45), Inches(11.7), Inches(0.4))
        tf_sub = tb_sub.text_frame
        tf_sub.word_wrap = True
        p_sub = tf_sub.paragraphs[0]
        p_sub.text = subtitle_text
        p_sub.font.name = "Arial"
        p_sub.font.size = Pt(11)
        p_sub.font.color.rgb = COLOR_TEXT_MUTED

    # ==========================================
    # SLIDE 1: TITLE SLIDE (Dark Theme)
    # ==========================================
    s1 = prs.slides.add_slide(blank_layout)
    add_bg(s1, COLOR_NAVY)

    # Decorative header bar
    top_bar = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(0.12))
    top_bar.fill.solid()
    top_bar.fill.fore_color.rgb = COLOR_TEAL
    top_bar.line.fill.background()

    # Academic Prototype Badge
    badge = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.2), Inches(1.2), Inches(4.8), Inches(0.4))
    badge.fill.solid()
    badge.fill.fore_color.rgb = RGBColor(30, 41, 59)
    badge.line.color.rgb = COLOR_CYAN
    badge.line.width = Pt(1)
    p = badge.text_frame.paragraphs[0]
    p.text = "RESEARCH & CLINICAL DECISION SUPPORT PROTOTYPE"
    p.font.name = "Arial"
    p.font.size = Pt(9)
    p.font.bold = True
    p.font.color.rgb = COLOR_CYAN
    p.alignment = PP_ALIGN.CENTER

    # Main Project Title
    tb_title = s1.shapes.add_textbox(Inches(1.2), Inches(1.8), Inches(11.0), Inches(1.3))
    p_title = tb_title.text_frame.paragraphs[0]
    p_title.text = "NeoNatal Watch AI"
    p_title.font.name = "Arial"
    p_title.font.size = Pt(44)
    p_title.font.bold = True
    p_title.font.color.rgb = COLOR_WHITE

    # Project Subtitle
    tb_desc = s1.shapes.add_textbox(Inches(1.2), Inches(3.0), Inches(11.0), Inches(0.8))
    p_desc = tb_desc.text_frame.paragraphs[0]
    p_desc.text = "Multi-Modal Longitudinal Clinical Decision Support & Continuous NICU Telemetry System"
    p_desc.font.name = "Arial"
    p_desc.font.size = Pt(18)
    p_desc.font.color.rgb = RGBColor(186, 230, 253)

    # 4 Pillar Feature Badges
    pillars = [
        ("Prenatal Surveillance", "Hadlock EFW & Doppler PI"),
        ("4-Model AI Ensemble", "XGB + CNN-LSTM + Trf + AE"),
        ("Tri-Modal Explainability", "SHAP + Residuals + Attention"),
        ("Continuous Telemetry", "Sub-second Streaming & Alerts")
    ]
    card_w = Inches(2.55)
    gap = Inches(0.25)
    start_x = Inches(1.2)
    for i, (p_title_str, p_sub_str) in enumerate(pillars):
        x = start_x + i * (card_w + gap)
        c = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, Inches(4.1), card_w, Inches(1.3))
        c.fill.solid()
        c.fill.fore_color.rgb = RGBColor(23, 37, 84)
        c.line.color.rgb = RGBColor(56, 189, 248)
        c.line.width = Pt(1)
        tf = c.text_frame
        p1 = tf.paragraphs[0]
        p1.text = p_title_str
        p1.font.bold = True
        p1.font.size = Pt(11)
        p1.font.color.rgb = COLOR_WHITE
        p2 = tf.add_paragraph()
        p2.text = p_sub_str
        p2.font.size = Pt(9.5)
        p2.font.color.rgb = RGBColor(148, 163, 184)

    # Meta Footer
    tb_footer = s1.shapes.add_textbox(Inches(1.2), Inches(6.1), Inches(11.0), Inches(0.6))
    p_foot = tb_footer.text_frame.paragraphs[0]
    p_foot.text = "Validated End-to-End Across 200 Clinical Tests  |  FastAPI + MySQL + React + PyTorch  |  Academic Presentation"
    p_foot.font.name = "Arial"
    p_foot.font.size = Pt(11)
    p_foot.font.color.rgb = RGBColor(148, 163, 184)

    # ==========================================
    # SLIDE 2: THE CLINICAL PROBLEM
    # ==========================================
    s2 = prs.slides.add_slide(blank_layout)
    add_bg(s2, COLOR_BG_LIGHT)
    add_header(s2, "Clinical Problem & Motivation", "The Critical Need for Proactive Neonatal Monitoring",
               "Preterm infants face rapid, silent deterioration where minutes dictate neurological outcomes.")

    cards_s2 = [
        ("Care Continuity Breakdown", COLOR_ROSE, COLOR_ROSE_BG, [
            "Maternal prenatal data remains siloed from post-delivery NICU charts.",
            "Physicians lack immediate fetal trajectory context during acute newborn resuscitation.",
            "Over 40% of maternal preeclampsia warnings fail to trigger proactive NICU staging."
        ]),
        ("Subtle Preterm Deterioration", COLOR_AMBER, COLOR_AMBER_BG, [
            "Neonatal sepsis, intraventricular hemorrhage, and RDS onset are insidious.",
            "Vital signs show micro-variability changes hours before overt clinical collapse.",
            "Conventional static threshold alarms fire only after severe decompensation occurs."
        ]),
        ("Alarm Fatigue & Black-Box AI", COLOR_TEAL, COLOR_TEAL_LIGHT, [
            ">85% of hospital ICU telemetry alerts are clinically non-actionable false alarms.",
            "Doctors distrust opaque AI models that output risk numbers without physiological rationale.",
            "Clinicians require actionable biological explainability (vital contributions & timing)."
        ])
    ]

    card_w = Inches(3.68)
    gap = Inches(0.33)
    start_x = Inches(0.8)
    for i, (title, accent_color, bg_pill, points) in enumerate(cards_s2):
        x = start_x + i * (card_w + gap)
        # Background card
        c = s2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, Inches(2.05), card_w, Inches(4.0))
        c.fill.solid()
        c.fill.fore_color.rgb = COLOR_CARD_BG
        c.line.color.rgb = COLOR_CARD_BORDER
        c.line.width = Pt(1)

        # Header bar on card
        bar = s2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x + Inches(0.2), Inches(2.3), card_w - Inches(0.4), Inches(0.45))
        bar.fill.solid()
        bar.fill.fore_color.rgb = bg_pill
        bar.line.color.rgb = accent_color
        bar.line.width = Pt(1)
        p = bar.text_frame.paragraphs[0]
        p.text = title
        p.font.bold = True
        p.font.size = Pt(11)
        p.font.color.rgb = accent_color
        p.alignment = PP_ALIGN.CENTER

        # Bullets
        tb = s2.shapes.add_textbox(x + Inches(0.2), Inches(2.9), card_w - Inches(0.4), Inches(2.9))
        tf = tb.text_frame
        tf.word_wrap = True
        for j, pt_text in enumerate(points):
            p = tf.paragraphs[0] if j == 0 else tf.add_paragraph()
            p.text = f"• {pt_text}"
            p.font.size = Pt(10.5)
            p.font.color.rgb = COLOR_TEXT_DARK
            p.space_after = Pt(10)

    # Bottom summary callout
    banner = s2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(6.25), Inches(11.73), Inches(0.7))
    banner.fill.solid()
    banner.fill.fore_color.rgb = RGBColor(238, 242, 255)
    banner.line.color.rgb = RGBColor(199, 210, 254)
    p = banner.text_frame.paragraphs[0]
    p.text = "NeoNatal Watch AI Goal: Bridge prenatal care to NICU telemetry with multi-modal AI and clinician-first explainability."
    p.font.bold = True
    p.font.size = Pt(11)
    p.font.color.rgb = RGBColor(67, 56, 202)
    p.alignment = PP_ALIGN.CENTER

    # ==========================================
    # SLIDE 3: LONGITUDINAL SYSTEM ARCHITECTURE
    # ==========================================
    s3 = prs.slides.add_slide(blank_layout)
    add_bg(s3, COLOR_BG_LIGHT)
    add_header(s3, "System Architecture", "Continuous Longitudinal Care Continuum",
               "Tracking the patient across conception, prenatal assessments, delivery, and high-acuity NICU telemetry.")

    stages = [
        ("1. Maternal Profile", "Baseline Clinical Risk", [
            "Demographics (Age, Gravida, Parity)",
            "Hemodynamics: Mean Arterial Pressure (MAP)",
            "Pre-existing: Chronic HTN, Diabetes"
        ], COLOR_TEAL),
        ("2. Prenatal Fetal Tracker", "Growth & Placental Function", [
            "Hadlock Ultrasound (BPD, HC, AC, FL)",
            "Estimated Fetal Weight (EFW) Percentiles",
            "Uterine Artery Doppler (PI & bilateral notch)",
            "Biomarkers: PAPP-A & PlGF serum levels"
        ], COLOR_EMERALD),
        ("3. Newborn & NICU", "Delivery & Admission", [
            "Birth Status: Gestational age, weight, length",
            "APGAR scoring & resuscitation events",
            "NICU Bed Allocation & diagnosis triage",
            "Longitudinal mother-to-infant link"
        ], COLOR_AMBER),
        ("4. Real-Time Telemetry", "Multi-Vital AI Surveillance", [
            "High-frequency HR, SpO2, RR, Temp",
            "60-minute sliding window feature extraction",
            "Ensemble 4-model inference & risk fusion",
            "Tri-modal XAI & WebSocket alert pushes"
        ], COLOR_ROSE)
    ]

    col_w = Inches(2.72)
    gap = Inches(0.28)
    start_x = Inches(0.8)
    for i, (st_name, st_sub, st_bullets, accent) in enumerate(stages):
        x = start_x + i * (col_w + gap)
        c = s3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, Inches(2.1), col_w, Inches(4.0))
        c.fill.solid()
        c.fill.fore_color.rgb = COLOR_CARD_BG
        c.line.color.rgb = COLOR_CARD_BORDER
        c.line.width = Pt(1)

        # Header tag
        tag = s3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x + Inches(0.15), Inches(2.25), col_w - Inches(0.3), Inches(0.55))
        tag.fill.solid()
        tag.fill.fore_color.rgb = accent
        tag.line.fill.background()
        tf = tag.text_frame
        p1 = tf.paragraphs[0]
        p1.text = st_name
        p1.font.bold = True
        p1.font.size = Pt(10.5)
        p1.font.color.rgb = COLOR_WHITE
        p1.alignment = PP_ALIGN.CENTER
        p2 = tf.add_paragraph()
        p2.text = st_sub
        p2.font.size = Pt(8.5)
        p2.font.color.rgb = RGBColor(241, 245, 249)
        p2.alignment = PP_ALIGN.CENTER

        # Bullets
        tb = s3.shapes.add_textbox(x + Inches(0.15), Inches(2.9), col_w - Inches(0.3), Inches(3.0))
        tf = tb.text_frame
        tf.word_wrap = True
        for j, b in enumerate(st_bullets):
            p = tf.paragraphs[0] if j == 0 else tf.add_paragraph()
            p.text = f"• {b}"
            p.font.size = Pt(9.5)
            p.font.color.rgb = COLOR_TEXT_DARK
            p.space_after = Pt(8)

    # Bottom Stat Row
    stat_box = s3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(6.25), Inches(11.73), Inches(0.7))
    stat_box.fill.solid()
    stat_box.fill.fore_color.rgb = COLOR_NAVY
    stat_box.line.fill.background()
    p = stat_box.text_frame.paragraphs[0]
    p.text = "Full Stack Architecture: 18 MySQL Relational Entities  |  28 FastAPI REST Endpoints  |  SSE Telemetry  |  WebSocket Alerts"
    p.font.bold = True
    p.font.size = Pt(11)
    p.font.color.rgb = RGBColor(224, 242, 254)
    p.alignment = PP_ALIGN.CENTER

    # ==========================================
    # SLIDE 4: PRENATAL MODULE & GROWTH TRAJECTORY
    # ==========================================
    s4 = prs.slides.add_slide(blank_layout)
    add_bg(s4, COLOR_BG_LIGHT)
    add_header(s4, "Prenatal Surveillance", "Fetal Biometry, Doppler PI & Placental Biomarkers",
               "Detecting intrauterine growth restriction (IUGR) and placental insufficiency before delivery.")

    cards_s4 = [
        ("Hadlock Fetal Biometry", "Ultrasound Anthropometry", [
            "Computes Estimated Fetal Weight (EFW) using Hadlock multi-parameter formula.",
            "Integrates Biparietal Diameter (BPD), Head Circumference (HC), Abdominal Circumference (AC), and Femur Length (FL).",
            "Evaluates gestational age-specific growth percentiles against standard ±2 standard deviation normal curves.",
            "Early identification of Small-for-Gestational-Age (<10th percentile) and Fetal Macrosomia (>90th percentile)."
        ], COLOR_TEAL),
        ("Uterine Artery Doppler", "Uteroplacental Perfusion", [
            "Measures Uterine Artery Pulsatility Index (UtA-PI) across 1st and 2nd trimesters.",
            "Flags elevated vascular resistance and persistent bilateral diastolic notching.",
            "Provides an early hemodynamic indicator of incomplete trophoblast invasion and impaired spiral artery remodeling.",
            "Strong predictive indicator for early-onset preeclampsia and placental insufficiency."
        ], COLOR_EMERALD),
        ("Maternal Serum Biomarkers", "Biochemical Screening", [
            "Analyzes Pregnancy-Associated Plasma Protein-A (PAPP-A) in early pregnancy.",
            "Tracks Placental Growth Factor (PlGF) as a vascular endothelial health marker.",
            "Normalizes raw laboratory results to Multiples of the Median (MoM).",
            "Low PAPP-A (<0.4 MoM) combined with suppressed PlGF signals acute placental compromise."
        ], COLOR_AMBER)
    ]

    for i, (title, sub, bullets, accent) in enumerate(cards_s4):
        x = start_x + i * (card_w + gap)
        c = s4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, Inches(2.05), card_w, Inches(4.0))
        c.fill.solid()
        c.fill.fore_color.rgb = COLOR_CARD_BG
        c.line.color.rgb = COLOR_CARD_BORDER
        c.line.width = Pt(1)

        bar = s4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x + Inches(0.2), Inches(2.25), card_w - Inches(0.4), Inches(0.55))
        bar.fill.solid()
        bar.fill.fore_color.rgb = accent
        bar.line.fill.background()
        tf = bar.text_frame
        p1 = tf.paragraphs[0]
        p1.text = title
        p1.font.bold = True
        p1.font.size = Pt(11)
        p1.font.color.rgb = COLOR_WHITE
        p1.alignment = PP_ALIGN.CENTER
        p2 = tf.add_paragraph()
        p2.text = sub
        p2.font.size = Pt(8.5)
        p2.font.color.rgb = RGBColor(241, 245, 249)
        p2.alignment = PP_ALIGN.CENTER

        tb = s4.shapes.add_textbox(x + Inches(0.2), Inches(2.95), card_w - Inches(0.4), Inches(2.9))
        tf = tb.text_frame
        tf.word_wrap = True
        for j, b in enumerate(bullets):
            p = tf.paragraphs[0] if j == 0 else tf.add_paragraph()
            p.text = f"• {b}"
            p.font.size = Pt(9.5)
            p.font.color.rgb = COLOR_TEXT_DARK
            p.space_after = Pt(7)

    # Bottom Callout
    banner = s4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(6.25), Inches(11.73), Inches(0.7))
    banner.fill.solid()
    banner.fill.fore_color.rgb = COLOR_EMERALD_BG
    banner.line.color.rgb = COLOR_EMERALD
    p = banner.text_frame.paragraphs[0]
    p.text = "Clinical Outcome: Fetal assessments directly feed newborn admission risk profiles, enabling preemptive NICU bed reservation."
    p.font.bold = True
    p.font.size = Pt(11)
    p.font.color.rgb = COLOR_EMERALD
    p.alignment = PP_ALIGN.CENTER

    # ==========================================
    # SLIDE 5: QUAD-MODEL AI ENGINE
    # ==========================================
    s5 = prs.slides.add_slide(blank_layout)
    add_bg(s5, COLOR_BG_LIGHT)
    add_header(s5, "Multi-Modal AI Engine", "Four Specialized Machine Learning Architectures",
               "Harnessing statistical learning, temporal sequences, self-attention, and unsupervised anomaly detection.")

    models = [
        ("XGBoost", "Tabular & Statistical Features", "Weight: 35%", [
            "Analyzes 15+ engineered statistical features from 60-min window.",
            "Features include rolling mean, standard deviation, min/max, trend slopes, and missingness metrics.",
            "High stability, robust to outliers, calibrated probability score."
        ], COLOR_TEAL),
        ("CNN-LSTM", "Spatio-Temporal Deep Learning", "Weight: 30%", [
            "1D Convolutional layers capture local vital sign morphometry (sharp dips & spikes).",
            "LSTM memory units retain long-term temporal dependencies across the sequence.",
            "Maps multi-vital trajectories to latent deterioration risk."
        ], COLOR_CYAN),
        ("Transformer", "Multi-Head Self-Attention", "Weight: 20%", [
            "Self-attention mechanism assigns weights to key critical time steps.",
            "Detects subtle non-linear vital co-dependencies (e.g. concurrent HR rise & SpO2 fall).",
            "Provides attention weight maps for temporal interpretability."
        ], COLOR_EMERALD),
        ("Autoencoder", "Unsupervised Anomaly Detection", "Weight: 15%", [
            "Encoder-decoder architecture trained purely on stable physiological baselines.",
            "Measures mean squared error (MSE) reconstruction loss.",
            "Detects novel pathological patterns without requiring labeled failure datasets."
        ], COLOR_AMBER)
    ]

    for i, (m_title, m_role, m_wt, m_points, accent) in enumerate(models):
        x = start_x + i * (col_w + gap)
        c = s5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, Inches(2.05), col_w, Inches(4.0))
        c.fill.solid()
        c.fill.fore_color.rgb = COLOR_CARD_BG
        c.line.color.rgb = COLOR_CARD_BORDER
        c.line.width = Pt(1)

        bar = s5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x + Inches(0.15), Inches(2.2), col_w - Inches(0.3), Inches(0.65))
        bar.fill.solid()
        bar.fill.fore_color.rgb = accent
        bar.line.fill.background()
        tf = bar.text_frame
        p1 = tf.paragraphs[0]
        p1.text = m_title
        p1.font.bold = True
        p1.font.size = Pt(12)
        p1.font.color.rgb = COLOR_WHITE
        p1.alignment = PP_ALIGN.CENTER
        p2 = tf.add_paragraph()
        p2.text = f"{m_role}  ({m_wt})"
        p2.font.size = Pt(8.5)
        p2.font.color.rgb = RGBColor(241, 245, 249)
        p2.alignment = PP_ALIGN.CENTER

        tb = s5.shapes.add_textbox(x + Inches(0.15), Inches(2.95), col_w - Inches(0.3), Inches(2.9))
        tf = tb.text_frame
        tf.word_wrap = True
        for j, pt in enumerate(m_points):
            p = tf.paragraphs[0] if j == 0 else tf.add_paragraph()
            p.text = f"• {pt}"
            p.font.size = Pt(9.5)
            p.font.color.rgb = COLOR_TEXT_DARK
            p.space_after = Pt(8)

    # Bottom summary
    bot = s5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(6.25), Inches(11.73), Inches(0.7))
    bot.fill.solid()
    bot.fill.fore_color.rgb = COLOR_NAVY
    bot.line.fill.background()
    p = bot.text_frame.paragraphs[0]
    p.text = "Multi-Model Ensemble Advantage: Eliminates single-model bias and achieves superior AUC compared to isolated classifiers."
    p.font.bold = True
    p.font.size = Pt(11)
    p.font.color.rgb = RGBColor(224, 242, 254)
    p.alignment = PP_ALIGN.CENTER

    # ==========================================
    # SLIDE 6: ENSEMBLE RISK FUSION & DECISION LOGIC
    # ==========================================
    s6 = prs.slides.add_slide(blank_layout)
    add_bg(s6, COLOR_BG_LIGHT)
    add_header(s6, "Risk Fusion & Calibration", "Weighted Consensus & Actionable Clinical Tiers",
               "Transforming multiple model outputs into calibrated, actionable clinical risk levels.")

    # Left: Formula & Rationale Card
    c_left = s6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(2.05), Inches(5.7), Inches(4.0))
    c_left.fill.solid()
    c_left.fill.fore_color.rgb = COLOR_CARD_BG
    c_left.line.color.rgb = COLOR_CARD_BORDER
    c_left.line.width = Pt(1)

    # Formula Banner
    f_bar = s6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.1), Inches(2.25), Inches(5.1), Inches(0.8))
    f_bar.fill.solid()
    f_bar.fill.fore_color.rgb = RGBColor(15, 23, 42)
    f_bar.line.fill.background()
    tf = f_bar.text_frame
    p1 = tf.paragraphs[0]
    p1.text = "CALIBRATED FUSION FORMULA"
    p1.font.bold = True
    p1.font.size = Pt(9.5)
    p1.font.color.rgb = COLOR_CYAN
    p1.alignment = PP_ALIGN.CENTER
    p2 = tf.add_paragraph()
    p2.text = "Risk = 0.35(XGB) + 0.30(CNN-LSTM) + 0.20(Trf) + 0.15(AE)"
    p2.font.bold = True
    p2.font.size = Pt(11)
    p2.font.color.rgb = COLOR_WHITE
    p2.alignment = PP_ALIGN.CENTER

    tb_left = s6.shapes.add_textbox(Inches(1.1), Inches(3.2), Inches(5.1), Inches(2.6))
    tf_l = tb_left.text_frame
    tf_l.word_wrap = True
    f_points = [
        "Clinically Calibrated Weights: XGBoost provides reliable baseline discrimination; CNN-LSTM captures acute trajectory shifts.",
        "Transformer & Autoencoder Harmony: Attention spots temporal crisis ticks while AE captures unmodeled rare physiological anomalies.",
        "Zero Hardcoded Scores: Every score is computed deterministically from multi-modal inference outputs.",
        "Graceful Fallback: System handles missing vitals safely without silent crashes or corrupted predictions."
    ]
    for j, fp in enumerate(f_points):
        p = tf_l.paragraphs[0] if j == 0 else tf_l.add_paragraph()
        p.text = f"• {fp}"
        p.font.size = Pt(9.5)
        p.font.color.rgb = COLOR_TEXT_DARK
        p.space_after = Pt(8)

    # Right: Severity Tiers
    tiers = [
        ("LOW RISK  (< 0.35)", "Normal Baseline Monitoring", [
            "Physiological parameters within normal neonatal ranges.",
            "Routine telemetry logging every 60 seconds; no alarms triggered."
        ], COLOR_EMERALD, COLOR_EMERALD_BG),
        ("WATCH  (0.35 - 0.70)", "Heightened Surveillance", [
            "Subtle trends detected; minor heart rate variability or mild desaturation.",
            "Yellow visual badge on dashboard; prompts nursing re-assessment."
        ], COLOR_AMBER, COLOR_AMBER_BG),
        ("HIGH RISK  (>= 0.70)", "Immediate Bedside Intervention", [
            "Severe multi-vital deterioration or acute anomaly score detected.",
            "Red high-priority WebSocket alarm broadcast; alerts attending physician."
        ], COLOR_ROSE, COLOR_ROSE_BG)
    ]

    tier_h = Inches(1.22)
    tier_gap = Inches(0.17)
    for i, (t_name, t_sub, t_pts, border_col, bg_col) in enumerate(tiers):
        y = Inches(2.05) + i * (tier_h + tier_gap)
        c = s6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.8), y, Inches(5.73), tier_h)
        c.fill.solid()
        c.fill.fore_color.rgb = bg_col
        c.line.color.rgb = border_col
        c.line.width = Pt(1.5)

        tf = c.text_frame
        tf.word_wrap = True
        p1 = tf.paragraphs[0]
        p1.text = f"{t_name} — {t_sub}"
        p1.font.bold = True
        p1.font.size = Pt(11)
        p1.font.color.rgb = border_col

        for pt in t_pts:
            p = tf.add_paragraph()
            p.text = f"• {pt}"
            p.font.size = Pt(9)
            p.font.color.rgb = COLOR_TEXT_DARK

    # Bottom
    b_s6 = s6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(6.25), Inches(11.73), Inches(0.7))
    b_s6.fill.solid()
    b_s6.fill.fore_color.rgb = COLOR_TEAL_LIGHT
    b_s6.line.color.rgb = COLOR_TEAL
    p = b_s6.text_frame.paragraphs[0]
    p.text = "Result: Eliminates nuisance alarms by requiring multi-model consensus before triggering high-priority red alerts."
    p.font.bold = True
    p.font.size = Pt(11)
    p.font.color.rgb = COLOR_TEAL
    p.alignment = PP_ALIGN.CENTER

    # ==========================================
    # SLIDE 7: CLINICIAN-CENTERED EXPLAINABLE AI (XAI)
    # ==========================================
    s7 = prs.slides.add_slide(blank_layout)
    add_bg(s7, COLOR_BG_LIGHT)
    add_header(s7, "Explainable AI (XAI)", "Tri-Modal Interpretability: Unmasking the Black Box",
               "Doctors do not just see an alert; they see WHAT vital, WHEN in time, and WHY the AI raised concern.")

    xai_cards = [
        ("SHAP TreeExplainer", "Feature Importance Attribution", [
            "Computes exact Shapley contribution values for each statistical feature.",
            "Quantifies whether HR standard deviation or SpO2 minimum drove the risk increase.",
            "Generates clear horizontal attribution charts directly in the clinical UI.",
            "Enables doctors to verify that the AI decision aligns with established neonatal physiology."
        ], COLOR_TEAL),
        ("Autoencoder Anomaly Residuals", "Vital-Level Error Breakdown", [
            "Deconstructs total reconstruction error into individual vital channels.",
            "Isolates whether the anomaly stems from Heart Rate, SpO2, Respiratory Rate, or Temp.",
            "Displays baseline expected value alongside actual observed value.",
            "Immediate bedside identification of subtle physiological channel degradation."
        ], COLOR_EMERALD),
        ("Transformer Attention Maps", "Temporal Horizon Localization", [
            "Extracts multi-head attention weights across the 60-minute window.",
            "Pinpoints the exact minute ticks where the model focused its predictive attention.",
            "Displays attention intensity heatmaps directly above continuous vital curves.",
            "Highlights transient physiological events that preceded the alarm."
        ], COLOR_AMBER)
    ]

    for i, (title, sub, bullets, accent) in enumerate(xai_cards):
        x = start_x + i * (card_w + gap)
        c = s7.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, Inches(2.05), card_w, Inches(4.0))
        c.fill.solid()
        c.fill.fore_color.rgb = COLOR_CARD_BG
        c.line.color.rgb = COLOR_CARD_BORDER
        c.line.width = Pt(1)

        bar = s7.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x + Inches(0.2), Inches(2.25), card_w - Inches(0.4), Inches(0.55))
        bar.fill.solid()
        bar.fill.fore_color.rgb = accent
        bar.line.fill.background()
        tf = bar.text_frame
        p1 = tf.paragraphs[0]
        p1.text = title
        p1.font.bold = True
        p1.font.size = Pt(10.5)
        p1.font.color.rgb = COLOR_WHITE
        p1.alignment = PP_ALIGN.CENTER
        p2 = tf.add_paragraph()
        p2.text = sub
        p2.font.size = Pt(8.5)
        p2.font.color.rgb = RGBColor(241, 245, 249)
        p2.alignment = PP_ALIGN.CENTER

        tb = s7.shapes.add_textbox(x + Inches(0.2), Inches(2.95), card_w - Inches(0.4), Inches(2.9))
        tf = tb.text_frame
        tf.word_wrap = True
        for j, b in enumerate(bullets):
            p = tf.paragraphs[0] if j == 0 else tf.add_paragraph()
            p.text = f"• {b}"
            p.font.size = Pt(9.5)
            p.font.color.rgb = COLOR_TEXT_DARK
            p.space_after = Pt(7)

    # Bottom
    b_s7 = s7.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(6.25), Inches(11.73), Inches(0.7))
    b_s7.fill.solid()
    b_s7.fill.fore_color.rgb = COLOR_NAVY
    b_s7.line.fill.background()
    p = b_s7.text_frame.paragraphs[0]
    p.text = "Clinical Trust Paradigm: Explainability transforms raw AI scores into justifiable clinical diagnostic evidence."
    p.font.bold = True
    p.font.size = Pt(11)
    p.font.color.rgb = RGBColor(224, 242, 254)
    p.alignment = PP_ALIGN.CENTER

    # ==========================================
    # SLIDE 8: NICU TELEMETRY & ALERT PIPELINE
    # ==========================================
    s8 = prs.slides.add_slide(blank_layout)
    add_bg(s8, COLOR_BG_LIGHT)
    add_header(s8, "NICU Telemetry & Alerts", "High-Frequency Vital Streaming & Alarm Deduplication",
               "Continuous sub-second telemetry processing with clinical bounds checking and deduplicated emergency broadcasts.")

    cards_s8 = [
        ("Multi-Vital Stream Engine", COLOR_TEAL, [
            "Continuous monitoring of 4 core neonatal vitals:",
            "  - Heart Rate (HR): normal 120-160 bpm",
            "  - Oxygen Saturation (SpO2): normal 92-98%",
            "  - Respiratory Rate (RR): normal 30-60 /min",
            "  - Core Temperature: normal 36.5-37.5 °C",
            "Data ingestion handles sensor noise and missing values via validated imputation."
        ]),
        ("Pathological Event Detection", COLOR_ROSE, [
            "Automated clinical condition flagging:",
            "  - Severe Bradycardia (HR < 100 bpm)",
            "  - Persistent Tachycardia (HR > 180 bpm)",
            "  - Acute Desaturation (SpO2 < 88%)",
            "  - Tachypnea / Apnea (RR < 20 or > 70)",
            "Dual verification: threshold violations corroborated by ML model risk."
        ]),
        ("Smart Alert Management", COLOR_AMBER, [
            "Intelligent Alarm Deduplication:",
            "  - Suppresses repeating transient alarm chimes within 10-minute cooldown periods.",
            "  - Distinguishes motion artifact spikes from sustained decompensation.",
            "Full Doctor Acknowledgment Lifecycle:",
            "  - Logs clinician ID, timestamp, and review notes in MySQL database."
        ])
    ]

    for i, (title, accent, bullets) in enumerate(cards_s8):
        x = start_x + i * (card_w + gap)
        c = s8.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, Inches(2.05), card_w, Inches(4.0))
        c.fill.solid()
        c.fill.fore_color.rgb = COLOR_CARD_BG
        c.line.color.rgb = COLOR_CARD_BORDER
        c.line.width = Pt(1)

        bar = s8.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x + Inches(0.2), Inches(2.25), card_w - Inches(0.4), Inches(0.45))
        bar.fill.solid()
        bar.fill.fore_color.rgb = accent
        bar.line.fill.background()
        p = bar.text_frame.paragraphs[0]
        p.text = title
        p.font.bold = True
        p.font.size = Pt(11)
        p.font.color.rgb = COLOR_WHITE
        p.alignment = PP_ALIGN.CENTER

        tb = s8.shapes.add_textbox(x + Inches(0.2), Inches(2.85), card_w - Inches(0.4), Inches(3.0))
        tf = tb.text_frame
        tf.word_wrap = True
        for j, b in enumerate(bullets):
            p = tf.paragraphs[0] if j == 0 else tf.add_paragraph()
            p.text = b
            p.font.size = Pt(9.5)
            p.font.color.rgb = COLOR_TEXT_DARK
            p.space_after = Pt(6)

    # Bottom
    b_s8 = s8.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(6.25), Inches(11.73), Inches(0.7))
    b_s8.fill.solid()
    b_s8.fill.fore_color.rgb = COLOR_ROSE_BG
    b_s8.line.color.rgb = COLOR_ROSE
    p = b_s8.text_frame.paragraphs[0]
    p.text = "Low Latency Telemetry: SSE delivers continuous sub-second vitals; WebSockets deliver instant bedside emergency alerts."
    p.font.bold = True
    p.font.size = Pt(11)
    p.font.color.rgb = COLOR_ROSE
    p.alignment = PP_ALIGN.CENTER

    # ==========================================
    # SLIDE 9: DOCTOR-FIRST CLINICAL INTERFACE
    # ==========================================
    s9 = prs.slides.add_slide(blank_layout)
    add_bg(s9, COLOR_BG_LIGHT)
    add_header(s9, "Doctor-First Interface", "Clinical Usability & Eye-Comfort Analytics Design",
               "Engineered specifically for clinical decision-making, rapid triage, and reduced cognitive load.")

    ui_cards = [
        ("Eye-Comfort Slate Theme", [
            "Elimination of scanlines, glowing CRT effects, and distracting visual animations.",
            "Soft Slate (#F1F5F9) background with pure elevated white cards (#FFFFFF).",
            "High contrast dark charcoal typography (#0F172A) adhering to WCAG AAA accessibility.",
            "Support for instant Dark Mode toggle for low-lit night-shift NICU environments."
        ], COLOR_TEAL),
        ("7-Tab Deep Inspection Drawer", [
            "Tab 1: Clinical Overview & Priority Summary",
            "Tab 2: Prenatal & Maternal Longitudinal Record",
            "Tab 3: Newborn Birth & NICU Admission Status",
            "Tab 4: Interactive Chart.js Multi-Vital Telemetry",
            "Tab 5: Multi-Modal XAI (SHAP, AE & Attention)",
            "Tab 6: Doctor Reviews, Findings & Prescriptions",
            "Tab 7: Longitudinal Patient Clinical Timeline"
        ], COLOR_EMERALD),
        ("AI Clinical Query Assistant", [
            "Embedded conversational AI assistant right on the patient dashboard.",
            "Doctors can query: 'Summarize latest vitals' or 'Why did risk spike?'.",
            "Retrieves verified database records and generates evidence-based clinical summaries.",
            "Saves nursing staff valuable minutes during handoffs and shift rounds."
        ], COLOR_CYAN)
    ]

    for i, (title, bullets, accent) in enumerate(ui_cards):
        x = start_x + i * (card_w + gap)
        c = s9.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, Inches(2.05), card_w, Inches(4.0))
        c.fill.solid()
        c.fill.fore_color.rgb = COLOR_CARD_BG
        c.line.color.rgb = COLOR_CARD_BORDER
        c.line.width = Pt(1)

        bar = s9.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x + Inches(0.2), Inches(2.25), card_w - Inches(0.4), Inches(0.45))
        bar.fill.solid()
        bar.fill.fore_color.rgb = accent
        bar.line.fill.background()
        p = bar.text_frame.paragraphs[0]
        p.text = title
        p.font.bold = True
        p.font.size = Pt(11)
        p.font.color.rgb = COLOR_WHITE
        p.alignment = PP_ALIGN.CENTER

        tb = s9.shapes.add_textbox(x + Inches(0.2), Inches(2.85), card_w - Inches(0.4), Inches(3.0))
        tf = tb.text_frame
        tf.word_wrap = True
        for j, b in enumerate(bullets):
            p = tf.paragraphs[0] if j == 0 else tf.add_paragraph()
            p.text = f"• {b}"
            p.font.size = Pt(9.5)
            p.font.color.rgb = COLOR_TEXT_DARK
            p.space_after = Pt(7)

    # Bottom
    b_s9 = s9.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(6.25), Inches(11.73), Inches(0.7))
    b_s9.fill.solid()
    b_s9.fill.fore_color.rgb = COLOR_NAVY
    b_s9.line.fill.background()
    p = b_s9.text_frame.paragraphs[0]
    p.text = "Live Interactive Dashboard: https://bhavan-06.github.io/neo_natal_watch_ai/ (Standalone & Connected Modes)"
    p.font.bold = True
    p.font.size = Pt(11)
    p.font.color.rgb = RGBColor(224, 242, 254)
    p.alignment = PP_ALIGN.CENTER

    # ==========================================
    # SLIDE 10: TECHNOLOGY STACK & DATA SCHEMA
    # ==========================================
    s10 = prs.slides.add_slide(blank_layout)
    add_bg(s10, COLOR_BG_LIGHT)
    add_header(s10, "Technology Stack", "Enterprise Full-Stack & Relational Data Engineering",
               "High-performance asynchronous backend coupled with normalized medical relational persistence.")

    tech_pillars = [
        ("FastAPI & Python 3.12", "Backend & Inference API", [
            "Asynchronous Python web server powered by Uvicorn.",
            "28 RESTful endpoints with Pydantic v2 data validation schemas.",
            "Built-in OpenAPI (Swagger) interactive documentation.",
            "PyTorch & Scikit-Learn ML runtime engines."
        ], COLOR_TEAL),
        ("MySQL 8.0 & SQLAlchemy", "Relational Database", [
            "18 normalized clinical entities with strict foreign key constraints.",
            "Alembic automated database migration versioning.",
            "Indexes on patient IDs, newborn codes, and vital timestamps.",
            "Zero data loss across server restarts and handoffs."
        ], COLOR_EMERALD),
        ("React 18 & Tailwind CSS", "Frontend & Telemetry UI", [
            "Componentized declarative UI with real-time state hooks.",
            "Tailwind CSS custom healthcare design token system.",
            "Chart.js interactive multi-vital time-series visualization.",
            "Pure browser portability without complex node build toolchains."
        ], COLOR_AMBER),
        ("Real-Time Communications", "Streaming & Event Bus", [
            "Server-Sent Events (SSE) for sub-second telemetry feeds.",
            "WebSocket full-duplex channel for instant alert broadcasts.",
            "Thread-safe alert deduplication queue.",
            "Graceful fallback to embedded clinical telemetry when offline."
        ], COLOR_CYAN)
    ]

    for i, (t_name, t_sub, t_bullets, accent) in enumerate(tech_pillars):
        x = start_x + i * (col_w + gap)
        c = s10.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, Inches(2.05), col_w, Inches(4.0))
        c.fill.solid()
        c.fill.fore_color.rgb = COLOR_CARD_BG
        c.line.color.rgb = COLOR_CARD_BORDER
        c.line.width = Pt(1)

        bar = s10.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x + Inches(0.15), Inches(2.2), col_w - Inches(0.3), Inches(0.65))
        bar.fill.solid()
        bar.fill.fore_color.rgb = accent
        bar.line.fill.background()
        tf = bar.text_frame
        p1 = tf.paragraphs[0]
        p1.text = t_name
        p1.font.bold = True
        p1.font.size = Pt(11)
        p1.font.color.rgb = COLOR_WHITE
        p1.alignment = PP_ALIGN.CENTER
        p2 = tf.add_paragraph()
        p2.text = t_sub
        p2.font.size = Pt(8.5)
        p2.font.color.rgb = RGBColor(241, 245, 249)
        p2.alignment = PP_ALIGN.CENTER

        tb = s10.shapes.add_textbox(x + Inches(0.15), Inches(2.95), col_w - Inches(0.3), Inches(2.9))
        tf = tb.text_frame
        tf.word_wrap = True
        for j, b in enumerate(t_bullets):
            p = tf.paragraphs[0] if j == 0 else tf.add_paragraph()
            p.text = f"• {b}"
            p.font.size = Pt(9.5)
            p.font.color.rgb = COLOR_TEXT_DARK
            p.space_after = Pt(8)

    # Bottom
    b_s10 = s10.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(6.25), Inches(11.73), Inches(0.7))
    b_s10.fill.solid()
    b_s10.fill.fore_color.rgb = COLOR_NAVY
    b_s10.line.fill.background()
    p = b_s10.text_frame.paragraphs[0]
    p.text = "Production Ready: Containerized via Docker & Docker-Compose with isolated production networks and environments."
    p.font.bold = True
    p.font.size = Pt(11)
    p.font.color.rgb = RGBColor(224, 242, 254)
    p.alignment = PP_ALIGN.CENTER

    # ==========================================
    # SLIDE 11: SYSTEM VALIDATION & PHASE Q METRICS
    # ==========================================
    s11 = prs.slides.add_slide(blank_layout)
    add_bg(s11, COLOR_BG_LIGHT)
    add_header(s11, "Validation & Quality Assurance", "Phase Q End-to-End Validation: 100% Passed",
               "Exhaustive test suite verifying the complete longitudinal workflow, model inference, and safety labeling.")

    # 4 Key Stat Badges
    stat_cards = [
        ("200 / 200", "AUTOMATED TESTS PASSED", "0 Failures  |  100% Success", COLOR_EMERALD, COLOR_EMERALD_BG),
        ("< 1.2s", "END-TO-END INFERENCE", "Sub-second 4-Model Fusion", COLOR_TEAL, COLOR_TEAL_LIGHT),
        ("18 TABLES", "MYSQL SCHEMA VERIFIED", "Full Cascades & Linkages", COLOR_CYAN, RGBColor(240, 249, 255)),
        ("10 PATIENTS", "COHORT JOURNEYS PROVEN", "Maternal to NICU Verified", COLOR_AMBER, COLOR_AMBER_BG)
    ]

    for i, (metric, label, sub, border_c, bg_c) in enumerate(stat_cards):
        x = start_x + i * (col_w + gap)
        c = s11.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, Inches(2.05), col_w, Inches(1.3))
        c.fill.solid()
        c.fill.fore_color.rgb = bg_c
        c.line.color.rgb = border_c
        c.line.width = Pt(1.5)

        tf = c.text_frame
        p1 = tf.paragraphs[0]
        p1.text = metric
        p1.font.bold = True
        p1.font.size = Pt(22)
        p1.font.color.rgb = border_c
        p1.alignment = PP_ALIGN.CENTER

        p2 = tf.add_paragraph()
        p2.text = label
        p2.font.bold = True
        p2.font.size = Pt(8.5)
        p2.font.color.rgb = COLOR_TEXT_DARK
        p2.alignment = PP_ALIGN.CENTER

        p3 = tf.add_paragraph()
        p3.text = sub
        p3.font.size = Pt(8)
        p3.font.color.rgb = COLOR_TEXT_MUTED
        p3.alignment = PP_ALIGN.CENTER

    # Lower Breakdown: 2 Wide Panels
    # Panel 1: Functional Verification Areas
    p1_box = s11.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(3.6), Inches(5.7), Inches(2.45))
    p1_box.fill.solid()
    p1_box.fill.fore_color.rgb = COLOR_CARD_BG
    p1_box.line.color.rgb = COLOR_CARD_BORDER
    p1_box.line.width = Pt(1)

    tf1 = p1_box.text_frame
    tf1.word_wrap = True
    p = tf1.paragraphs[0]
    p.text = "Verified Functional Subsystems"
    p.font.bold = True
    p.font.size = Pt(12)
    p.font.color.rgb = COLOR_TEXT_DARK
    p.space_after = Pt(8)

    checks = [
        "Prenatal Pipeline: Hadlock EFW, UtA Doppler PI, PAPP-A/PlGF lab scoring.",
        "Model Verifications: XGBoost, CNN-LSTM, Transformer, and Autoencoder.",
        "XAI Validations: SHAP attribution values, AE residuals, Attention heatmaps.",
        "Data Streaming: SSE vital generator, WebSocket alert deduplication.",
        "Persistence: MySQL transactions, foreign key cascades, doctor reviews."
    ]
    for ch in checks:
        p = tf1.add_paragraph()
        p.text = f"✓  {ch}"
        p.font.size = Pt(9.5)
        p.font.color.rgb = COLOR_EMERALD
        p.space_after = Pt(4)

    # Panel 2: Safety & Ethical Disclaimers
    p2_box = s11.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.8), Inches(3.6), Inches(5.73), Inches(2.45))
    p2_box.fill.solid()
    p2_box.fill.fore_color.rgb = COLOR_CARD_BG
    p2_box.line.color.rgb = COLOR_CARD_BORDER
    p2_box.line.width = Pt(1)

    tf2 = p2_box.text_frame
    tf2.word_wrap = True
    p = tf2.paragraphs[0]
    p.text = "Clinical Safety & Governance"
    p.font.bold = True
    p.font.size = Pt(12)
    p.font.color.rgb = COLOR_TEXT_DARK
    p.space_after = Pt(8)

    safeties = [
        "Academic Prototype Guardrail: Explicit disclaimers on UI & API headers.",
        "Zero Diagnostic Autonomy: System acts strictly as decision-support.",
        "Zero Fake Forecasts: Forecast limitation audits enforce honest uncertainty.",
        "Data Privacy Protection: Zero hardcoded patient identifiers or secrets.",
        "Reproducible Validation: Automated test suite runnable with single command."
    ]
    for sf in safeties:
        p = tf2.add_paragraph()
        p.text = f"🛡️  {sf}"
        p.font.size = Pt(9.5)
        p.font.color.rgb = COLOR_TEAL
        p.space_after = Pt(4)

    # Bottom
    b_s11 = s11.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(6.25), Inches(11.73), Inches(0.7))
    b_s11.fill.solid()
    b_s11.fill.fore_color.rgb = COLOR_NAVY
    b_s11.line.fill.background()
    p = b_s11.text_frame.paragraphs[0]
    p.text = "Validation Conclusion: Phase Q confirms that the entire longitudinal pipeline operates flawlessly without regressions."
    p.font.bold = True
    p.font.size = Pt(11)
    p.font.color.rgb = RGBColor(224, 242, 254)
    p.alignment = PP_ALIGN.CENTER

    # ==========================================
    # SLIDE 12: DEPLOYMENT & HOSTING
    # ==========================================
    s12 = prs.slides.add_slide(blank_layout)
    add_bg(s12, COLOR_BG_LIGHT)
    add_header(s12, "Deployment & Hosting", "Dual-Mode Deployment: Public Showcase & Production Cloud",
               "Seamlessly transitioning between instant browser demonstration and high-availability containerized backend.")

    c1_dep = s12.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(2.05), Inches(5.7), Inches(4.0))
    c1_dep.fill.solid()
    c1_dep.fill.fore_color.rgb = COLOR_CARD_BG
    c1_dep.line.color.rgb = COLOR_CARD_BORDER
    c1_dep.line.width = Pt(1)

    h1 = s12.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.1), Inches(2.25), Inches(5.1), Inches(0.55))
    h1.fill.solid()
    h1.fill.fore_color.rgb = COLOR_TEAL
    h1.line.fill.background()
    p = h1.text_frame.paragraphs[0]
    p.text = "GitHub Pages Public Showcase"
    p.font.bold = True
    p.font.size = Pt(12)
    p.font.color.rgb = COLOR_WHITE
    p.alignment = PP_ALIGN.CENTER

    tb1 = s12.shapes.add_textbox(Inches(1.1), Inches(2.95), Inches(5.1), Inches(2.9))
    tf1 = tb1.text_frame
    tf1.word_wrap = True
    p_gh = [
        "Live Public URL: https://bhavan-06.github.io/neo_natal_watch_ai/",
        "Automated CI/CD: Deployed automatically via GitHub Actions (.github/workflows/pages.yml).",
        "Standalone Fallback: Embedded clinical data store simulates all 10 verified patient cohorts.",
        "Full Interactivity: Working Chart.js vitals, 7-tab inspection drawer, XAI cards, and doctor reviews without needing a Python server.",
        "Zero Configuration: Accessible from any phone, tablet, or browser worldwide."
    ]
    for j, pt in enumerate(p_gh):
        p = tf1.paragraphs[0] if j == 0 else tf1.add_paragraph()
        p.text = f"• {pt}"
        p.font.size = Pt(9.5)
        p.font.color.rgb = COLOR_TEXT_DARK
        p.space_after = Pt(7)

    c2_dep = s12.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.8), Inches(2.05), Inches(5.73), Inches(4.0))
    c2_dep.fill.solid()
    c2_dep.fill.fore_color.rgb = COLOR_CARD_BG
    c2_dep.line.color.rgb = COLOR_CARD_BORDER
    c2_dep.line.width = Pt(1)

    h2 = s12.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(7.1), Inches(2.25), Inches(5.1), Inches(0.55))
    h2.fill.solid()
    h2.fill.fore_color.rgb = COLOR_EMERALD
    h2.line.fill.background()
    p = h2.text_frame.paragraphs[0]
    p.text = "Dockerized Production Stack"
    p.font.bold = True
    p.font.size = Pt(12)
    p.font.color.rgb = COLOR_WHITE
    p.alignment = PP_ALIGN.CENTER

    tb2 = s12.shapes.add_textbox(Inches(7.1), Inches(2.95), Inches(5.1), Inches(2.9))
    tf2 = tb2.text_frame
    tf2.word_wrap = True
    p_dk = [
        "Dockerfile: Multi-stage build with Python 3.12, PyTorch runtime, and FastAPI server.",
        "Docker Compose: Multi-container orchestration linking FastAPI service with MySQL 8.0.",
        "Cloud Ready: Pre-configured render.yaml and cloud templates for Render / AWS / GCP.",
        "Security Verified: Zero secrets in git repository; strict .env.example parameterization.",
        "Local Run Command: docker-compose up --build executes complete system in 1 step."
    ]
    for j, pt in enumerate(p_dk):
        p = tf2.paragraphs[0] if j == 0 else tf2.add_paragraph()
        p.text = f"• {pt}"
        p.font.size = Pt(9.5)
        p.font.color.rgb = COLOR_TEXT_DARK
        p.space_after = Pt(7)

    # Bottom
    b_s12 = s12.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(6.25), Inches(11.73), Inches(0.7))
    b_s12.fill.solid()
    b_s12.fill.fore_color.rgb = COLOR_NAVY
    b_s12.line.fill.background()
    p = b_s12.text_frame.paragraphs[0]
    p.text = "Dual-Mode Architecture delivers the best of both worlds: Instant demo accessibility + Enterprise cloud scalability."
    p.font.bold = True
    p.font.size = Pt(11)
    p.font.color.rgb = RGBColor(224, 242, 254)
    p.alignment = PP_ALIGN.CENTER

    # ==========================================
    # SLIDE 13: CLINICAL IMPACT, ROADMAP & CONCLUSION (Dark Theme)
    # ==========================================
    s13 = prs.slides.add_slide(blank_layout)
    add_bg(s13, COLOR_NAVY)

    top_bar13 = s13.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(0.12))
    top_bar13.fill.solid()
    top_bar13.fill.fore_color.rgb = COLOR_TEAL
    top_bar13.line.fill.background()

    tb_c_title = s13.shapes.add_textbox(Inches(1.0), Inches(0.7), Inches(11.3), Inches(1.1))
    tf_c = tb_c_title.text_frame
    p = tf_c.paragraphs[0]
    p.text = "Conclusion & Future Clinical Horizon"
    p.font.bold = True
    p.font.size = Pt(28)
    p.font.color.rgb = COLOR_WHITE
    p_sub = tf_c.add_paragraph()
    p_sub.text = "Advancing neonatal care through proactive, interpretable, and continuous intelligence."
    p_sub.font.size = Pt(13)
    p_sub.font.color.rgb = RGBColor(186, 230, 253)

    future_cards = [
        ("1. Hospital EHR & FHIR Link", "Seamless Interoperability", [
            "Integration with HL7 FHIR (Fast Healthcare Interoperability Resources).",
            "Bi-directional sync with Epic Systems and Cerner EHR records.",
            "Automated import of lab panels and ultrasound scans."
        ], COLOR_TEAL),
        ("2. Clinical Observational Trials", "Real-World Evidence", [
            "IRB-approved retrospective observational studies on NICU registries.",
            "Benchmarking against MIMIC-III and physionet clinical databases.",
            "Quantifying sensitivity, specificity, and lead time before deterioration."
        ], COLOR_EMERALD),
        ("3. Bedside Edge Compute", "Incubator Edge Hardware", [
            "Optimizing models with TensorRT for low-power edge computers (NVIDIA Jetson).",
            "Zero cloud latency; fully autonomous monitoring during network outages.",
            "Direct interface with bedside pulse oximeters and ECG monitors."
        ], COLOR_CYAN)
    ]

    for i, (f_title, f_sub, f_bullets, accent) in enumerate(future_cards):
        x = Inches(1.0) + i * (Inches(3.55) + Inches(0.32))
        c = s13.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, Inches(2.2), Inches(3.55), Inches(3.4))
        c.fill.solid()
        c.fill.fore_color.rgb = RGBColor(23, 37, 84)
        c.line.color.rgb = accent
        c.line.width = Pt(1.5)

        tf = c.text_frame
        tf.word_wrap = True
        p1 = tf.paragraphs[0]
        p1.text = f_title
        p1.font.bold = True
        p1.font.size = Pt(12)
        p1.font.color.rgb = COLOR_WHITE
        p2 = tf.add_paragraph()
        p2.text = f_sub
        p2.font.size = Pt(9.5)
        p2.font.color.rgb = accent
        p2.space_after = Pt(12)

        for b in f_bullets:
            p = tf.add_paragraph()
            p.text = f"• {b}"
            p.font.size = Pt(9)
            p.font.color.rgb = RGBColor(226, 232, 240)
            p.space_after = Pt(6)

    # Bottom Contact & Link Card
    foot_box = s13.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.0), Inches(5.9), Inches(11.3), Inches(0.95))
    foot_box.fill.solid()
    foot_box.fill.fore_color.rgb = RGBColor(30, 41, 59)
    foot_box.line.color.rgb = COLOR_CYAN
    foot_box.line.width = Pt(1)

    tf_f = foot_box.text_frame
    p1 = tf_f.paragraphs[0]
    p1.text = "Thank You! Questions & Discussion Welcome"
    p1.font.bold = True
    p1.font.size = Pt(13)
    p1.font.color.rgb = COLOR_WHITE
    p1.alignment = PP_ALIGN.CENTER

    p2 = tf_f.add_paragraph()
    p2.text = "GitHub Repository: github.com/bhavan-06/neo_natal_watch_ai   |   Live Interactive Dashboard: bhavan-06.github.io/neo_natal_watch_ai"
    p2.font.size = Pt(10)
    p2.font.color.rgb = COLOR_CYAN
    p2.alignment = PP_ALIGN.CENTER

    # Save presentation
    output_path = "presentation/NeoNatal_Watch_AI_Presentation.pptx"
    prs.save(output_path)
    print(f"Presentation saved successfully to: {output_path}")

if __name__ == "__main__":
    create_presentation()

