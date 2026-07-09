from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import os
import json
import pandas as pd
import joblib

app = Flask(__name__)
CORS(app) # Allow React to fetch data from this API

# Global variables to store model and data
model_path = os.path.join('models', 'random_forest.pkl')
data_path = os.path.join('data', 'processed', 'task2_predictions_full.csv')

rf_model = None
historical_df = None

def load_resources():
    global rf_model, historical_df
    try:
        if os.path.exists(model_path):
            rf_model = joblib.load(model_path)
            print("Model loaded successfully.")
        
        if os.path.exists(data_path):
            historical_df = pd.read_csv(data_path)
            historical_df['pickup_hour'] = pd.to_datetime(historical_df['pickup_hour'])
            print("Historical data loaded successfully.")
    except Exception as e:
        print(f"Error loading resources: {e}")

load_resources()

@app.route('/api/results', methods=['GET'])
def get_results():
    results_path = os.path.join('reports', 'task2_results.json')
    if os.path.exists(results_path):
        with open(results_path, 'r') as f:
            data = json.load(f)
        return jsonify(data)
    return jsonify({"error": "Results not found"}), 404

@app.route('/api/images/<filename>', methods=['GET'])
def get_image(filename):
    return send_from_directory('images', filename)

@app.route('/api/data/csv', methods=['GET'])
def get_csv_data():
    file_type = request.args.get('type', 'hour') # hour, day, weekend
    file_map = {
        'hour': 'task2_predictions_by_hour.csv',
        'day': 'task2_predictions_by_day.csv',
        'weekend': 'task2_predictions_by_weekend.csv'
    }
    
    if file_type not in file_map:
        return jsonify({"error": "Invalid type"}), 400
        
    csv_file = os.path.join('data', 'processed', file_map[file_type])
    if os.path.exists(csv_file):
        df = pd.read_csv(csv_file)
        return jsonify(df.to_dict(orient='records'))
    return jsonify({"error": "File not found"}), 404

@app.route('/api/data/chart', methods=['GET'])
def get_chart_data():
    zone_id = request.args.get('zone_id', 142, type=int)
    if historical_df is None:
        return jsonify({"error": "Data not loaded"}), 500
        
    zone_data = historical_df[historical_df['PULocationID'] == zone_id].copy()
    if zone_data.empty:
        return jsonify({"error": "No data found for this zone"}), 404
        
    # Format for Recharts
    chart_data = []
    for _, row in zone_data.iterrows():
        # Only take last 7 days of test set to keep chart clean
        if row['pickup_hour'] >= pd.to_datetime('2024-01-25'):
            chart_data.append({
                "time": row['pickup_hour'].strftime('%Y-%m-%d %H:00'),
                "actual": int(row['pickup_count']) if 'pickup_count' in row else 0,
                "predicted": max(0, int(round(row['rf_prediction']))) if 'rf_prediction' in row else 0
            })
            
    return jsonify(chart_data)

@app.route('/api/predict', methods=['POST'])
def predict():
    if rf_model is None or historical_df is None:
        return jsonify({"error": "Model or data not loaded"}), 500

    try:
        req_data = request.json
        zone_id = int(req_data.get('zone_id'))
        target_time = pd.to_datetime(req_data.get('target_time'))
        
        row = historical_df[(historical_df['PULocationID'] == zone_id) & (historical_df['pickup_hour'] == target_time)]
        
        if row.empty:
            return jsonify({"error": f"No historical context for Zone {zone_id} at {target_time}. Test period: Jan 22 - Jan 31."}), 404
            
        row = row.iloc[0]
        
        features = pd.DataFrame([{
            'hour_of_day': row['hour_of_day'],
            'day_of_week': row['day_of_week'],
            'is_weekend': row['is_weekend'],
            'lag_1_pickups': row['lag_1_pickups'],
            'lag_24_pickups': row['lag_24_pickups'],
            'lag_168_pickups': row['lag_168_pickups']
        }])
        
        prediction = rf_model.predict(features)[0]
        prediction = max(0, int(round(prediction)))
        
        return jsonify({
            "zone_id": zone_id,
            "target_time": str(target_time),
            "actual_demand": int(row['pickup_count']) if 'pickup_count' in row else None,
            "predicted_demand": prediction
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True, port=5000)
