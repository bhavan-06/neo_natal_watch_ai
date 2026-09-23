"""
=============================================================================
NeoNatal Watch AI — Preprocessing Pipeline
=============================================================================

WHAT  : Cleans, resamples, and prepares raw vital sign data for ML models.
WHY   : Raw data has noise, gaps, inconsistent intervals, and different
        scales. Models need clean, normalized, consistently-sampled data.
HOW   : Step-by-step transformations: outlier detection → missing value
        handling → resampling → normalization → window creation →
        patient-level splitting.

INPUT : Raw DataFrame (synthetic, CinC 2019, or PICS-derived)
OUTPUT: Clean train / validation / test DataFrames ready for ML

⚠️  SYNTHETIC / REFERENCE DATA — NOT FOR CLINICAL USE
=============================================================================
"""

import os
import logging
import json
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler, StandardScaler
from sklearn.model_selection import GroupShuffleSplit
import joblib

logger = logging.getLogger("Preprocessing")
logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")

# ─────────────────────────────────────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────────────────────────────────────

VITAL_COLUMNS = [
    "heart_rate",
    "spo2",
    "respiratory_rate",
    "temperature",
    "systolic_bp",
    "diastolic_bp",
]

# Physiological plausibility bounds (used for outlier detection/clamping).
# IMPORTANT: These are NOT clinical alert thresholds.
# They are wide safety nets to catch obviously impossible values.
PHYSIOLOGICAL_BOUNDS = {
    "heart_rate":        (40,  300),   # bpm
    "spo2":              (50,  100),   # %
    "respiratory_rate":  (5,   120),   # breaths/min
    "temperature":       (30,  45),    # °C
    "systolic_bp":       (15,  300),   # mmHg
    "diastolic_bp":      (5,   200),   # mmHg
}

LABEL_COLUMN  = "deterioration_label"
TIME_COLUMN   = "timestamp"
PATIENT_COLUMN = "patient_id"


# ─────────────────────────────────────────────────────────────────────────────
# STEP 1: VALIDATE INPUT
# ─────────────────────────────────────────────────────────────────────────────

def validate_dataframe(df: pd.DataFrame, source: str = "unknown") -> pd.DataFrame:
    """
    WHAT: Checks that the DataFrame has all required columns and correct types.
    WHY:  Fail fast with a clear error message rather than a confusing crash later.

    Parameters
    ----------
    df     : Raw input DataFrame.
    source : Name of the data source (for logging).

    Returns
    -------
    df : Validated (and lightly coerced) DataFrame.
    """
    required_cols = [PATIENT_COLUMN, TIME_COLUMN] + VITAL_COLUMNS
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        raise ValueError(
            f"[{source}] Missing required columns: {missing}. "
            f"Available: {list(df.columns)}"
        )

    # Ensure timestamp is datetime
    if not pd.api.types.is_datetime64_any_dtype(df[TIME_COLUMN]):
        df[TIME_COLUMN] = pd.to_datetime(df[TIME_COLUMN], errors="coerce")

    # Ensure vital signs are float
    for col in VITAL_COLUMNS:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Ensure label column exists; if not, add NaN (unsupervised mode)
    if LABEL_COLUMN not in df.columns:
        df[LABEL_COLUMN] = np.nan
        logger.warning(f"[{source}] No label column found. Added NaN column.")

    logger.info(f"[{source}] Validation OK — {len(df):,} rows, {df[PATIENT_COLUMN].nunique()} patients")
    return df


# ─────────────────────────────────────────────────────────────────────────────
# STEP 2: OUTLIER DETECTION AND CLAMPING
# ─────────────────────────────────────────────────────────────────────────────

def detect_and_clamp_outliers(
    df: pd.DataFrame,
    z_threshold: float = 4.0,
    use_physiological_bounds: bool = True,
    report: bool = True,
) -> Tuple[pd.DataFrame, Dict]:
    """
    WHAT: Identifies and neutralizes physiologically impossible or statistically
          extreme values.
    WHY:  A single corrupted sensor reading (e.g. HR = 999) would destroy
          model predictions. We must handle this robustly.

    Two-stage approach:
      Stage 1 — Physiological bounds: Clamp values outside known possible
                 human ranges to NaN (they'll be filled in Step 3).
      Stage 2 — Z-score detection: Flag per-patient z-score outliers for logging
                 (we do NOT remove them — just flag for audit).

    Parameters
    ----------
    df                       : Validated DataFrame.
    z_threshold              : Z-score above which a value is flagged (not removed).
    use_physiological_bounds : Whether to apply hard physiological limits.
    report                   : Whether to print an outlier report.

    Returns
    -------
    df_clean : DataFrame with physiologically impossible values set to NaN.
    report_d : Dictionary summarising what was found.
    """
    df = df.copy()
    report_d = {}

    for col in VITAL_COLUMNS:
        if col not in df.columns:
            continue

        n_before = df[col].notna().sum()
        n_out_phys = 0

        # Stage 1: Physiological bounds
        if use_physiological_bounds and col in PHYSIOLOGICAL_BOUNDS:
            lo, hi = PHYSIOLOGICAL_BOUNDS[col]
            mask_out = (df[col] < lo) | (df[col] > hi)
            n_out_phys = mask_out.sum()
            if n_out_phys > 0:
                df.loc[mask_out, col] = np.nan

        # Stage 2: Per-patient Z-score flag (for audit only, not removal)
        z_flagged = 0
        for pid in df[PATIENT_COLUMN].unique():
            patient_mask = df[PATIENT_COLUMN] == pid
            col_vals = df.loc[patient_mask, col]
            mean = col_vals.mean()
            std  = col_vals.std()
            if std > 0:
                z_scores = np.abs((col_vals - mean) / std)
                z_flagged += (z_scores > z_threshold).sum()

        report_d[col] = {
            "n_total":        int(n_before),
            "phys_clamped":   int(n_out_phys),
            "z_flagged":      int(z_flagged),
            "pct_clamped":    round(n_out_phys / max(n_before, 1) * 100, 3),
        }

    if report:
        logger.info("Outlier detection report:")
        for col, stats in report_d.items():
            logger.info(
                f"  {col:<22}: phys_clamped={stats['phys_clamped']:>5}  "
                f"z_flagged={stats['z_flagged']:>5}"
            )

    return df, report_d


# ─────────────────────────────────────────────────────────────────────────────
# STEP 3: MISSING VALUE HANDLING
# ─────────────────────────────────────────────────────────────────────────────

def handle_missing_values(
    df: pd.DataFrame,
    max_gap_minutes: int = 30,
    forward_fill_limit: int = 6,
    add_missingness_flags: bool = True,
) -> pd.DataFrame:
    """
    WHAT: Fills in missing vital sign values using medically appropriate methods.
    WHY:  Real ICU data (CinC 2019, MIMIC-III) has 60–90% missing values per
          column because nurses don't record vitals at fixed intervals. Models
          can't handle NaN — we must decide how to fill them.

    Strategy (in order):
      1. Add binary "was_missing" indicator columns (BEFORE filling).
         These preserve the information that data WAS missing.
      2. Linear interpolation within small gaps (< max_gap_minutes).
         Scientifically justified: vital signs change gradually between valid readings.
      3. Limited forward-fill for any remaining small gaps.
      4. Median fill (per patient) for any remaining NaN after the above.
         Uses patient-specific median, NOT global median — avoids leaking
         population statistics into individual patients.

    IMPORTANT DECISIONS:
      - We do NOT interpolate across large gaps (> max_gap_minutes) because
        we cannot guess what happened during a long gap.
      - We always add missingness indicator columns — these are features too!

    Parameters
    ----------
    df                   : DataFrame after outlier handling (may have NaN).
    max_gap_minutes      : Gaps larger than this will NOT be interpolated.
    forward_fill_limit   : Max consecutive rows to forward-fill.
    add_missingness_flags: Whether to add binary missing indicator columns.

    Returns
    -------
    df : DataFrame with missing values filled and indicator columns added.
    """
    df = df.copy()
    df = df.sort_values([PATIENT_COLUMN, TIME_COLUMN])

    # Step 3a: Add binary missingness indicator columns (do this FIRST)
    if add_missingness_flags:
        for col in VITAL_COLUMNS:
            if col in df.columns:
                flag_col = f"{col}_was_missing"
                df[flag_col] = df[col].isnull().astype(int)

    # Step 3b & 3c: Per-patient interpolation + forward-fill
    for pid in df[PATIENT_COLUMN].unique():
        mask = df[PATIENT_COLUMN] == pid
        patient_df = df.loc[mask].copy()

        for col in VITAL_COLUMNS:
            if col not in patient_df.columns:
                continue

            series = patient_df[col]

            # Interpolate only within small gaps
            # Limit = number of consecutive NaN rows allowed in linear interp
            # 1 minute resampled data: max_gap_minutes rows = max gap
            series_interp = series.interpolate(
                method="linear",
                limit=max_gap_minutes,
                limit_direction="forward",
            )
            # Forward-fill residual small gaps
            series_ffill = series_interp.ffill(limit=forward_fill_limit)

            patient_df[col] = series_ffill

        df.loc[mask] = patient_df

    # Step 3d: Fill any remaining NaN with per-patient median
    for pid in df[PATIENT_COLUMN].unique():
        mask = df[PATIENT_COLUMN] == pid
        for col in VITAL_COLUMNS:
            if col not in df.columns:
                continue
            n_remaining = df.loc[mask, col].isnull().sum()
            if n_remaining > 0:
                median_val = df.loc[mask, col].median()
                if pd.isna(median_val):
                    # Fallback: global median for this column
                    median_val = df[col].median()
                df.loc[mask & df[col].isnull(), col] = median_val

    total_remaining_nan = df[VITAL_COLUMNS].isnull().sum().sum()
    logger.info(f"Missing value handling complete. Remaining NaN: {total_remaining_nan}")
    return df


# ─────────────────────────────────────────────────────────────────────────────
# STEP 4: TIMESTAMP NORMALIZATION AND RESAMPLING
# ─────────────────────────────────────────────────────────────────────────────

def resample_to_regular_intervals(
    df: pd.DataFrame,
    target_seconds: int = 60,
    aggregation: str = "mean",
) -> pd.DataFrame:
    """
    WHAT: Converts irregular or high-frequency data to a fixed, regular time grid.
    WHY:  ML models (especially LSTM and Transformer) expect evenly-spaced
          time steps. Raw data may be sampled at 10s, 500Hz (waveforms), or
          irregular clinical intervals. We standardize to 1 minute.

    For the label column, we use 'max' aggregation:
      If ANY sample in the 1-minute window is labeled as an event (1),
      the entire window gets label = 1.
      This is a conservative approach — we don't want to miss events.

    Parameters
    ----------
    df             : Cleaned DataFrame with valid timestamps.
    target_seconds : Target interval in seconds (default: 60 = 1 minute).
    aggregation    : How to aggregate: 'mean' (default) or 'median'.

    Returns
    -------
    df_resampled : DataFrame at the target sampling rate.
    """
    df = df.copy()
    df = df.sort_values([PATIENT_COLUMN, TIME_COLUMN])

    rule = f"{target_seconds}s"
    all_patients = []

    for pid in df[PATIENT_COLUMN].unique():
        patient_df = df[df[PATIENT_COLUMN] == pid].copy()
        patient_df = patient_df.set_index(TIME_COLUMN)

        # Build agg dict: vitals → aggregation method
        agg_dict = {}
        for col in VITAL_COLUMNS:
            if col in patient_df.columns:
                agg_dict[col] = aggregation

        # Label: use MAX (any event in window → window is labeled)
        if LABEL_COLUMN in patient_df.columns:
            agg_dict[LABEL_COLUMN] = "max"

        # Missingness flags: use MAX (if any was missing, flag = 1)
        flag_cols = [c for c in patient_df.columns if c.endswith("_was_missing")]
        for fc in flag_cols:
            agg_dict[fc] = "max"

        # Resample
        resampled = patient_df[list(agg_dict.keys())].resample(rule).agg(agg_dict)
        resampled[PATIENT_COLUMN] = pid

        # Fill any NaN introduced by resampling (gaps between samples)
        for col in VITAL_COLUMNS:
            if col in resampled.columns:
                resampled[col] = resampled[col].ffill(limit=5).bfill(limit=2)

        resampled = resampled.reset_index()
        resampled = resampled.rename(columns={"index": TIME_COLUMN})

        all_patients.append(resampled)

    df_resampled = pd.concat(all_patients, ignore_index=True)

    logger.info(
        f"Resampled to {target_seconds}s intervals: "
        f"{len(df_resampled):,} rows "
        f"(was {len(df):,})"
    )
    return df_resampled


# ─────────────────────────────────────────────────────────────────────────────
# STEP 5: NORMALIZATION / SCALING
# ─────────────────────────────────────────────────────────────────────────────

def fit_scaler(
    df_train: pd.DataFrame,
    method: str = "minmax",
    save_path: Optional[str] = None,
) -> object:
    """
    WHAT: Fits a scaler on the TRAINING data only.
    WHY:  Models work best when all features are on the same scale (e.g. 0–1).
          Without scaling, heart rate (100–180) would dominate temperature (36–38).

    CRITICAL: The scaler is ONLY fit on training data.
    It is then APPLIED to validation and test data.
    Fitting on all data would cause data leakage (the model would indirectly
    see test data statistics during training).

    Parameters
    ----------
    df_train  : Training split only.
    method    : 'minmax' (0–1 range) or 'standard' (zero mean, unit variance).
    save_path : Optional path to save the fitted scaler (for inference).

    Returns
    -------
    scaler : Fitted sklearn scaler object.
    """
    cols_to_scale = [c for c in VITAL_COLUMNS if c in df_train.columns]

    if method == "minmax":
        scaler = MinMaxScaler(feature_range=(0, 1))
    elif method == "standard":
        scaler = StandardScaler()
    else:
        raise ValueError(f"Unknown scaler method: '{method}'. Use 'minmax' or 'standard'.")

    scaler.fit(df_train[cols_to_scale])

    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        joblib.dump(scaler, save_path)
        logger.info(f"Scaler saved: {save_path}")

    logger.info(f"Fitted {method} scaler on {len(df_train):,} training rows")
    return scaler


def apply_scaler(
    df: pd.DataFrame,
    scaler,
    cols: Optional[List[str]] = None,
) -> pd.DataFrame:
    """
    WHAT: Applies a pre-fitted scaler to a DataFrame.
    WHY:  We use the same scaler (fit on train only) to scale val and test data.

    Parameters
    ----------
    df     : DataFrame to scale (train, val, or test).
    scaler : Pre-fitted scaler.
    cols   : Which columns to scale (defaults to VITAL_COLUMNS).

    Returns
    -------
    df_scaled : DataFrame with vital columns scaled.
    """
    df = df.copy()
    if cols is None:
        cols = [c for c in VITAL_COLUMNS if c in df.columns]

    df[cols] = scaler.transform(df[cols])
    return df


# ─────────────────────────────────────────────────────────────────────────────
# STEP 6: PATIENT-LEVEL TRAIN / VAL / TEST SPLIT
# ─────────────────────────────────────────────────────────────────────────────

def patient_level_split(
    df: pd.DataFrame,
    train_frac: float = 0.70,
    val_frac: float   = 0.15,
    test_frac: float  = 0.15,
    seed: int = 42,
    stratify_events: bool = True,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    WHAT: Splits data into training, validation, and test sets at the
          PATIENT level — NOT at the row level.
    WHY:  If we split randomly by rows, the same patient's data can appear
          in both training and test sets. This causes "data leakage":
          the model learns patterns from one part of a patient's timeline
          and is evaluated on another part of the SAME patient's timeline.
          This artificially inflates performance metrics.

          CORRECT approach: each patient is entirely in ONE split.
          Train patients and test patients never share data.

    WHAT is stratification?
          We ensure that patients WITH events are roughly proportionally
          distributed across splits. Otherwise all event-patients might
          end up in one split by chance.

    Parameters
    ----------
    df              : Fully preprocessed (but unscaled) DataFrame.
    train_frac      : Fraction of patients for training.
    val_frac        : Fraction for validation.
    test_frac       : Fraction for test.
    seed            : Random seed for reproducibility.
    stratify_events : Whether to ensure event-positive patients are spread across splits.

    Returns
    -------
    train_df, val_df, test_df : Three DataFrames with no patient overlap.
    """
    assert abs(train_frac + val_frac + test_frac - 1.0) < 1e-9, \
        "train_frac + val_frac + test_frac must equal 1.0"

    np.random.seed(seed)
    all_patients = df[PATIENT_COLUMN].unique()
    n_patients   = len(all_patients)

    if stratify_events:
        # Separate patients WITH events from those WITHOUT
        patients_with_events = (
            df.groupby(PATIENT_COLUMN)[LABEL_COLUMN]
            .max()
            .loc[lambda x: x > 0]
            .index.tolist()
        )
        patients_no_events = [
            p for p in all_patients if p not in patients_with_events
        ]
        np.random.shuffle(patients_with_events)
        np.random.shuffle(patients_no_events)

        def _stratified_assign(patients, train_f, val_f):
            n = len(patients)
            n_train = max(1, int(n * train_f))
            n_val   = max(1, int(n * val_f))
            return (
                patients[:n_train],
                patients[n_train:n_train + n_val],
                patients[n_train + n_val:]
            )

        we_train, we_val, we_test = _stratified_assign(
            patients_with_events, train_frac, val_frac
        )
        noe_train, noe_val, noe_test = _stratified_assign(
            patients_no_events, train_frac, val_frac
        )

        train_patients = list(we_train) + list(noe_train)
        val_patients   = list(we_val)   + list(noe_val)
        test_patients  = list(we_test)  + list(noe_test)
    else:
        shuffled = all_patients.copy()
        np.random.shuffle(shuffled)
        n_train = int(n_patients * train_frac)
        n_val   = int(n_patients * val_frac)
        train_patients = shuffled[:n_train]
        val_patients   = shuffled[n_train:n_train + n_val]
        test_patients  = shuffled[n_train + n_val:]

    train_df = df[df[PATIENT_COLUMN].isin(train_patients)].copy()
    val_df   = df[df[PATIENT_COLUMN].isin(val_patients)].copy()
    test_df  = df[df[PATIENT_COLUMN].isin(test_patients)].copy()

    # Verify no overlap
    assert len(set(train_patients) & set(val_patients))  == 0, "Train-Val overlap!"
    assert len(set(train_patients) & set(test_patients)) == 0, "Train-Test overlap!"
    assert len(set(val_patients)   & set(test_patients)) == 0, "Val-Test overlap!"

    logger.info("Patient-level split complete:")
    for name, split_df, pats in [
        ("Train", train_df, train_patients),
        ("Val",   val_df,   val_patients),
        ("Test",  test_df,  test_patients),
    ]:
        n_ev = split_df[LABEL_COLUMN].sum() if LABEL_COLUMN in split_df else 0
        ev_rate = split_df[LABEL_COLUMN].mean() * 100 if LABEL_COLUMN in split_df else 0
        logger.info(
            f"  {name:<6}: {len(pats):>2} patients | "
            f"{len(split_df):>7,} rows | "
            f"{int(n_ev):>4} events ({ev_rate:.2f}%)"
        )

    return train_df, val_df, test_df


# ─────────────────────────────────────────────────────────────────────────────
# STEP 7: SLIDING WINDOW CREATION
# ─────────────────────────────────────────────────────────────────────────────

def create_windows(
    df: pd.DataFrame,
    window_size: int = 30,
    step_size: int   = 1,
    feature_cols: Optional[List[str]] = None,
    label_strategy: str = "last",
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    WHAT: Converts a 2D time-series DataFrame into 3D windows
          of shape (n_windows, window_size, n_features).
    WHY:  CNN-LSTM and Transformer models don't look at single time steps.
          They look at a WINDOW of recent observations and predict what
          happens next (or the risk level of that window).

    Example:
          Window size = 30 minutes (30 rows at 1-min intervals).
          Step size   = 1  (slide the window forward by 1 minute each time).
          At each position, the model sees the last 30 minutes of vitals
          and predicts: "Is this patient deteriorating?"

    Label strategy:
      'last'  → label of the LAST row in the window (current state)
      'max'   → 1 if ANY row in the window is an event (looser)
      'next'  → label of the row AFTER the window (predictive)

    Parameters
    ----------
    df             : Preprocessed, scaled DataFrame for ONE split (train/val/test).
    window_size    : Number of time steps per window.
    step_size      : Stride between consecutive windows.
    feature_cols   : Columns to use as features. Defaults to VITAL_COLUMNS.
    label_strategy : 'last', 'max', or 'next'.

    Returns
    -------
    X      : (n_windows, window_size, n_features) — model input sequences
    y      : (n_windows,)                         — labels per window
    pids   : (n_windows,)                         — patient IDs per window
    """
    if feature_cols is None:
        feature_cols = [c for c in VITAL_COLUMNS if c in df.columns]

    df = df.sort_values([PATIENT_COLUMN, TIME_COLUMN])

    X_list, y_list, pid_list = [], [], []

    for pid in df[PATIENT_COLUMN].unique():
        patient_df = df[df[PATIENT_COLUMN] == pid].copy()
        patient_df = patient_df.reset_index(drop=True)

        n = len(patient_df)
        if n < window_size + 1:
            logger.warning(
                f"Patient {pid}: only {n} rows — skipping "
                f"(need > {window_size})"
            )
            continue

        features = patient_df[feature_cols].values        # (n, n_features)
        labels   = patient_df[LABEL_COLUMN].values if LABEL_COLUMN in patient_df.columns \
                   else np.zeros(n)

        max_start = n - window_size - (1 if label_strategy == "next" else 0)
        for start in range(0, max_start, step_size):
            end = start + window_size
            window_X = features[start:end]                # (window_size, n_features)

            if label_strategy == "last":
                window_y = labels[end - 1]
            elif label_strategy == "max":
                window_y = labels[start:end].max()
            elif label_strategy == "next":
                window_y = labels[end] if end < n else labels[end - 1]
            else:
                raise ValueError(f"Unknown label_strategy: {label_strategy}")

            X_list.append(window_X)
            y_list.append(window_y)
            pid_list.append(pid)

    if not X_list:
        raise ValueError("No windows created. Check window_size vs data length.")

    X   = np.array(X_list,   dtype=np.float32)
    y   = np.array(y_list,   dtype=np.int32)
    pid = np.array(pid_list)

    logger.info(
        f"Windows created: {X.shape} "
        f"| Events: {y.sum():,} ({y.mean()*100:.2f}%)"
    )
    return X, y, pid


# ─────────────────────────────────────────────────────────────────────────────
# STEP 8: FULL PIPELINE RUNNER
# ─────────────────────────────────────────────────────────────────────────────

def run_preprocessing_pipeline(
    df: pd.DataFrame,
    source: str = "synthetic",
    target_seconds: int = 60,
    scaler_method: str = "minmax",
    train_frac: float = 0.70,
    val_frac:   float = 0.15,
    test_frac:  float = 0.15,
    seed: int = 42,
    output_dir: Optional[str] = None,
    scaler_save_path: Optional[str] = None,
) -> Dict:
    """
    WHAT: Runs the complete preprocessing pipeline end-to-end.
    WHY:  Centralises all preprocessing in one function call so that:
          (a) the same steps are applied consistently to all splits,
          (b) the scaler is fit on train only,
          (c) results can be saved for downstream phases.

    Pipeline order:
      1. Validate → 2. Outlier handling → 3. Missing values →
      4. Resample → 5. Split (patient-level) → 6. Scale →
      7. Create windows

    Parameters
    ----------
    df               : Raw input DataFrame.
    source           : Data source name (for logging).
    target_seconds   : Resampling interval.
    scaler_method    : 'minmax' or 'standard'.
    train/val/test   : Split fractions.
    seed             : Random seed.
    output_dir       : If set, saves processed CSVs here.
    scaler_save_path : If set, saves fitted scaler here.

    Returns
    -------
    results : Dictionary with keys:
              'train_df', 'val_df', 'test_df' — tabular splits (for XGBoost)
              'X_train', 'y_train', ...        — window arrays (for CNN-LSTM)
              'scaler'                         — fitted scaler
              'stats'                          — preprocessing statistics
    """
    logger.info("=" * 60)
    logger.info(f"Starting preprocessing pipeline  |  source={source}")
    logger.info("=" * 60)

    stats = {}

    # Step 1: Validate
    logger.info("[1/7] Validating input data...")
    df = validate_dataframe(df, source)
    stats["input_rows"]     = len(df)
    stats["input_patients"] = df[PATIENT_COLUMN].nunique()

    # Step 2: Outlier detection
    logger.info("[2/7] Detecting and clamping outliers...")
    df, outlier_report = detect_and_clamp_outliers(df)
    stats["outlier_report"] = outlier_report

    # Step 3: Missing value handling
    logger.info("[3/7] Handling missing values...")
    df = handle_missing_values(df)
    stats["nan_after_fill"] = int(df[VITAL_COLUMNS].isnull().sum().sum())

    # Step 4: Resample
    logger.info(f"[4/7] Resampling to {target_seconds}s intervals...")
    df = resample_to_regular_intervals(df, target_seconds=target_seconds)
    stats["rows_after_resample"] = len(df)

    # Step 5: Patient-level split
    logger.info("[5/7] Splitting (patient-level)...")
    train_df, val_df, test_df = patient_level_split(
        df,
        train_frac=train_frac,
        val_frac=val_frac,
        test_frac=test_frac,
        seed=seed,
        stratify_events=True,
    )
    stats["train_rows"]    = len(train_df)
    stats["val_rows"]      = len(val_df)
    stats["test_rows"]     = len(test_df)
    stats["train_patients"] = train_df[PATIENT_COLUMN].nunique()
    stats["val_patients"]   = val_df[PATIENT_COLUMN].nunique()
    stats["test_patients"]  = test_df[PATIENT_COLUMN].nunique()

    # Step 6: Scale (fit on train ONLY, apply to all)
    logger.info("[6/7] Fitting and applying scaler...")
    scaler = fit_scaler(train_df, method=scaler_method, save_path=scaler_save_path)
    train_df_scaled = apply_scaler(train_df, scaler)
    val_df_scaled   = apply_scaler(val_df,   scaler)
    test_df_scaled  = apply_scaler(test_df,  scaler)

    # Step 7: Create sliding windows for deep learning
    logger.info("[7/7] Creating sliding windows (window=30, step=1)...")
    X_train, y_train, pid_train = create_windows(train_df_scaled, window_size=30, step_size=1)
    X_val,   y_val,   pid_val   = create_windows(val_df_scaled,   window_size=30, step_size=1)
    X_test,  y_test,  pid_test  = create_windows(test_df_scaled,  window_size=30, step_size=1)

    stats["X_train_shape"] = list(X_train.shape)
    stats["X_val_shape"]   = list(X_val.shape)
    stats["X_test_shape"]  = list(X_test.shape)

    # Save processed data if requested
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        train_df.to_csv(os.path.join(output_dir, "train.csv"), index=False)
        val_df.to_csv(  os.path.join(output_dir, "val.csv"),   index=False)
        test_df.to_csv( os.path.join(output_dir, "test.csv"),  index=False)
        train_df_scaled.to_csv(os.path.join(output_dir, "train_scaled.csv"), index=False)
        val_df_scaled.to_csv(  os.path.join(output_dir, "val_scaled.csv"),   index=False)
        test_df_scaled.to_csv( os.path.join(output_dir, "test_scaled.csv"),  index=False)
        np.save(os.path.join(output_dir, "X_train.npy"), X_train)
        np.save(os.path.join(output_dir, "y_train.npy"), y_train)
        np.save(os.path.join(output_dir, "X_val.npy"),   X_val)
        np.save(os.path.join(output_dir, "y_val.npy"),   y_val)
        np.save(os.path.join(output_dir, "X_test.npy"),  X_test)
        np.save(os.path.join(output_dir, "y_test.npy"),  y_test)
        with open(os.path.join(output_dir, "preprocessing_stats.json"), "w") as f:
            json.dump(stats, f, indent=2)
        logger.info(f"All processed files saved to: {output_dir}")

    logger.info("=" * 60)
    logger.info("Preprocessing pipeline complete!")
    logger.info(f"  X_train : {X_train.shape}  |  events: {y_train.sum()}")
    logger.info(f"  X_val   : {X_val.shape}    |  events: {y_val.sum()}")
    logger.info(f"  X_test  : {X_test.shape}   |  events: {y_test.sum()}")
    logger.info("=" * 60)

    return {
        # Tabular DataFrames (unscaled) — for XGBoost flat feature input
        "train_df":        train_df,
        "val_df":          val_df,
        "test_df":         test_df,
        # Tabular DataFrames (scaled) — for manual inspection
        "train_df_scaled": train_df_scaled,
        "val_df_scaled":   val_df_scaled,
        "test_df_scaled":  test_df_scaled,
        # 3D Window arrays — for CNN-LSTM, Transformer, Autoencoder
        "X_train": X_train,  "y_train": y_train,  "pid_train": pid_train,
        "X_val":   X_val,    "y_val":   y_val,    "pid_val":   pid_val,
        "X_test":  X_test,   "y_test":  y_test,   "pid_test":  pid_test,
        # Scaler — needed for inference
        "scaler": scaler,
        "stats":  stats,
    }


# ─────────────────────────────────────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    """
    Run the full preprocessing pipeline on synthetic data.

    Usage:
        python ml/preprocessing/preprocess.py
    """
    import sys
    sys.path.insert(0, os.path.abspath("."))

    from ml.data.data_loader import load_synthetic_data

    # Load synthetic data
    df_raw = load_synthetic_data("data/synthetic")

    # Run pipeline
    results = run_preprocessing_pipeline(
        df=df_raw,
        source="synthetic",
        target_seconds=60,
        scaler_method="minmax",
        train_frac=0.70,
        val_frac=0.15,
        test_frac=0.15,
        seed=42,
        output_dir="data/processed",
        scaler_save_path="models/scaler.pkl",
    )

    print()
    print("Preprocessing complete!")
    print(f"  Train: {results['X_train'].shape}  events={results['y_train'].sum()}")
    print(f"  Val:   {results['X_val'].shape}    events={results['y_val'].sum()}")
    print(f"  Test:  {results['X_test'].shape}   events={results['y_test'].sum()}")
    print()
    print("[IMPORTANT] Scaler was fit on TRAINING data only.")
    print("[IMPORTANT] Same scaler applied to val and test — no data leakage.")
    print()
    print("[WARNING] SYNTHETIC DATA - NOT FOR CLINICAL USE")

