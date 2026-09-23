"""
=============================================================================
NeoNatal Watch AI — Feature Engineering
=============================================================================

WHAT  : Generates statistical and temporal features from 1-minute resampled data.
WHY   : Traditional ML models (like XGBoost) only look at one row at a time.
        They have no concept of "time". We must manually extract temporal
        context (e.g., "Heart rate has been rising for 15 minutes") and feed
        it as flat columns.
HOW   : Calculates rolling means, standard deviations, min, max, and
        rate-of-change (differences) over multiple time windows (e.g. 15m, 60m).
        Must group by patient_id to prevent leaking across patients!

INPUT : Processed tabular data (train.csv, val.csv, test.csv)
OUTPUT: Feature-rich tabular data (train_features.csv, etc.)

⚠️  SYNTHETIC / REFERENCE DATA — NOT FOR CLINICAL USE
=============================================================================
"""

import logging
from typing import List

import numpy as np
import pandas as pd

logger = logging.getLogger("FeatureEngineering")
logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")

# Standard vital columns to extract features from
VITAL_COLUMNS = [
    "heart_rate",
    "spo2",
    "respiratory_rate",
    "temperature",
    "systolic_bp",
    "diastolic_bp",
]

def add_rolling_statistics(
    df: pd.DataFrame, 
    columns: List[str], 
    window_sizes: List[int] = [15, 60]
) -> pd.DataFrame:
    """
    Calculates rolling mean, std, min, and max for each vital sign.
    Uses grouped operations to avoid overlapping patients.
    
    Parameters
    ----------
    df : pd.DataFrame
        Data sorted by patient_id and timestamp.
    columns : List[str]
        Vital sign columns to process.
    window_sizes : List[int]
        Window sizes in minutes (assuming 1 row = 1 minute).
        
    Returns
    -------
    pd.DataFrame
        Dataframe with new rolling statistic columns.
    """
    df_out = df.copy()
    grouped = df_out.groupby("patient_id")
    
    for col in columns:
        if col not in df_out.columns:
            continue
            
        for w in window_sizes:
            # Mean
            mean_col = f"{col}_mean_{w}m"
            df_out[mean_col] = grouped[col].transform(
                lambda x: x.rolling(w, min_periods=1).mean()
            )
            
            # Standard Deviation (fill NaN with 0 for the first element)
            std_col = f"{col}_std_{w}m"
            df_out[std_col] = grouped[col].transform(
                lambda x: x.rolling(w, min_periods=1).std().fillna(0)
            )
            
            # Min
            min_col = f"{col}_min_{w}m"
            df_out[min_col] = grouped[col].transform(
                lambda x: x.rolling(w, min_periods=1).min()
            )
            
            # Max
            max_col = f"{col}_max_{w}m"
            df_out[max_col] = grouped[col].transform(
                lambda x: x.rolling(w, min_periods=1).max()
            )
            
    return df_out


def add_rate_of_change(
    df: pd.DataFrame, 
    columns: List[str], 
    window_sizes: List[int] = [15, 60]
) -> pd.DataFrame:
    """
    Calculates the absolute difference between the current value 
    and the value 'w' minutes ago.
    
    Parameters
    ----------
    df : pd.DataFrame
        Data sorted by patient_id and timestamp.
    columns : List[str]
        Vital sign columns to process.
    window_sizes : List[int]
        Window sizes in minutes.
        
    Returns
    -------
    pd.DataFrame
        Dataframe with new rate-of-change columns.
    """
    df_out = df.copy()
    grouped = df_out.groupby("patient_id")
    
    for col in columns:
        if col not in df_out.columns:
            continue
            
        for w in window_sizes:
            diff_col = f"{col}_diff_{w}m"
            # shift(w) gets the value w rows ago. 
            # We bfill (backfill) the initial rows so we don't get NaNs at the start of a patient's timeline
            df_out[diff_col] = grouped[col].transform(
                lambda x: x - x.shift(w).bfill()
            )
            
    return df_out


def engineer_features(
    df: pd.DataFrame, 
    window_sizes: List[int] = [15, 60]
) -> pd.DataFrame:
    """
    Master function to run all feature engineering steps.
    
    Parameters
    ----------
    df : pd.DataFrame
        The preprocessed data (e.g., train_df).
    window_sizes : List[int]
        Windows in minutes to calculate features over.
        
    Returns
    -------
    pd.DataFrame
        Feature-enriched DataFrame.
    """
    # Ensure data is sorted temporally per patient
    df_feat = df.sort_values(["patient_id", "timestamp"]).copy()
    
    start_cols = len(df_feat.columns)
    logger.info(f"Engineering features for {len(df_feat):,} rows...")
    
    # Add features
    df_feat = add_rolling_statistics(df_feat, VITAL_COLUMNS, window_sizes)
    df_feat = add_rate_of_change(df_feat, VITAL_COLUMNS, window_sizes)
    
    end_cols = len(df_feat.columns)
    logger.info(f"Added {end_cols - start_cols} new feature columns. Total columns: {end_cols}")
    
    # Sanity check: Ensure we didn't introduce accidental NaNs
    nan_count = df_feat.isnull().sum().sum()
    if nan_count > 0:
        logger.warning(f"Feature engineering introduced {nan_count} missing values!")
        df_feat = df_feat.fillna(0) # Safe fallback
        
    return df_feat

