import pandas as pd
import numpy as np
from typing import Tuple, Dict
from src.utils import setup_logger

logger = setup_logger(__name__)

def log_step(func):
    """
    Decorator to log row counts before and after a cleaning step.
    """
    def wrapper(df, *args, **kwargs):
        initial_rows = len(df)
        df_cleaned = func(df, *args, **kwargs)
        final_rows = len(df_cleaned)
        dropped_rows = initial_rows - final_rows
        if dropped_rows > 0:
            logger.info(f"{func.__name__}: Removed {dropped_rows} rows. Remaining: {final_rows}")
        else:
            logger.info(f"{func.__name__}: No rows removed. Remaining: {final_rows}")
        return df_cleaned
    return wrapper

@log_step
def remove_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    """Identify and remove duplicate rows."""
    duplicates = df.duplicated().sum()
    logger.info(f"Found {duplicates} duplicate rows.")
    return df.drop_duplicates()

def cast_data_types(df: pd.DataFrame) -> pd.DataFrame:
    """Cast columns to appropriate data types."""
    # Datetime casting
    df['tpep_pickup_datetime'] = pd.to_datetime(df['tpep_pickup_datetime'])
    df['tpep_dropoff_datetime'] = pd.to_datetime(df['tpep_dropoff_datetime'])
    
    # Categorical casting
    categoricals = ['VendorID', 'RatecodeID', 'store_and_fwd_flag', 'PULocationID', 'DOLocationID', 'payment_type']
    for col in categoricals:
        if col in df.columns:
            df[col] = df[col].astype('category')
            
    # Ensure numerics are numeric (Parquet usually handles this, but forcing it for safety)
    numerics = ['passenger_count', 'trip_distance', 'fare_amount', 'extra', 'mta_tax', 
                'tip_amount', 'tolls_amount', 'improvement_surcharge', 'total_amount', 'congestion_surcharge']
    for col in numerics:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            
    logger.info("Data types casted successfully.")
    return df

def handle_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    """
    Report % missing, check correlations, and handle missing values.
    """
    missing_pct = df.isnull().mean() * 100
    missing_report = missing_pct[missing_pct > 0]
    
    if not missing_report.empty:
        logger.info("Missing Values Percentage:")
        for col, pct in missing_report.items():
            logger.info(f"  {col}: {pct:.2f}%")
            
        # Example of checking correlation of missingness
        if 'passenger_count' in df.columns and 'RatecodeID' in df.columns:
            corr = df['passenger_count'].isnull().corr(df['RatecodeID'].isnull())
            logger.info(f"  Correlation of missingness between passenger_count and RatecodeID: {corr:.3f}")
    
    # Drop rows where critical fields have no sane imputable value
    # E.g., timestamps (though usually not null in this dataset) or location IDs
    critical_cols = ['tpep_pickup_datetime', 'tpep_dropoff_datetime', 'PULocationID', 'DOLocationID']
    initial_rows = len(df)
    df = df.dropna(subset=critical_cols)
    if len(df) < initial_rows:
        logger.info(f"Dropped {initial_rows - len(df)} rows due to missing critical fields (timestamps/locations).")

    # Impute missing values with justifiable fill values
    if 'passenger_count' in df.columns:
        # Fill passenger_count with median (robust to outliers, typical ride is 1 or 2)
        med_passengers = df['passenger_count'].median()
        df['passenger_count'] = df['passenger_count'].fillna(med_passengers)
        logger.info(f"Filled missing passenger_count with median: {med_passengers}")

    if 'RatecodeID' in df.columns:
        # Fill RatecodeID with mode (most trips are standard rate)
        mode_rate = df['RatecodeID'].mode()[0]
        df['RatecodeID'] = df['RatecodeID'].fillna(mode_rate)
        logger.info(f"Filled missing RatecodeID with mode: {mode_rate}")

    if 'payment_type' in df.columns:
        # Fill payment_type with mode
        mode_payment = df['payment_type'].mode()[0]
        df['payment_type'] = df['payment_type'].fillna(mode_payment)
        logger.info(f"Filled missing payment_type with mode: {mode_payment}")
        
    if 'store_and_fwd_flag' in df.columns:
        mode_flag = df['store_and_fwd_flag'].mode()[0]
        df['store_and_fwd_flag'] = df['store_and_fwd_flag'].fillna(mode_flag)
        logger.info(f"Filled missing store_and_fwd_flag with mode: {mode_flag}")

    if 'congestion_surcharge' in df.columns:
        # If congestion surcharge is missing, assume 0
        df['congestion_surcharge'] = df['congestion_surcharge'].fillna(0.0)
        logger.info("Filled missing congestion_surcharge with 0.0")

    if 'Airport_fee' in df.columns:
        df['Airport_fee'] = df['Airport_fee'].fillna(0.0)
        logger.info("Filled missing Airport_fee with 0.0")

    return df

@log_step
def remove_invalid_rows(df: pd.DataFrame) -> pd.DataFrame:
    """
    Remove rows with negative fares/distances, zero-passengers, and impossible timestamps.
    """
    # Negative fares
    mask_fare = df['fare_amount'] >= 0
    # Negative distances
    mask_dist = df['trip_distance'] > 0
    # Zero passengers (after imputation, if any were genuinely 0, though 0 is technically possible in NYC TLC if package delivery, we are asked to handle/remove zero-passenger trips)
    mask_pass = df['passenger_count'] > 0
    # Impossible timestamps
    mask_time = df['tpep_dropoff_datetime'] > df['tpep_pickup_datetime']
    
    # Combined mask
    valid_mask = mask_fare & mask_dist & mask_pass & mask_time
    
    return df[valid_mask].copy()

@log_step
def handle_outliers(df: pd.DataFrame) -> pd.DataFrame:
    """
    Detect and handle outliers based on domain knowledge.
    - trip_distance > 100 miles
    - fare_amount > 500 dollars
    - trip_duration (calculated) > 12 hours
    """
    df['trip_duration_mins'] = (df['tpep_dropoff_datetime'] - df['tpep_pickup_datetime']).dt.total_seconds() / 60.0
    
    dist_outliers = (df['trip_distance'] > 100).sum()
    fare_outliers = (df['fare_amount'] > 500).sum()
    time_outliers = (df['trip_duration_mins'] > 720).sum()
    
    logger.info(f"Outlier Detection (Domain Knowledge thresholds):")
    logger.info(f"  trip_distance > 100 miles: {dist_outliers} rows flagged.")
    logger.info(f"  fare_amount > $500: {fare_outliers} rows flagged.")
    logger.info(f"  trip_duration > 12 hours: {time_outliers} rows flagged.")
    
    # We will remove these as they represent extreme anomalies or errors
    mask_valid = (df['trip_distance'] <= 100) & (df['fare_amount'] <= 500) & (df['trip_duration_mins'] <= 720)
    
    return df[mask_valid].copy()

def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Execute the full data cleaning pipeline.
    """
    logger.info(f"Initial shape: {df.shape}")
    df = remove_duplicates(df)
    df = cast_data_types(df)
    df = handle_missing_values(df)
    df = remove_invalid_rows(df)
    df = handle_outliers(df)
    logger.info(f"Final shape: {df.shape}")
    return df
