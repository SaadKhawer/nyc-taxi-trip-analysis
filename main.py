import os
import pandas as pd
import scipy.stats as stats
from fpdf import FPDF
from src.utils import setup_logger, download_file, validate_file
from src.data_cleaning import clean_data
from src.visualization import generate_all_plots

logger = setup_logger('main')

def generate_pdf_report(business_answers: dict, report_path: str):
    """
    Generate a PDF report summarizing the business answers.
    """
    pdf = FPDF()
    pdf.add_page()
    
    # Titles
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(w=190, h=10, text="Exploratory Data Analysis: NYC Taxi Trip Records", align='C')
    pdf.ln(10)
    pdf.cell(w=190, h=10, text="(Yellow Taxi - Jan 2024)", align='C')
    pdf.ln(15)
    
    # Content
    for i, (question, answer) in enumerate(business_answers.items(), 1):
        pdf.set_x(10)  # Always force X back to left margin
        pdf.set_font("Arial", 'B', 12)
        pdf.multi_cell(w=190, h=8, text=f"{i}. {question}")
        
        pdf.set_x(10)
        pdf.set_font("Arial", size=11)
        pdf.multi_cell(w=190, h=8, text=str(answer))
        pdf.ln(5)
        
    pdf.output(report_path)
    logger.info(f"Report saved to {report_path}")

def compute_business_answers(df: pd.DataFrame) -> dict:
    answers = {}
    
    # 1. Peak demand hour vs slowest hour
    df['hour'] = df['tpep_pickup_datetime'].dt.hour
    hourly_counts = df['hour'].value_counts()
    peak_hour = hourly_counts.idxmax()
    peak_count = hourly_counts.max()
    slow_hour = hourly_counts.idxmin()
    slow_count = hourly_counts.min()
    ratio = peak_count / slow_count
    answers["Peak demand hour vs. slowest hour"] = f"Peak hour is {peak_hour}:00 with {peak_count} trips. Slowest hour is {slow_hour}:00 with {slow_count} trips. The peak is {ratio:.2f}x the trough."
    
    # 2. Weekend vs weekday avg fare
    df['day_of_week'] = df['tpep_pickup_datetime'].dt.dayofweek
    df['is_weekend'] = df['day_of_week'] >= 5
    weekend_fare = df[df['is_weekend']]['fare_amount']
    weekday_fare = df[~df['is_weekend']]['fare_amount']
    
    avg_weekend = weekend_fare.mean()
    avg_weekday = weekday_fare.mean()
    diff = avg_weekend - avg_weekday
    
    # Statistical significance using t-test
    t_stat, p_val = stats.ttest_ind(weekend_fare.dropna(), weekday_fare.dropna(), equal_var=False)
    sig = "statistically meaningful" if p_val < 0.05 else "not statistically meaningful"
    answers["Weekend vs. weekday average fare"] = f"Weekend avg: ${avg_weekend:.2f}, Weekday avg: ${avg_weekday:.2f}. Difference is ${diff:.2f}. With a p-value of {p_val:.2e}, this difference is {sig}."
    
    # 3. Payment type with highest avg tip rate
    # Usually payment_type 1 is Credit Card, which has tips recorded. Cash (2) tips are not recorded.
    df['tip_rate'] = df['tip_amount'] / df['fare_amount']
    df_tip = df.replace([float('inf'), -float('inf')], float('nan')).dropna(subset=['tip_rate', 'payment_type'])
    
    tip_by_payment = df_tip.groupby('payment_type')['tip_rate'].mean()
    highest_payment = tip_by_payment.idxmax()
    highest_rate = tip_by_payment.max()
    
    total_trips = len(df)
    payment_trips = len(df[df['payment_type'] == highest_payment])
    share = (payment_trips / total_trips) * 100
    
    answers["Payment type with highest average tip rate"] = f"Payment type {highest_payment} has the highest tip rate at {highest_rate:.2%}. It accounts for {share:.2f}% of total trips."
    
    # 4. Average trip duration by day-of-week
    day_mapping = {0: 'Mon', 1: 'Tue', 2: 'Wed', 3: 'Thu', 4: 'Fri', 5: 'Sat', 6: 'Sun'}
    df['day_name'] = df['day_of_week'].map(day_mapping)
    duration_dow = df.groupby('day_name')['trip_duration_mins'].mean().reindex(day_mapping.values())
    duration_str = ", ".join([f"{d}: {m:.1f} mins" for d, m in duration_dow.items()])
    answers["Average trip duration by day-of-week"] = duration_str
    
    # 5. Share of trips under 2 miles and fare-per-mile comparison
    df['is_under_2'] = df['trip_distance'] < 2.0
    under_2_share = df['is_under_2'].mean() * 100
    
    df['fare_per_mile'] = df['fare_amount'] / df['trip_distance']
    df_fpm = df.replace([float('inf'), -float('inf')], float('nan')).dropna(subset=['fare_per_mile'])
    
    fpm_under_2 = df_fpm[df_fpm['is_under_2']]['fare_per_mile'].mean()
    fpm_over_2 = df_fpm[~df_fpm['is_under_2']]['fare_per_mile'].mean()
    
    answers["Share of trips under 2 miles & fare-per-mile comparison"] = f"{under_2_share:.2f}% of trips are under 2 miles. Fare-per-mile for <2 miles is ${fpm_under_2:.2f}, while for >=2 miles it is ${fpm_over_2:.2f}."
    
    return answers

def main():
    logger.info("Starting EDA Pipeline...")
    
    # Ensure required directories exist
    dirs_to_create = [
        os.path.join("data", "raw"),
        os.path.join("data", "processed"),
        "images",
        "reports"
    ]
    for d in dirs_to_create:
        os.makedirs(d, exist_ok=True)
        
    # 1. Data Collection
    url = "https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2024-01.parquet"
    raw_path = os.path.join("data", "raw", "yellow_tripdata_2024-01.parquet")
    
    download_file(url, raw_path)
    
    if not validate_file(raw_path):
        logger.error("Data validation failed. Exiting.")
        return
        
    # 2. Load Data
    logger.info(f"Loading data from {raw_path}")
    df = pd.read_parquet(raw_path)
    
    # (Optional) For EDA on local, if the machine struggles, uncomment the next line:
    # df = df.sample(1000000, random_state=42)
    
    # 3. Data Cleaning
    logger.info("Starting Data Cleaning...")
    df_cleaned = clean_data(df)
    
    processed_path = os.path.join("data", "processed", "yellow_tripdata_2024-01_cleaned.parquet")
    df_cleaned.to_parquet(processed_path)
    logger.info(f"Saved cleaned data to {processed_path}")
    
    # 4. Visualizations
    logger.info("Starting Visualizations...")
    generate_all_plots(df_cleaned, "images")
    
    # 5. Business Answers
    logger.info("Computing Business Answers...")
    answers = compute_business_answers(df_cleaned)
    
    for k, v in answers.items():
        logger.info(f"{k}: {v}")
        
    # 6. Generate Report
    report_path = os.path.join("reports", "final_report.pdf")
    generate_pdf_report(answers, report_path)
    
    logger.info("Pipeline completed successfully.")

if __name__ == "__main__":
    main()
