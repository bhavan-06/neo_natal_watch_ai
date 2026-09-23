"""
backend/app/services/prenatal_service.py
-----------------------------------------
Authoritative prenatal decision-support service.

Phase M: Enhanced to include full contributing-pattern routing,
evidence traceability, future outcome estimation, and missing-data handling.

IMPORTANT:
- This is a RULE-BASED decision-support service.
- It is NOT a trained ML model.
- All outputs are labeled as application/simulation decision-support outputs.
- All outputs REQUIRE clinician review.
- No autonomous diagnosis or treatment is generated.
"""

from sqlalchemy.orm import Session
from backend.app.db.models import (
    GrowthAnalysis, Pregnancy, FetalAssessment, Prediction,
    MaternalProfile, LabResult, DopplerResult, DoctorReview,
    Prescription, Newborn, NicuAdmission
)
from datetime import datetime
from typing import Optional, Dict, Any, List

# ── Constants ────────────────────────────────────────────────────────────────

# Prediction target key as stored in the database
PRENATAL_PREDICTION_TARGET = 'EFW_PERCENTILE_T2'

# Application-level (non-clinical) thresholds
CRITICAL_EFW_PERCENTILE = 10.0    # actual EFW < 10 triggers CRITICAL flag
CRITICAL_VARIANCE_PP = 30.0       # |delta| >= 30 pp triggers CRITICAL flag

# Lab "low" thresholds (application/simulation only — not clinical cut-offs)
LOW_PLGF_THRESHOLD = 38.0         # pg/mL — app-level only
LOW_PAPP_A_THRESHOLD = 0.5        # MoM — app-level only

# Doppler status keywords indicating high resistance
HIGH_RESISTANCE_KEYWORDS = ["high_resistance", "elevated", "persistently_high", "bilateral_notch"]
ABNORMAL_UMBILICAL_KEYWORDS = ["reduced_end_diastolic", "absent", "reversed"]

# ── Helpers ───────────────────────────────────────────────────────────────────

def _is_high_doppler(status: Optional[str]) -> bool:
    if not status:
        return False
    return any(kw in status.lower() for kw in HIGH_RESISTANCE_KEYWORDS)


def _is_abnormal_umbilical(status: Optional[str]) -> bool:
    if not status:
        return False
    return any(kw in status.lower() for kw in ABNORMAL_UMBILICAL_KEYWORDS)


def _validate_percentile(value: Optional[float], label: str) -> Optional[str]:
    """Returns an error string if invalid, else None."""
    if value is None:
        return None   # missing is handled separately, not an error
    if not isinstance(value, (int, float)):
        return f"{label}: non-numeric value"
    if value < 0 or value > 100:
        return f"{label}: value {value} is outside valid percentile range [0, 100]"
    return None


# ── Main Service ──────────────────────────────────────────────────────────────

def analyze_prenatal_status(db: Session, pregnancy_id: int) -> Dict[str, Any]:
    """
    Full authoritative prenatal analysis for a given pregnancy.

    Returns a structured decision-support dict with:
        - growth variance
        - evaluation status
        - contributing pattern (rule-based)
        - supporting evidence
        - future outcome estimation (application-level heuristic)
        - data gaps

    All outputs are RULE-BASED / HEURISTIC.
    Labels: 'potential contributing pattern', 'requires clinician review'.
    NOT a clinical diagnosis. NOT a trained ML model output.
    """
    result: Dict[str, Any] = {
        "pregnancy_id": pregnancy_id,
        "analysis_type": "RULE_BASED_DECISION_SUPPORT",
        "safety_disclaimer": (
            "SYNTHETIC / ACADEMIC DEMO DATA — NOT FOR CLINICAL USE. "
            "All outputs are application/simulation decision-support labels. "
            "This is NOT a clinical diagnosis. Clinician review required."
        ),
        "evaluation_status": None,
        "growth_variance": None,
        "predicted_efw_percentile": None,
        "actual_efw_percentile": None,
        "contributing_pattern": None,
        "supporting_evidence": {},
        "monitoring_considerations": [],
        "future_outcome_estimation": None,
        "data_gaps": [],
        "validation_errors": [],
        "clinician_review_required": True,
        "generated_at": datetime.utcnow().isoformat(),
    }

    # ── 1. Verify pregnancy ──────────────────────────────────────────────────
    pregnancy = db.query(Pregnancy).filter(Pregnancy.id == pregnancy_id).first()
    if not pregnancy:
        result["evaluation_status"] = "PREGNANCY_NOT_FOUND"
        result["data_gaps"].append("Pregnancy record not found")
        return result

    # ── 2. Maternal Profile ──────────────────────────────────────────────────
    mat_profile = db.query(MaternalProfile).filter(
        MaternalProfile.pregnancy_id == pregnancy_id
    ).order_by(MaternalProfile.recorded_at.desc()).first()

    maternal_ctx: Dict[str, Any] = {}
    if mat_profile:
        maternal_ctx = {
            "maternal_age": mat_profile.maternal_age,
            "bmi": mat_profile.bmi,
            "map_value": mat_profile.map_value,
            "chronic_hypertension": mat_profile.chronic_hypertension,
            "diabetes": mat_profile.diabetes,
            "other_conditions": mat_profile.other_conditions,
        }
    else:
        result["data_gaps"].append("Maternal profile not available")

    result["supporting_evidence"]["maternal_context"] = maternal_ctx

    # ── 3. T1 Fetal Assessment ───────────────────────────────────────────────
    t1_assessment = db.query(FetalAssessment).filter(
        FetalAssessment.pregnancy_id == pregnancy_id,
        FetalAssessment.trimester == 1
    ).order_by(FetalAssessment.assessment_date.desc()).first()

    t1_data: Dict[str, Any] = {}
    if t1_assessment:
        t1_data = {
            "assessment_id": t1_assessment.id,
            "gestational_age_weeks": t1_assessment.gestational_age_weeks,
            "nt": t1_assessment.nt,
            "crl": t1_assessment.crl,
            "nasal_bone": t1_assessment.nasal_bone,
            "efw_percentile": t1_assessment.efw_percentile,
            "assessment_date": t1_assessment.assessment_date.isoformat() if t1_assessment.assessment_date else None,
        }
        err = _validate_percentile(t1_assessment.efw_percentile, "T1 EFW percentile")
        if err:
            result["validation_errors"].append(err)
    else:
        result["data_gaps"].append("Trimester 1 fetal assessment not available")

    result["supporting_evidence"]["trimester_1"] = t1_data

    # ── 4. T1 Prediction (predicted T2 EFW) ─────────────────────────────────
    t1_prediction = db.query(Prediction).filter(
        Prediction.pregnancy_id == pregnancy_id,
        Prediction.target == PRENATAL_PREDICTION_TARGET
    ).order_by(Prediction.created_at.desc()).first()

    predicted_efw = None
    if t1_prediction:
        predicted_efw = t1_prediction.predicted_value
        err = _validate_percentile(predicted_efw, "Predicted EFW percentile")
        if err:
            result["validation_errors"].append(err)
            predicted_efw = None
        result["supporting_evidence"]["t1_prediction"] = {
            "predicted_efw_percentile": predicted_efw,
            "risk_level_at_prediction": t1_prediction.risk_level,
            "prediction_id": t1_prediction.id,
        }
    else:
        result["data_gaps"].append("Trimester 1 prediction for T2 EFW not available")
        result["supporting_evidence"]["t1_prediction"] = None

    result["predicted_efw_percentile"] = predicted_efw

    # ── 5. T2 Fetal Assessment (actual EFW) ─────────────────────────────────
    t2_assessment = db.query(FetalAssessment).filter(
        FetalAssessment.pregnancy_id == pregnancy_id,
        FetalAssessment.trimester == 2,
        FetalAssessment.efw_percentile != None
    ).order_by(FetalAssessment.assessment_date.desc()).first()

    actual_efw = None
    if t2_assessment:
        actual_efw = t2_assessment.efw_percentile
        err = _validate_percentile(actual_efw, "Actual T2 EFW percentile")
        if err:
            result["validation_errors"].append(err)
            actual_efw = None
        result["supporting_evidence"]["trimester_2"] = {
            "assessment_id": t2_assessment.id,
            "gestational_age_weeks": t2_assessment.gestational_age_weeks,
            "actual_efw_percentile": actual_efw,
            "assessment_date": t2_assessment.assessment_date.isoformat() if t2_assessment.assessment_date else None,
        }
    else:
        result["data_gaps"].append("Trimester 2 fetal assessment with EFW percentile not available")
        result["supporting_evidence"]["trimester_2"] = None

    result["actual_efw_percentile"] = actual_efw

    # ── 6. Lab Results ───────────────────────────────────────────────────────
    latest_lab = db.query(LabResult).filter(
        LabResult.pregnancy_id == pregnancy_id
    ).order_by(LabResult.recorded_at.desc()).first()

    lab_data: Dict[str, Any] = {}
    if latest_lab:
        lab_data = {
            "papp_a": latest_lab.papp_a,
            "plgf": latest_lab.plgf,
            "free_beta_hcg": latest_lab.free_beta_hcg,
            "status": latest_lab.status,
        }
    else:
        result["data_gaps"].append("Laboratory results not available")

    result["supporting_evidence"]["lab_results"] = lab_data

    # ── 7. Doppler Results ───────────────────────────────────────────────────
    t2_doppler = db.query(DopplerResult).filter(
        DopplerResult.pregnancy_id == pregnancy_id
    ).order_by(DopplerResult.recorded_at.desc()).first()

    doppler_data: Dict[str, Any] = {}
    if t2_doppler:
        doppler_data = {
            "uterine_artery_pi": t2_doppler.uterine_artery_pi,
            "uterine_artery_status": t2_doppler.uterine_artery_status,
            "umbilical_artery_status": t2_doppler.umbilical_artery_status,
        }
    else:
        result["data_gaps"].append("Doppler results not available")

    result["supporting_evidence"]["doppler"] = doppler_data

    # ── 8. Growth Variance Calculation ──────────────────────────────────────
    if predicted_efw is not None and actual_efw is not None:
        # delta = predicted - actual (positive means actual is less than predicted)
        delta = round(predicted_efw - actual_efw, 2)
        result["growth_variance"] = delta

        # ── 9. Evaluation Status ─────────────────────────────────────────────
        if actual_efw < CRITICAL_EFW_PERCENTILE or abs(delta) >= CRITICAL_VARIANCE_PP:
            result["evaluation_status"] = "CRITICAL_ADAPTIVE_DEVIATION_DETECTED"
        else:
            result["evaluation_status"] = "NORMAL_GROWTH_TRAJECTORY"

        # ── 10. Contributing Pattern Routing ─────────────────────────────────
        if result["evaluation_status"] == "CRITICAL_ADAPTIVE_DEVIATION_DETECTED":
            pattern = _route_contributing_pattern(
                actual_efw=actual_efw,
                delta=delta,
                lab_data=lab_data,
                doppler_data=doppler_data,
                maternal_ctx=maternal_ctx
            )
            result["contributing_pattern"] = pattern
        else:
            result["contributing_pattern"] = {
                "label": "NO_CRITICAL_DEVIATION",
                "description": "Growth trajectory within expected parameters.",
                "requires_clinician_review": False,
            }
    else:
        result["evaluation_status"] = "INSUFFICIENT_DATA_FOR_ANALYSIS"
        if predicted_efw is None:
            result["data_gaps"].append("Cannot calculate variance: predicted EFW missing")
        if actual_efw is None:
            result["data_gaps"].append("Cannot calculate variance: actual T2 EFW missing")

    # ── 11. Future Outcome Estimation (heuristic, not ML) ────────────────────
    result["future_outcome_estimation"] = _estimate_future_trajectory(
        evaluation_status=result["evaluation_status"],
        pregnancy_status=pregnancy.pregnancy_status,
        actual_efw=actual_efw,
        delta=result.get("growth_variance"),
        maternal_ctx=maternal_ctx,
        has_newborn=bool(db.query(Newborn).filter(Newborn.pregnancy_id == pregnancy_id).first()),
        has_nicu=_check_nicu_linkage(db, pregnancy_id),
    )

    # ── 12. Monitoring Considerations ────────────────────────────────────────
    result["monitoring_considerations"] = _build_monitoring_considerations(result)

    return result


def _route_contributing_pattern(
    actual_efw: float,
    delta: float,
    lab_data: Dict,
    doppler_data: Dict,
    maternal_ctx: Dict,
) -> Dict[str, Any]:
    """
    Rule-based pattern routing. Returns a labeled potential contributing pattern
    with supporting evidence. NOT a clinical diagnosis.
    """
    low_plgf = lab_data.get("plgf") is not None and lab_data["plgf"] < LOW_PLGF_THRESHOLD
    low_papp_a = lab_data.get("papp_a") is not None and lab_data["papp_a"] < LOW_PAPP_A_THRESHOLD
    high_ua = _is_high_doppler(doppler_data.get("uterine_artery_status"))
    abnormal_umb = _is_abnormal_umbilical(doppler_data.get("umbilical_artery_status"))
    high_map = maternal_ctx.get("map_value") is not None and maternal_ctx["map_value"] >= 105
    chronic_htn = maternal_ctx.get("chronic_hypertension", False)

    evidence: List[str] = []

    # Pattern 1: Placental insufficiency — low angiogenic markers or uterine artery high resistance
    if high_ua or low_plgf or low_papp_a:
        if high_ua:
            evidence.append(f"Uterine artery PI status: {doppler_data.get('uterine_artery_status', 'high resistance pattern')}")
        if low_plgf:
            evidence.append(f"PlGF: {lab_data.get('plgf')} pg/mL (application-level low threshold: <{LOW_PLGF_THRESHOLD})")
        if low_papp_a:
            evidence.append(f"PAPP-A: {lab_data.get('papp_a')} MoM (application-level low threshold: <{LOW_PAPP_A_THRESHOLD})")

        return {
            "label": "POTENTIAL_PLACENTAL_INSUFFICIENCY_PATTERN",
            "description": (
                "Application/simulation decision-support output: Potential contributing pattern identified. "
                "Evidence suggests possible placental insufficiency-related growth deviation. "
                "Requires clinician review."
            ),
            "supporting_evidence": evidence,
            "requires_clinician_review": True,
        }

    # Pattern 2: FGR with vascular adaptation — abnormal umbilical artery + low EFW
    if abnormal_umb and actual_efw < CRITICAL_EFW_PERCENTILE:
        evidence.append(f"Umbilical artery Doppler: {doppler_data.get('umbilical_artery_status')}")
        evidence.append(f"Actual EFW percentile: {actual_efw} (< {CRITICAL_EFW_PERCENTILE}th)")

        return {
            "label": "POTENTIAL_FGR_WITH_VASCULAR_ADAPTATION_PATTERN",
            "description": (
                "Application/simulation decision-support output: Potential contributing pattern identified. "
                "Evidence suggests fetal growth restriction with vascular adaptation features. "
                "Requires clinician review."
            ),
            "supporting_evidence": evidence,
            "requires_clinician_review": True,
        }

    # Pattern 3: Maternal vascular complication / preeclampsia risk context
    if high_map or chronic_htn:
        if high_map:
            evidence.append(f"MAP: {maternal_ctx.get('map_value')} mmHg (application-level threshold: >=105)")
        if chronic_htn:
            evidence.append("Chronic hypertension: present")

        return {
            "label": "POTENTIAL_MATERNAL_VASCULAR_RISK_PATTERN",
            "description": (
                "Application/simulation decision-support output: Potential contributing pattern identified. "
                "Maternal vascular risk context is present alongside growth deviation. "
                "Requires clinician review."
            ),
            "supporting_evidence": evidence,
            "requires_clinician_review": True,
        }

    # Pattern 4: Constitutionally small / Idiopathic — deviation present but other markers absent
    evidence.append(f"Growth variance: {delta} pp")
    evidence.append(f"Actual EFW percentile: {actual_efw}")
    evidence.append("Uterine artery Doppler: within normal or not elevated")
    evidence.append("Angiogenic markers: within normal or not available")
    evidence.append("Maternal vascular factors: not elevated")

    return {
        "label": "POTENTIAL_CONSTITUTIONAL_SMALL_OR_IDIOPATHIC_PATTERN",
        "description": (
            "Application/simulation decision-support output: Potential contributing pattern identified. "
            "Growth deviation is present, but other supported abnormal markers are absent. "
            "May represent constitutional smallness or idiopathic FGR. "
            "Requires clinician review."
        ),
        "supporting_evidence": evidence,
        "requires_clinician_review": True,
    }


def _estimate_future_trajectory(
    evaluation_status: Optional[str],
    pregnancy_status: Optional[str],
    actual_efw: Optional[float],
    delta: Optional[float],
    maternal_ctx: Dict,
    has_newborn: bool,
    has_nicu: bool,
) -> Dict[str, Any]:
    """
    Application-level heuristic trajectory estimation.
    NOT a trained ML prediction. NOT a clinical prognosis.
    """
    if evaluation_status == "PREGNANCY_NOT_FOUND" or evaluation_status == "INSUFFICIENT_DATA_FOR_ANALYSIS":
        return {
            "trajectory_status": "UNDETERMINED",
            "monitoring_priority": "UNKNOWN",
            "next_assessment_stage": "DATA_COLLECTION_REQUIRED",
            "clinician_review_indicated": True,
            "note": "Insufficient data to estimate trajectory. Clinician review required.",
        }

    if pregnancy_status == "active":
        if evaluation_status == "CRITICAL_ADAPTIVE_DEVIATION_DETECTED":
            return {
                "trajectory_status": "ACTIVE_PREGNANCY_HIGH_MONITORING_PRIORITY",
                "monitoring_priority": "HIGH",
                "next_assessment_stage": "CLOSE_INTERVAL_MONITORING",
                "clinician_review_indicated": True,
                "note": (
                    "Application/simulation output: Active pregnancy with detected growth deviation. "
                    "Consider close-interval monitoring. Review applicable professional guidance. "
                    "Clinician assessment required."
                ),
            }
        else:
            return {
                "trajectory_status": "ACTIVE_PREGNANCY_ROUTINE_MONITORING",
                "monitoring_priority": "ROUTINE",
                "next_assessment_stage": "ROUTINE_NEXT_TRIMESTER_ASSESSMENT",
                "clinician_review_indicated": False,
                "note": "Application/simulation output: Active pregnancy with normal growth trajectory.",
            }

    if has_nicu:
        return {
            "trajectory_status": "POSTNATAL_NICU_PATHWAY",
            "monitoring_priority": "NICU_MONITORING_ACTIVE",
            "next_assessment_stage": "NICU_POSTNATAL_FOLLOWUP",
            "clinician_review_indicated": True,
            "note": "Application/simulation output: Pregnancy has resulted in NICU admission. Refer to NICU monitoring module.",
        }

    if has_newborn:
        return {
            "trajectory_status": "POSTNATAL_DELIVERED",
            "monitoring_priority": "POSTNATAL_ASSESSMENT",
            "next_assessment_stage": "POSTNATAL_NEWBORN_FOLLOWUP",
            "clinician_review_indicated": False,
            "note": "Application/simulation output: Pregnancy has concluded with birth. Postnatal follow-up as appropriate.",
        }

    return {
        "trajectory_status": "COMPLETED_DELIVERED",
        "monitoring_priority": "STANDARD",
        "next_assessment_stage": "OUTCOME_DOCUMENTED",
        "clinician_review_indicated": False,
        "note": "Application/simulation output: Pregnancy appears to have concluded.",
    }


def _check_nicu_linkage(db: Session, pregnancy_id: int) -> bool:
    """Check whether any newborn from this pregnancy has a NICU admission."""
    newborn = db.query(Newborn).filter(Newborn.pregnancy_id == pregnancy_id).first()
    if not newborn:
        return False
    return db.query(NicuAdmission).filter(NicuAdmission.newborn_id == newborn.id).count() > 0


def _build_monitoring_considerations(result: Dict) -> List[str]:
    considerations = []
    if result.get("data_gaps"):
        considerations.append("Additional data collection may be appropriate to complete assessment.")
    if result.get("validation_errors"):
        considerations.append("Data quality issues detected. Review input data validity.")
    if result.get("evaluation_status") == "CRITICAL_ADAPTIVE_DEVIATION_DETECTED":
        considerations.append("Consider clinician review of potential contributing pattern.")
        considerations.append("Review applicable professional guidance for growth deviation management.")
        considerations.append("Additional assessment may be appropriate based on clinical context.")
    pattern = result.get("contributing_pattern")
    if isinstance(pattern, dict) and pattern.get("requires_clinician_review"):
        considerations.append("Clinician review required before any clinical decision.")
    return considerations


# ─── Legacy compatibility wrapper ────────────────────────────────────────────

def analyze_growth_variance(db: Session, pregnancy_id: int):
    """
    Legacy wrapper retained for backward compatibility.
    Calls the new analyze_prenatal_status service and returns a GrowthAnalysis ORM record.
    """
    result = analyze_prenatal_status(db, pregnancy_id)

    if result["evaluation_status"] in ("PREGNANCY_NOT_FOUND", "INSUFFICIENT_DATA_FOR_ANALYSIS"):
        return None

    import json
    pattern_label = None
    if result.get("contributing_pattern"):
        pattern_label = result["contributing_pattern"].get("label")

    analysis = GrowthAnalysis(
        pregnancy_id=pregnancy_id,
        predicted_efw_percentile=result["predicted_efw_percentile"],
        actual_efw_percentile=result["actual_efw_percentile"],
        growth_variance=result["growth_variance"],
        evaluation_status=result["evaluation_status"],
        contributing_patterns=pattern_label,
        model_version="phase_m_rule_based_v1",
        generated_at=datetime.utcnow()
    )
    db.add(analysis)
    db.commit()
    db.refresh(analysis)
    return analysis
