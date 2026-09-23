"""
=============================================================================
NeoNatal Watch AI — Synthetic Data Generator
=============================================================================

⚠️  DEMO / SYNTHETIC DATA — NOT FOR CLINICAL USE ⚠️
This module generates purely simulated vital-sign time-series data
for software development and demonstration purposes ONLY.

This data does NOT represent real patients.
It must NOT be used for clinical decision-making.
It must NOT be presented as real patient data.

The generated patterns are loosely inspired by neonatal physiology
literature for plausibility, but have NOT been clinically validated.
=============================================================================
"""

import numpy as np
import pandas as pd
import os
import json
from datetime import datetime, timedelta
import random
import logging

logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
logger = logging.getLogger("SyntheticDataGenerator")

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 1: Normal Vital Sign Ranges for Synthetic Neonates
# ─────────────────────────────────────────────────────────────────────────────
# These ranges are loosely based on published neonatal reference ranges.
# They are used for SYNTHETIC DATA GENERATION ONLY.
# They are NOT clinical thresholds.

NORMAL_RANGES = {
    "heart_rate": {
        "mean": 140,          # bpm
        "std": 10,            # normal variability
        "min_physiological": 100,
        "max_physiological": 180,
    },
    "spo2": {
        "mean": 96,           # %
        "std": 1.5,           # normal variability
        "min_physiological": 85,
        "max_physiological": 100,
    },
    "respiratory_rate": {
        "mean": 45,           # breaths/min
        "std": 5,             # normal variability
        "min_physiological": 30,
        "max_physiological": 70,
    },
    "temperature": {
        "mean": 37.0,         # °C
        "std": 0.2,           # normal variability
        "min_physiological": 35.5,
        "max_physiological": 38.5,
    },
    "systolic_bp": {
        "mean": 55,           # mmHg
        "std": 5,
        "min_physiological": 35,
        "max_physiological": 90,
    },
    "diastolic_bp": {
        "mean": 30,           # mmHg
        "std": 4,
        "min_physiological": 15,
        "max_physiological": 60,
    },
    "incubator_temperature": {
        "mean": 35.5,         # °C (incubator temp, not body temp)
        "std": 0.3,
        "min_physiological": 32.0,
        "max_physiological": 37.0,
    },
}

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 2: Abnormal Event Definitions
# ─────────────────────────────────────────────────────────────────────────────
# These describe simulated deterioration patterns for software testing.
# They are NOT clinically validated deterioration definitions.

ABNORMAL_EVENTS = {
    "bradycardia_apnea": {
        "description": "Simulated bradycardia with desaturation (common NICU event pattern)",
        "heart_rate_drop": (-50, -30),      # bpm change from baseline
        "spo2_drop": (-12, -8),             # % change from baseline
        "resp_rate_change": (-10, -5),      # breaths/min change
        "temperature_change": (-0.2, 0.0),  # °C change
        "duration_seconds": (30, 120),
        "recovery_seconds": (20, 60),
        "label": 1,
    },
    "hypoxia": {
        "description": "Simulated gradual SpO2 decline",
        "heart_rate_drop": (-10, 10),
        "spo2_drop": (-15, -5),
        "resp_rate_change": (5, 15),
        "temperature_change": (-0.1, 0.2),
        "duration_seconds": (60, 300),
        "recovery_seconds": (30, 90),
        "label": 1,
    },
    "tachycardia": {
        "description": "Simulated tachycardia — can indicate stress or infection",
        "heart_rate_drop": (30, 50),        # positive = increase
        "spo2_drop": (-3, 0),
        "resp_rate_change": (5, 15),
        "temperature_change": (0.3, 0.8),
        "duration_seconds": (120, 600),
        "recovery_seconds": (60, 180),
        "label": 1,
    },
    "temperature_instability": {
        "description": "Simulated temperature deviation with cardiovascular changes",
        "heart_rate_drop": (10, 25),
        "spo2_drop": (-5, 0),
        "resp_rate_change": (5, 10),
        "temperature_change": (0.5, 1.2),
        "duration_seconds": (300, 900),
        "recovery_seconds": (120, 360),
        "label": 1,
    },
}


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 3: Core Generator Functions
# ─────────────────────────────────────────────────────────────────────────────

def _clamp(value: float, lo: float, hi: float) -> float:
    """Clamp a value within physiological bounds."""
    return max(lo, min(hi, value))


def _generate_noise(length: int, std: float, trend: float = 0.0) -> np.ndarray:
    """
    Generate correlated (AR(1)) noise with optional linear trend.
    AR(1) noise is more realistic than pure white noise because real vital
    signs have temporal autocorrelation — the current value depends on the
    previous value.
    """
    noise = np.zeros(length)
    ar_coef = 0.7  # autocorrelation coefficient (makes the signal "sticky")
    noise[0] = np.random.normal(0, std)
    for i in range(1, length):
        noise[i] = ar_coef * noise[i - 1] + np.random.normal(0, std * (1 - ar_coef))
        noise[i] += trend * i
    return noise


def generate_normal_segment(
    n_samples: int,
    sampling_interval_seconds: int = 10,
    seed: int = None,
) -> pd.DataFrame:
    """
    Generate a segment of normal (stable) synthetic vital signs.

    Parameters
    ----------
    n_samples : int
        Number of time-step rows to generate.
    sampling_interval_seconds : int
        How many seconds between each sample (default: 10 seconds).
    seed : int, optional
        Random seed for reproducibility.

    Returns
    -------
    pd.DataFrame
        DataFrame with normal vital sign columns.
        Label column = 0 (normal) for all rows.
    """
    if seed is not None:
        np.random.seed(seed)

    r = NORMAL_RANGES

    df = pd.DataFrame()
    df["heart_rate"] = (
        r["heart_rate"]["mean"]
        + _generate_noise(n_samples, r["heart_rate"]["std"])
    ).clip(
        r["heart_rate"]["min_physiological"],
        r["heart_rate"]["max_physiological"],
    )

    df["spo2"] = (
        r["spo2"]["mean"]
        + _generate_noise(n_samples, r["spo2"]["std"])
    ).clip(
        r["spo2"]["min_physiological"],
        r["spo2"]["max_physiological"],
    )

    df["respiratory_rate"] = (
        r["respiratory_rate"]["mean"]
        + _generate_noise(n_samples, r["respiratory_rate"]["std"])
    ).clip(
        r["respiratory_rate"]["min_physiological"],
        r["respiratory_rate"]["max_physiological"],
    )

    df["temperature"] = (
        r["temperature"]["mean"]
        + _generate_noise(n_samples, r["temperature"]["std"])
    ).clip(
        r["temperature"]["min_physiological"],
        r["temperature"]["max_physiological"],
    )

    df["systolic_bp"] = (
        r["systolic_bp"]["mean"]
        + _generate_noise(n_samples, r["systolic_bp"]["std"])
    ).clip(
        r["systolic_bp"]["min_physiological"],
        r["systolic_bp"]["max_physiological"],
    )

    df["diastolic_bp"] = (
        r["diastolic_bp"]["mean"]
        + _generate_noise(n_samples, r["diastolic_bp"]["std"])
    ).clip(
        r["diastolic_bp"]["min_physiological"],
        r["diastolic_bp"]["max_physiological"],
    )

    df["incubator_temperature"] = (
        r["incubator_temperature"]["mean"]
        + _generate_noise(n_samples, r["incubator_temperature"]["std"])
    ).clip(
        r["incubator_temperature"]["min_physiological"],
        r["incubator_temperature"]["max_physiological"],
    )

    # Ground truth label: 0 = normal (for demonstration only)
    df["deterioration_label"] = 0
    df["clinical_event"] = "none"
    df["data_source"] = "SYNTHETIC"

    # Round for realism
    df["heart_rate"] = df["heart_rate"].round(1)
    df["spo2"] = df["spo2"].round(1)
    df["respiratory_rate"] = df["respiratory_rate"].round(1)
    df["temperature"] = df["temperature"].round(2)
    df["systolic_bp"] = df["systolic_bp"].round(1)
    df["diastolic_bp"] = df["diastolic_bp"].round(1)
    df["incubator_temperature"] = df["incubator_temperature"].round(2)

    return df


def generate_abnormal_segment(
    event_type: str,
    n_samples_before: int = 30,
    n_samples_during: int = 20,
    n_samples_after: int = 30,
    sampling_interval_seconds: int = 10,
    seed: int = None,
) -> pd.DataFrame:
    """
    Generate a simulated vital-sign segment with an abnormal event injected.

    The segment has three phases:
    1. BEFORE  — normal baseline (n_samples_before rows)
    2. DURING  — deterioration event (n_samples_during rows)
    3. AFTER   — recovery (n_samples_after rows)

    Parameters
    ----------
    event_type : str
        One of: 'bradycardia_apnea', 'hypoxia', 'tachycardia', 'temperature_instability'
    n_samples_before : int
        Baseline rows before the event.
    n_samples_during : int
        Rows during the event peak.
    n_samples_after : int
        Recovery rows after the event.
    sampling_interval_seconds : int
        Seconds between samples.
    seed : int, optional
        Random seed.

    Returns
    -------
    pd.DataFrame
        DataFrame with label = 0 (before/after) and label = 1 (during event).
    """
    if seed is not None:
        np.random.seed(seed)

    if event_type not in ABNORMAL_EVENTS:
        raise ValueError(f"Unknown event type '{event_type}'. "
                         f"Choose from: {list(ABNORMAL_EVENTS.keys())}")

    event = ABNORMAL_EVENTS[event_type]
    r = NORMAL_RANGES

    # ── Before segment (normal) ──
    before_df = generate_normal_segment(n_samples_before, sampling_interval_seconds)

    # ── During segment (deterioration) ──
    # Start from the last value of 'before' and apply drift toward the abnormal state
    hr_shift = random.uniform(*event["heart_rate_drop"])
    spo2_shift = random.uniform(*event["spo2_drop"])
    rr_shift = random.uniform(*event["resp_rate_change"])
    temp_shift = random.uniform(*event["temperature_change"])

    during_df = pd.DataFrame()

    # Gradual onset using a sigmoid-like ramp
    ramp = np.linspace(0, 1, n_samples_during)

    during_df["heart_rate"] = (
        r["heart_rate"]["mean"]
        + hr_shift * ramp
        + _generate_noise(n_samples_during, r["heart_rate"]["std"] * 1.5)
    ).clip(r["heart_rate"]["min_physiological"], r["heart_rate"]["max_physiological"])

    during_df["spo2"] = (
        r["spo2"]["mean"]
        + spo2_shift * ramp
        + _generate_noise(n_samples_during, r["spo2"]["std"] * 2)
    ).clip(r["spo2"]["min_physiological"], r["spo2"]["max_physiological"])

    during_df["respiratory_rate"] = (
        r["respiratory_rate"]["mean"]
        + rr_shift * ramp
        + _generate_noise(n_samples_during, r["respiratory_rate"]["std"] * 1.5)
    ).clip(r["respiratory_rate"]["min_physiological"], r["respiratory_rate"]["max_physiological"])

    during_df["temperature"] = (
        r["temperature"]["mean"]
        + temp_shift * ramp
        + _generate_noise(n_samples_during, r["temperature"]["std"])
    ).clip(r["temperature"]["min_physiological"], r["temperature"]["max_physiological"])

    during_df["systolic_bp"] = (
        r["systolic_bp"]["mean"]
        + _generate_noise(n_samples_during, r["systolic_bp"]["std"] * 1.5)
    ).clip(r["systolic_bp"]["min_physiological"], r["systolic_bp"]["max_physiological"])

    during_df["diastolic_bp"] = (
        r["diastolic_bp"]["mean"]
        + _generate_noise(n_samples_during, r["diastolic_bp"]["std"] * 1.5)
    ).clip(r["diastolic_bp"]["min_physiological"], r["diastolic_bp"]["max_physiological"])

    during_df["incubator_temperature"] = (
        r["incubator_temperature"]["mean"]
        + _generate_noise(n_samples_during, r["incubator_temperature"]["std"])
    ).clip(r["incubator_temperature"]["min_physiological"], r["incubator_temperature"]["max_physiological"])

    during_df["deterioration_label"] = 1         # ← event label
    during_df["clinical_event"] = event_type
    during_df["data_source"] = "SYNTHETIC"

    # ── After segment (recovery) ──
    after_df = generate_normal_segment(n_samples_after, sampling_interval_seconds)

    # Combine all three segments
    segment = pd.concat([before_df, during_df, after_df], ignore_index=True)

    # Round
    for col in ["heart_rate", "spo2", "respiratory_rate", "systolic_bp", "diastolic_bp"]:
        segment[col] = segment[col].round(1)
    for col in ["temperature", "incubator_temperature"]:
        segment[col] = segment[col].round(2)

    return segment


def generate_patient_timeline(
    patient_id: str,
    total_hours: float = 24.0,
    sampling_interval_seconds: int = 10,
    event_probability_per_hour: float = 0.2,
    start_time: datetime = None,
    seed: int = None,
) -> pd.DataFrame:
    """
    Generate a complete synthetic vital-sign timeline for one simulated patient.

    The timeline randomly injects abnormal events based on the given probability.

    Parameters
    ----------
    patient_id : str
        Patient identifier string (e.g., 'SYN-001').
    total_hours : float
        Duration of the timeline in hours.
    sampling_interval_seconds : int
        Time step in seconds between observations.
    event_probability_per_hour : float
        Probability of a deterioration event occurring each hour (0.0–1.0).
    start_time : datetime, optional
        Start timestamp. Defaults to current time.
    seed : int, optional
        Random seed.

    Returns
    -------
    pd.DataFrame
        Complete timeline DataFrame with all vital signs, timestamps,
        patient ID, labels, and clinical events.
    """
    if seed is not None:
        np.random.seed(seed)
        random.seed(seed)

    if start_time is None:
        start_time = datetime.now()

    total_seconds = int(total_hours * 3600)
    n_total_samples = total_seconds // sampling_interval_seconds

    logger.info(
        f"Generating timeline for patient {patient_id}: "
        f"{total_hours}h = {n_total_samples} samples "
        f"@ {sampling_interval_seconds}s intervals"
    )

    segments = []
    samples_generated = 0

    while samples_generated < n_total_samples:
        # How many samples remain?
        remaining = n_total_samples - samples_generated

        # Decide: normal segment or event segment?
        if random.random() < (event_probability_per_hour / 6):  # ~per-10-min check
            event_type = random.choice(list(ABNORMAL_EVENTS.keys()))
            n_before = min(random.randint(20, 40), remaining // 3)
            n_during = min(random.randint(10, 25), remaining // 3)
            n_after = min(random.randint(20, 40), remaining - n_before - n_during)

            if n_before + n_during + n_after > remaining:
                n_after = max(0, remaining - n_before - n_during)

            if n_before > 0 and n_during > 0:
                seg = generate_abnormal_segment(
                    event_type=event_type,
                    n_samples_before=n_before,
                    n_samples_during=n_during,
                    n_samples_after=n_after,
                    sampling_interval_seconds=sampling_interval_seconds,
                )
                segments.append(seg)
                samples_generated += len(seg)
                continue

        # Normal segment: generate a chunk of 10–60 minutes
        chunk_size = min(
            random.randint(60, 360),  # 10–60 minutes
            remaining,
        )
        seg = generate_normal_segment(chunk_size, sampling_interval_seconds)
        segments.append(seg)
        samples_generated += len(seg)

    # Combine all segments
    df = pd.concat(segments, ignore_index=True)
    df = df.head(n_total_samples)  # trim to exact length

    # Add timestamps
    timestamps = [
        start_time + timedelta(seconds=i * sampling_interval_seconds)
        for i in range(len(df))
    ]
    df.insert(0, "timestamp", timestamps)
    df.insert(1, "patient_id", patient_id)

    logger.info(
        f"Patient {patient_id}: "
        f"{len(df)} samples, "
        f"{df['deterioration_label'].sum()} event samples "
        f"({df['deterioration_label'].mean() * 100:.1f}% events)"
    )

    return df


def generate_synthetic_dataset(
    n_patients: int = 20,
    hours_per_patient: float = 24.0,
    sampling_interval_seconds: int = 10,
    event_probability_per_hour: float = 0.15,
    output_dir: str = None,
    seed: int = 42,
) -> pd.DataFrame:
    """
    Generate a complete synthetic dataset with multiple simulated patients.

    ⚠️ SYNTHETIC DATA — NOT FOR CLINICAL USE ⚠️

    Parameters
    ----------
    n_patients : int
        Number of synthetic patients to generate.
    hours_per_patient : float
        Hours of data per patient.
    sampling_interval_seconds : int
        Time step between observations.
    event_probability_per_hour : float
        Per-hour probability of injecting an abnormal event.
    output_dir : str, optional
        Directory to save CSV files. If None, data is only returned.
    seed : int
        Master random seed for reproducibility.

    Returns
    -------
    pd.DataFrame
        Combined dataset with all synthetic patients.
    """
    random.seed(seed)
    np.random.seed(seed)

    logger.info("=" * 65)
    logger.info("[WARNING] SYNTHETIC DATA GENERATOR - NOT FOR CLINICAL USE")
    logger.info("=" * 65)
    logger.info(f"Patients:        {n_patients}")
    logger.info(f"Hours/patient:   {hours_per_patient}")
    logger.info(f"Sampling:        {sampling_interval_seconds}s")
    logger.info(f"Event rate:      {event_probability_per_hour:.0%}/hour")
    logger.info(f"Random seed:     {seed}")

    all_patients = []
    start_time_base = datetime(2025, 1, 1, 0, 0, 0)

    for i in range(n_patients):
        patient_id = f"SYN-{i + 1:03d}"
        patient_seed = seed + i

        # Stagger start times slightly for realism
        patient_start = start_time_base + timedelta(hours=random.randint(0, 72))

        df = generate_patient_timeline(
            patient_id=patient_id,
            total_hours=hours_per_patient,
            sampling_interval_seconds=sampling_interval_seconds,
            event_probability_per_hour=event_probability_per_hour,
            start_time=patient_start,
            seed=patient_seed,
        )
        all_patients.append(df)

    combined_df = pd.concat(all_patients, ignore_index=True)

    # Add a clear synthetic marker column
    combined_df["data_warning"] = "SYNTHETIC_DATA_NOT_FOR_CLINICAL_USE"

    logger.info("-" * 65)
    logger.info(f"Total records:   {len(combined_df):,}")
    logger.info(f"Total patients:  {combined_df['patient_id'].nunique()}")
    logger.info(f"Event samples:   {combined_df['deterioration_label'].sum():,}")
    logger.info(
        f"Class balance:   {combined_df['deterioration_label'].mean() * 100:.1f}% events"
    )
    logger.info("=" * 65)

    # Save to disk if requested
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

        # Save combined CSV
        combined_path = os.path.join(output_dir, "synthetic_nicu_vitals.csv")
        combined_df.to_csv(combined_path, index=False)
        logger.info(f"Saved combined dataset: {combined_path}")

        # Save per-patient CSVs
        per_patient_dir = os.path.join(output_dir, "per_patient")
        os.makedirs(per_patient_dir, exist_ok=True)
        for pid in combined_df["patient_id"].unique():
            patient_df = combined_df[combined_df["patient_id"] == pid]
            patient_path = os.path.join(per_patient_dir, f"{pid}.csv")
            patient_df.to_csv(patient_path, index=False)

        # Save metadata
        metadata = {
            "description": "SYNTHETIC DATA — NOT FOR CLINICAL USE",
            "generated_at": datetime.now().isoformat(),
            "n_patients": n_patients,
            "hours_per_patient": hours_per_patient,
            "sampling_interval_seconds": sampling_interval_seconds,
            "event_probability_per_hour": event_probability_per_hour,
            "seed": seed,
            "total_records": len(combined_df),
            "event_rate_percent": float(
                round(combined_df["deterioration_label"].mean() * 100, 2)
            ),
            "columns": list(combined_df.columns),
            "event_types": list(ABNORMAL_EVENTS.keys()),
            "vital_sign_ranges_note": (
                "Ranges inspired by neonatal physiology literature. "
                "NOT clinically validated. For software demonstration only."
            ),
        }
        meta_path = os.path.join(output_dir, "synthetic_metadata.json")
        with open(meta_path, "w") as f:
            json.dump(metadata, f, indent=2)
        logger.info(f"Saved metadata: {meta_path}")

    return combined_df


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 4: Convenience Functions for Streaming Simulation
# ─────────────────────────────────────────────────────────────────────────────

def generate_single_observation(
    patient_id: str,
    timestamp: datetime = None,
    abnormal: bool = False,
    event_type: str = "hypoxia",
) -> dict:
    """
    Generate a single vital-sign observation (one row).

    Used by the real-time streaming simulator.

    Returns
    -------
    dict
        Dictionary of vital sign values with timestamp and patient_id.
    """
    if timestamp is None:
        timestamp = datetime.now()

    r = NORMAL_RANGES

    obs = {
        "timestamp": timestamp.isoformat(),
        "patient_id": patient_id,
        "heart_rate": round(
            _clamp(
                np.random.normal(r["heart_rate"]["mean"], r["heart_rate"]["std"]),
                r["heart_rate"]["min_physiological"],
                r["heart_rate"]["max_physiological"],
            ), 1
        ),
        "spo2": round(
            _clamp(
                np.random.normal(r["spo2"]["mean"], r["spo2"]["std"]),
                r["spo2"]["min_physiological"],
                r["spo2"]["max_physiological"],
            ), 1
        ),
        "respiratory_rate": round(
            _clamp(
                np.random.normal(r["respiratory_rate"]["mean"], r["respiratory_rate"]["std"]),
                r["respiratory_rate"]["min_physiological"],
                r["respiratory_rate"]["max_physiological"],
            ), 1
        ),
        "temperature": round(
            _clamp(
                np.random.normal(r["temperature"]["mean"], r["temperature"]["std"]),
                r["temperature"]["min_physiological"],
                r["temperature"]["max_physiological"],
            ), 2
        ),
        "systolic_bp": round(
            _clamp(
                np.random.normal(r["systolic_bp"]["mean"], r["systolic_bp"]["std"]),
                r["systolic_bp"]["min_physiological"],
                r["systolic_bp"]["max_physiological"],
            ), 1
        ),
        "diastolic_bp": round(
            _clamp(
                np.random.normal(r["diastolic_bp"]["mean"], r["diastolic_bp"]["std"]),
                r["diastolic_bp"]["min_physiological"],
                r["diastolic_bp"]["max_physiological"],
            ), 1
        ),
        "incubator_temperature": round(
            _clamp(
                np.random.normal(r["incubator_temperature"]["mean"], r["incubator_temperature"]["std"]),
                r["incubator_temperature"]["min_physiological"],
                r["incubator_temperature"]["max_physiological"],
            ), 2
        ),
        "clinical_event": "none",
        "data_source": "SYNTHETIC",
        "data_warning": "SYNTHETIC_DATA_NOT_FOR_CLINICAL_USE",
    }

    # Apply abnormal perturbation if requested
    if abnormal and event_type in ABNORMAL_EVENTS:
        ev = ABNORMAL_EVENTS[event_type]
        obs["heart_rate"] = round(_clamp(
            obs["heart_rate"] + random.uniform(*ev["heart_rate_drop"]),
            r["heart_rate"]["min_physiological"],
            r["heart_rate"]["max_physiological"],
        ), 1)
        obs["spo2"] = round(_clamp(
            obs["spo2"] + random.uniform(*ev["spo2_drop"]),
            r["spo2"]["min_physiological"],
            r["spo2"]["max_physiological"],
        ), 1)
        obs["respiratory_rate"] = round(_clamp(
            obs["respiratory_rate"] + random.uniform(*ev["resp_rate_change"]),
            r["respiratory_rate"]["min_physiological"],
            r["respiratory_rate"]["max_physiological"],
        ), 1)
        obs["temperature"] = round(_clamp(
            obs["temperature"] + random.uniform(*ev["temperature_change"]),
            r["temperature"]["min_physiological"],
            r["temperature"]["max_physiological"],
        ), 2)
        obs["clinical_event"] = event_type

    return obs


def print_dataset_summary(df: pd.DataFrame) -> None:
    """Print a summary of the generated synthetic dataset."""
    print("\n" + "=" * 65)
    print("[WARNING] SYNTHETIC DATASET SUMMARY - NOT FOR CLINICAL USE")
    print("=" * 65)
    print(f"Total records   : {len(df):,}")
    print(f"Patients        : {df['patient_id'].nunique()}")
    print(f"Time range      : {df['timestamp'].min()} → {df['timestamp'].max()}")
    print(f"Event samples   : {df['deterioration_label'].sum():,}")
    print(f"Class balance   : {df['deterioration_label'].mean() * 100:.1f}% events")
    print()
    print("Vital sign statistics:")
    vitals = [
        "heart_rate", "spo2", "respiratory_rate",
        "temperature", "systolic_bp", "diastolic_bp",
    ]
    print(df[vitals].describe().round(2).to_string())
    print()
    print("Event type distribution:")
    print(df["clinical_event"].value_counts().to_string())
    print("=" * 65 + "\n")


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 5: Entry Point
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    """
    Run this script directly to generate synthetic data for development.

    Usage:
        python synthetic_generator.py

    Output:
        data/synthetic/synthetic_nicu_vitals.csv
        data/synthetic/per_patient/SYN-001.csv  ... SYN-020.csv
        data/synthetic/synthetic_metadata.json
    """
    output_directory = os.path.join(
        os.path.dirname(              # project root
            os.path.dirname(          # ml/
                os.path.dirname(      # ml/data/
                    os.path.abspath(__file__)
                )
            )
        ),
        "data", "synthetic"
    )

    df = generate_synthetic_dataset(
        n_patients=20,
        hours_per_patient=24.0,
        sampling_interval_seconds=10,
        event_probability_per_hour=0.15,
        output_dir=output_directory,
        seed=42,
    )

    print_dataset_summary(df)
    print(f"✅ Synthetic data saved to: {output_directory}")
    print()
    print("⚠️  REMINDER: This data is SYNTHETIC and NOT for clinical use.")
