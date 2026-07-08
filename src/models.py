import pandas as pd
import numpy as np
import logging
from sklearn.linear_model import LinearRegression # pyright: ignore
from sklearn.ensemble import RandomForestRegressor # pyright: ignore
from sklearn.metrics import mean_squared_error, mean_absolute_error # pyright: ignore

logger = logging.getLogger('models')

def train_and_evaluate(df: pd.DataFrame, test_start_date: str):
    """
    Train Linear Regression and Random Forest models, and evaluate against Naive Baseline.
    Evaluate using RMSE and MAE.
    """
    logger.info(f"Splitting data into train (< {test_start_date}) and test (>= {test_start_date})...")
    
    train_df = df[df['pickup_hour'] < test_start_date].copy()
    test_df = df[df['pickup_hour'] >= test_start_date].copy()
    
    features = ['hour_of_day', 'day_of_week', 'is_weekend', 'lag_1_pickups', 'lag_24_pickups', 'lag_168_pickups']
    target = 'pickup_count'
    
    X_train = train_df[features]
    y_train = train_df[target]
    
    X_test = test_df[features]
    y_test = test_df[target]
    
    results = {}
    
    # 1. Naive Baseline (Guessing last week's exact value)
    # "Last Monday at 9 am, there were 300 pickups. So this Monday at 9 am, I will guess 300."
    baseline_preds = test_df['lag_168_pickups']
    results['Baseline'] = {
        'RMSE': float(np.sqrt(mean_squared_error(y_test, baseline_preds))),
        'MAE': float(mean_absolute_error(y_test, baseline_preds))
    }
    
    # 2. Linear Regression
    logger.info("Training Linear Regression...")
    lr = LinearRegression()
    lr.fit(X_train, y_train)
    lr_preds = lr.predict(X_test)
    # clip predictions to 0 (cannot have negative pickups)
    lr_preds = np.clip(lr_preds, 0, None)
    results['LinearRegression'] = {
        'RMSE': float(np.sqrt(mean_squared_error(y_test, lr_preds))),
        'MAE': float(mean_absolute_error(y_test, lr_preds))
    }
    
    # 3. Random Forest (Fast configuration for execution limits)
    logger.info("Training Random Forest...")
    rf = RandomForestRegressor(n_estimators=50, max_depth=10, random_state=42, n_jobs=-1)
    rf.fit(X_train, y_train)
    rf_preds = rf.predict(X_test)
    results['RandomForest'] = {
        'RMSE': float(np.sqrt(mean_squared_error(y_test, rf_preds))),
        'MAE': float(mean_absolute_error(y_test, rf_preds))
    }
    
    # Store RF predictions for failure analysis
    test_df['rf_prediction'] = rf_preds
    test_df['baseline_prediction'] = baseline_preds
    test_df['rf_absolute_error'] = np.abs(test_df['pickup_count'] - test_df['rf_prediction'])
    
    return results, test_df, rf

def perform_failure_analysis(test_df: pd.DataFrame):
    """
    Perform failure analysis by finding where the Random Forest model is most wrong.
    Groups by Hour, Day, and Zone to find systemic patterns.
    """
    logger.info("Performing Failure Analysis...")
    
    analysis = {}
    
    # 1. Worst Hours of the Day
    hourly_errors = test_df.groupby('hour_of_day')['rf_absolute_error'].mean().sort_values(ascending=False)
    analysis['worst_hours'] = hourly_errors.head(3).to_dict()
    
    # 2. Worst Days of the Week
    day_mapping = {0: 'Mon', 1: 'Tue', 2: 'Wed', 3: 'Thu', 4: 'Fri', 5: 'Sat', 6: 'Sun'}
    test_df['day_name'] = test_df['day_of_week'].map(day_mapping)
    daily_errors = test_df.groupby('day_name')['rf_absolute_error'].mean().sort_values(ascending=False)
    analysis['worst_days'] = daily_errors.head(3).to_dict()
    
    # 3. Worst Zones
    zone_errors = test_df.groupby('PULocationID')['rf_absolute_error'].mean().sort_values(ascending=False)
    analysis['worst_zones'] = zone_errors.head(3).to_dict()
    
    # 4. Specific Extreme Failure Cases (Top 2 worst individual predictions)
    top_failures = test_df.nlargest(2, 'rf_absolute_error')
    analysis['top_specific_failures'] = []
    for _, row in top_failures.iterrows():
        case = (f"Zone {row['PULocationID']} on {row['pickup_hour']} "
                f"(Actual: {row['pickup_count']}, Predicted: {row['rf_prediction']:.1f}, "
                f"Error: {row['rf_absolute_error']:.1f})")
        analysis['top_specific_failures'].append(case)
        
    return analysis
