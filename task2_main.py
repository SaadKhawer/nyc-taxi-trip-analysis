import os
import json
import logging
import pandas as pd
import matplotlib.pyplot as plt
from src.utils import setup_logger
from src.features import load_and_aggregate_data, engineer_features
from src.models import train_and_evaluate, perform_failure_analysis

logger = setup_logger('task2_main')

def plot_actual_vs_predicted(test_df, zone_id=142):
    """
    Plots the Actual vs Predicted demand for a specific zone over time.
    """
    logger.info(f"Generating Actual vs Predicted graph for Zone {zone_id}...")
    zone_data = test_df[test_df['PULocationID'] == zone_id].copy()
    zone_data = zone_data.sort_values('pickup_hour')
    
    plt.figure(figsize=(15, 6))
    plt.plot(zone_data['pickup_hour'], zone_data['pickup_count'], label='Actual Demand (Ground Truth)', color='#1f77b4', linewidth=2)
    plt.plot(zone_data['pickup_hour'], zone_data['rf_prediction'], label='Random Forest Prediction', color='#ff7f0e', linestyle='--', linewidth=2)
    
    plt.title(f'NYC Taxi Demand: Actual vs Predicted (Zone {zone_id} - Test Period)', fontsize=16, fontweight='bold')
    plt.xlabel('Date & Time', fontsize=12)
    plt.ylabel('Number of Pickups', fontsize=12)
    plt.legend(fontsize=12)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    
    os.makedirs('images', exist_ok=True)
    save_path = os.path.join('images', f'task2_forecast_zone_{zone_id}.png')
    plt.savefig(save_path, dpi=300)
    plt.close()
    return save_path

def plot_error_by_hour(test_df):
    """
    Plots the average absolute error by hour of day (Failure Analysis visualization).
    """
    logger.info("Generating Error by Hour graph...")
    hourly_errors = test_df.groupby('hour_of_day')['rf_absolute_error'].mean()
    
    plt.figure(figsize=(12, 6))
    bars = plt.bar(hourly_errors.index, hourly_errors.values, color='#d62728', alpha=0.7)
    
    # Highlight the worst 3 hours
    worst_hours = hourly_errors.nlargest(3).index
    for bar in bars:
        # get the hour number (x coordinate of the center of the bar)
        hour = int(bar.get_x() + bar.get_width() / 2.0)
        if hour in worst_hours:
            bar.set_color('#7f3136') # Darker red for worst hours
            bar.set_edgecolor('black')
            bar.set_linewidth(1.5)
            
    plt.title('Failure Analysis: Average Prediction Error by Hour of Day', fontsize=16, fontweight='bold')
    plt.xlabel('Hour of Day (0-23)', fontsize=12)
    plt.ylabel('Average Absolute Error (Pickups)', fontsize=12)
    plt.xticks(range(24))
    plt.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    
    save_path = os.path.join('images', 'task2_error_by_hour.png')
    plt.savefig(save_path, dpi=300)
    plt.close()
    return save_path

def main():
    # Setup
    input_file = os.path.join('data', 'processed', 'yellow_tripdata_2024-01_cleaned.parquet')
    
    if not os.path.exists(input_file):
        logger.error(f"Input file not found: {input_file}. Please ensure Task 1 data is available.")
        return
        
    try:
        # 1. Features
        df = load_and_aggregate_data(input_file)
        df_features = engineer_features(df)
        
        # 2. Modeling
        # Train: Jan 8 - Jan 21 (since Jan 1-7 are lost to 168h lag)
        # Test: Jan 22 - Jan 31
        test_start_date = '2024-01-22'
        results, test_df, rf_model = train_and_evaluate(df_features, test_start_date)
        
        import pandas as pd
        
        # Format Evaluation Results as DataFrame
        eval_df = pd.DataFrame(results).T
        logger.info("\n" + "="*40 + "\n          EVALUATION RESULTS\n" + "="*40)
        logger.info("\n" + eval_df.round(2).to_string())
            
        # 3. Failure Analysis
        failure_insights = perform_failure_analysis(test_df)
        
        logger.info("\n" + "="*40 + "\n          FAILURE ANALYSIS\n" + "="*40)
        
        logger.info("\n--- Worst Hours ---")
        hours_df = pd.DataFrame(list(failure_insights['worst_hours'].items()), columns=['Hour of Day', 'Avg Error (Pickups)'])
        logger.info("\n" + hours_df.round(2).to_string(index=False))
        
        logger.info("\n--- Worst Days ---")
        days_df = pd.DataFrame(list(failure_insights['worst_days'].items()), columns=['Day of Week', 'Avg Error (Pickups)'])
        logger.info("\n" + days_df.round(2).to_string(index=False))
        
        logger.info("\n--- Worst Zones ---")
        zones_df = pd.DataFrame(list(failure_insights['worst_zones'].items()), columns=['Zone ID', 'Avg Error (Pickups)'])
        logger.info("\n" + zones_df.round(2).to_string(index=False))
        
        logger.info("\n--- Specific Extreme Failures ---")
        for case in failure_insights['top_specific_failures']:
            logger.info(f" -> {case}")
            
        # Generate Graphs
        plot_actual_vs_predicted(test_df, zone_id=142)
        plot_error_by_hour(test_df)
            
        # Save results locally to build the report
        output_results_file = os.path.join('reports', 'task2_results.json')
        os.makedirs('reports', exist_ok=True)
        with open(output_results_file, 'w') as f:
            # handle types for json dump
            def convert_keys(obj):
                if isinstance(obj, dict):
                    return {str(k): convert_keys(v) for k, v in obj.items()}
                return obj
                
            json.dump({'evaluation': results, 'failure_analysis': convert_keys(failure_insights)}, f, indent=4)
            
        # NEW: Save predictions to CSV
        csv_path = os.path.join('data', 'processed', 'task2_predictions_full.csv')
        test_df.to_csv(csv_path, index=False)
        
        # Export aggregated slices (Hour, Day, Weekend)
        hour_csv = os.path.join('data', 'processed', 'task2_predictions_by_hour.csv')
        test_df.groupby('hour_of_day')[['pickup_count', 'rf_prediction']].mean().round(2).reset_index().to_csv(hour_csv, index=False)
        
        day_csv = os.path.join('data', 'processed', 'task2_predictions_by_day.csv')
        test_df.groupby('day_of_week')[['pickup_count', 'rf_prediction']].mean().round(2).reset_index().to_csv(day_csv, index=False)
        
        weekend_csv = os.path.join('data', 'processed', 'task2_predictions_by_weekend.csv')
        test_df.groupby('is_weekend')[['pickup_count', 'rf_prediction']].mean().round(2).reset_index().to_csv(weekend_csv, index=False)
        
        logger.info(f"Predictions and additional slices (Hour, Day, Weekend) saved to data/processed/")
        
        # NEW: Save the trained model for interactive CLI
        import joblib
        os.makedirs('models', exist_ok=True)
        model_path = os.path.join('models', 'random_forest.pkl')
        joblib.dump(rf_model, model_path)
        logger.info(f"Model saved to {model_path}")
            
        logger.info(f"Results saved to {output_results_file}")
        logger.info("Task 2 Pipeline completed successfully.")
        
    except Exception as e:
        logger.error(f"Pipeline failed: {e}", exc_info=True)

if __name__ == "__main__":
    main()
