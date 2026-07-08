import pandas as pd
import numpy as np
import logging
import os

logger = logging.getLogger('features')

def load_and_aggregate_data(filepath: str) -> pd.DataFrame:
    """
    Load cleaned trip data and aggregate pickups by hour and zone (PULocationID).
    We create a complete time grid to ensure hours with 0 pickups are correctly represented as 0,
    rather than missing.
    """
    logger.info(f"Loading data from {filepath}...")
    df = pd.read_parquet(filepath)
    
    # CRITICAL FIX: Ensure we only keep January 2024 to avoid 45 Million row grid blowups
    df = df[(df['tpep_pickup_datetime'] >= '2024-01-01') & (df['tpep_pickup_datetime'] < '2024-02-01')].copy()
    
    # Floor datetime to hour
    df['pickup_hour'] = df['tpep_pickup_datetime'].dt.floor('h')
    
    # Aggregate pickups
    logger.info("Aggregating pickups by hour and PULocationID...")
    hourly_pickups = df.groupby(['PULocationID', 'pickup_hour']).size().reset_index(name='pickup_count')
    
    # Create complete grid
    unique_zones = hourly_pickups['PULocationID'].unique()
    # Min and max dates to create full time range
    min_time = hourly_pickups['pickup_hour'].min()
    max_time = hourly_pickups['pickup_hour'].max()
    
    all_hours = pd.date_range(start=min_time, end=max_time, freq='h')
    
    # Create MultiIndex for complete grid
    grid = pd.MultiIndex.from_product([unique_zones, all_hours], names=['PULocationID', 'pickup_hour'])
    grid_df = pd.DataFrame(index=grid).reset_index()
    
    # Merge and fill missing counts with 0
    full_df = pd.merge(grid_df, hourly_pickups, on=['PULocationID', 'pickup_hour'], how='left')
    full_df['pickup_count'] = full_df['pickup_count'].fillna(0).astype(int)
    
    # Sort by zone and time to prepare for lag features
    full_df = full_df.sort_values(['PULocationID', 'pickup_hour']).reset_index(drop=True)
    return full_df

def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Engineer time-based and lag features for forecasting.
    Justifications:
    - hour_of_day: Captures daily commuting patterns (rush hour vs midnight).
    - day_of_week: Captures differences between weekdays and weekends.
    - is_weekend: Binary flag highlighting completely different demand dynamics on weekends.
    - lag_1_pickups: Captures immediate short-term trend (what happened an hour ago).
    - lag_24_pickups: Captures exactly yesterday's demand at the same hour.
    - lag_168_pickups: Captures exactly last week's demand at the same hour (used for naive baseline).
    """
    logger.info("Engineering time and lag features...")
    
    # Time features
    df['hour_of_day'] = df['pickup_hour'].dt.hour
    df['day_of_week'] = df['pickup_hour'].dt.dayofweek
    df['is_weekend'] = (df['day_of_week'] >= 5).astype(int)
    
    # Lag features (grouped by zone so we don't bleed data across zones)
    # lag_1: 1 hour ago
    df['lag_1_pickups'] = df.groupby('PULocationID')['pickup_count'].shift(1)
    # lag_24: 1 day ago
    df['lag_24_pickups'] = df.groupby('PULocationID')['pickup_count'].shift(24)
    # lag_168: 1 week ago (baseline)
    df['lag_168_pickups'] = df.groupby('PULocationID')['pickup_count'].shift(168)
    
    # Drop rows with NaN values resulting from the 168-hour lag.
    # This means the first 7 days of the dataset will be used as context, not training targets.
    logger.info(f"Shape before dropping NaNs: {df.shape}")
    df_clean = df.dropna().copy()
    logger.info(f"Shape after dropping NaNs: {df_clean.shape}")
    
    return df_clean
