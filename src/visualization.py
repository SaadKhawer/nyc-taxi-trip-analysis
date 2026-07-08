import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
from src.utils import setup_logger

logger = setup_logger(__name__)

# Set style
sns.set_theme(style="whitegrid")

def plot_univariate(df: pd.DataFrame, output_dir: str):
    """
    Generate univariate plots: histograms for numerical, countplots for categorical.
    """
    logger.info("Generating univariate plots...")
    
    numerics = ['trip_distance', 'fare_amount', 'tip_amount', 'total_amount', 'trip_duration_mins']
    categoricals = ['VendorID', 'RatecodeID', 'payment_type']
    
    # Use a sample for faster plotting if df is very large
    sample_size = min(100000, len(df))
    df_sample = df.sample(sample_size, random_state=42)
    
    for col in numerics:
        if col in df.columns:
            plt.figure(figsize=(10, 6))
            sns.histplot(df_sample[col], bins=50, kde=True, color='skyblue')  # pyright: ignore
            plt.title(f'Distribution of {col}')
            plt.xlabel(col)
            plt.ylabel('Frequency')
            plt.tight_layout()
            plt.savefig(os.path.join(output_dir, f'univariate_{col}.png'))
            plt.close()
            
    for col in categoricals:
        if col in df.columns:
            plt.figure(figsize=(10, 6))
            sns.countplot(x=col, data=df, palette='viridis')
            plt.title(f'Count of {col}')
            plt.xlabel(col)
            plt.ylabel('Count')
            plt.tight_layout()
            plt.savefig(os.path.join(output_dir, f'univariate_{col}.png'))
            plt.close()

def plot_bivariate(df: pd.DataFrame, output_dir: str):
    """
    Generate bivariate plots: numerical vs numerical, numerical vs categorical.
    """
    logger.info("Generating bivariate plots...")
    
    sample_size = min(50000, len(df))
    df_sample = df.sample(sample_size, random_state=42)
    
    # Num vs Num: trip_distance vs fare_amount
    if 'trip_distance' in df.columns and 'fare_amount' in df.columns:
        plt.figure(figsize=(10, 6))
        corr = df_sample['trip_distance'].corr(df_sample['fare_amount'])
        sns.scatterplot(x='trip_distance', y='fare_amount', data=df_sample, alpha=0.5)
        plt.title(f'Trip Distance vs Fare Amount (Corr: {corr:.3f})')
        plt.xlabel('Trip Distance (miles)')
        plt.ylabel('Fare Amount ($)')
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, 'bivariate_distance_vs_fare.png'))
        plt.close()
        
    # Num vs Cat: payment_type vs tip_amount
    if 'payment_type' in df.columns and 'tip_amount' in df.columns:
        plt.figure(figsize=(10, 6))
        # Cap tip amount for better visualization
        sns.violinplot(x='payment_type', y='tip_amount', data=df_sample[df_sample['tip_amount'] <= 20], palette='Set2')
        plt.title('Tip Amount by Payment Type (Capped at $20)')
        plt.xlabel('Payment Type')
        plt.ylabel('Tip Amount ($)')
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, 'bivariate_payment_vs_tip.png'))
        plt.close()

def plot_business_answers(df: pd.DataFrame, output_dir: str):
    """
    Generate specific charts required for business answers.
    """
    logger.info("Generating business answer plots...")
    
    # 1. Peak demand hour vs. slowest hour
    df['hour'] = df['tpep_pickup_datetime'].dt.hour  # pyright: ignore
    hourly_counts = df['hour'].value_counts().sort_index()
    plt.figure(figsize=(12, 6))
    sns.barplot(x=hourly_counts.index, y=hourly_counts.values, palette='coolwarm')
    plt.title('Trip Volume by Hour of Day')
    plt.xlabel('Hour (0-23)')
    plt.ylabel('Number of Trips')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'business_hourly_demand.png'))
    plt.close()
    
    # 2. Weekend vs weekday avg fare
    df['day_of_week'] = df['tpep_pickup_datetime'].dt.dayofweek  # pyright: ignore
    df['is_weekend'] = df['day_of_week'] >= 5
    plt.figure(figsize=(8, 6))
    sns.barplot(x='is_weekend', y='fare_amount', data=df, errorbar='ci', palette='pastel')
    plt.title('Average Fare: Weekday vs Weekend')
    plt.xlabel('Is Weekend (False=Weekday, True=Weekend)')
    plt.ylabel('Average Fare ($)')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'business_weekend_vs_weekday_fare.png'))
    plt.close()
    
    # 3. Payment type tip rate
    df['tip_rate'] = df['tip_amount'] / df['fare_amount']
    # Replace inf and nan
    df['tip_rate'] = df['tip_rate'].replace([np.inf, -np.inf], np.nan).fillna(0)
    
    payment_tip = df.groupby('payment_type')['tip_rate'].mean().reset_index()
    plt.figure(figsize=(10, 6))
    sns.barplot(x='payment_type', y='tip_rate', data=payment_tip, palette='magma')
    plt.title('Average Tip Rate by Payment Type')
    plt.xlabel('Payment Type')
    plt.ylabel('Average Tip Rate')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'business_payment_tip_rate.png'))
    plt.close()
    
    # 4. Avg trip duration by day-of-week
    day_mapping = {0: 'Mon', 1: 'Tue', 2: 'Wed', 3: 'Thu', 4: 'Fri', 5: 'Sat', 6: 'Sun'}
    df['day_name'] = df['day_of_week'].map(day_mapping)
    duration_dow = df.groupby('day_name')['trip_duration_mins'].mean().reindex(day_mapping.values()).reset_index()  # pyright: ignore
    
    plt.figure(figsize=(10, 6))
    sns.barplot(x='day_name', y='trip_duration_mins', data=duration_dow, palette='crest')
    plt.title('Average Trip Duration by Day of Week')
    plt.xlabel('Day of Week')
    plt.ylabel('Average Duration (minutes)')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'business_duration_by_dow.png'))
    plt.close()
    
    # 5. Share of trips under 2 miles vs >= 2 miles
    df['is_under_2_miles'] = df['trip_distance'] < 2.0
    df['fare_per_mile'] = df['fare_amount'] / df['trip_distance']
    df['fare_per_mile'] = df['fare_per_mile'].replace([np.inf, -np.inf], np.nan).fillna(0)
    
    plt.figure(figsize=(8, 6))
    sns.violinplot(x='is_under_2_miles', y='fare_per_mile', data=df[df['fare_per_mile'] <= 20], palette='muted')
    plt.title('Fare Per Mile: < 2 Miles vs >= 2 Miles (Capped at $20/mile)')
    plt.xlabel('Is Under 2 Miles')
    plt.ylabel('Fare Per Mile ($)')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'business_fare_per_mile_comparison.png'))
    plt.close()

def generate_all_plots(df: pd.DataFrame, output_dir: str):
    plot_univariate(df, output_dir)
    plot_bivariate(df, output_dir)
    plot_business_answers(df, output_dir)
