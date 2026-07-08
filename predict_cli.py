import pandas as pd
import joblib
import os

def run_cli():
    print("=" * 50)
    print("🚕 NYC Taxi Demand Predictor (Interactive CLI) 🚕")
    print("=" * 50)
    
    model_path = os.path.join('models', 'random_forest.pkl')
    data_path = os.path.join('data', 'processed', 'task2_predictions_full.csv')
    
    if not os.path.exists(model_path) or not os.path.exists(data_path):
        print("Error: Model or data not found. Please run 'python task2_main.py' first.")
        return
        
    print("Loading AI Model and Historical Data...")
    rf_model = joblib.load(model_path)
    # Load historical data to extract lags
    df = pd.read_csv(data_path)
    df['pickup_hour'] = pd.to_datetime(df['pickup_hour'])
    
    while True:
        try:
            print("\n" + "-" * 30)
            zone_input = input("Enter Taxi Zone ID (1-265) [or 'q' to quit]: ")
            if zone_input.lower() == 'q':
                break
            zone_id = int(zone_input)
            
            time_input = input("Enter Date and Time (YYYY-MM-DD HH:00) e.g., 2024-01-25 22:00 : ")
            target_time = pd.to_datetime(time_input)
            
            # Find the specific row in the historical dataset to grab the lags
            # (In a real production system, you'd calculate lags dynamically from a live database)
            row = df[(df['PULocationID'] == zone_id) & (df['pickup_hour'] == target_time)]
            
            if row.empty:
                print(f"Sorry, could not find historical context for Zone {zone_id} at {target_time}. Note: Test period is Jan 22 to Jan 31.")
                continue
                
            row = row.iloc[0]
            
            # Extract features expected by the model
            features = pd.DataFrame([{
                'hour_of_day': row['hour_of_day'],
                'day_of_week': row['day_of_week'],
                'is_weekend': row['is_weekend'],
                'lag_1_pickups': row['lag_1_pickups'],
                'lag_24_pickups': row['lag_24_pickups'],
                'lag_168_pickups': row['lag_168_pickups']
            }])
            
            # Predict
            prediction = rf_model.predict(features)[0]
            prediction = max(0, int(round(prediction))) # clip to 0 and round to integer
            
            print("\n🔮 AI PREDICTION 🔮")
            print(f"Zone: {zone_id}")
            print(f"Time: {target_time}")
            print(f"Expected Taxi Pickups: {prediction} rides")
            print("-" * 30)
            
        except ValueError:
            print("Invalid input. Please try again.")
        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    run_cli()
