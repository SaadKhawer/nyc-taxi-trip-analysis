<div align="center">

# 🚖 NYC Taxi Analytics & Demand Forecasting
### Exploratory Data Analysis and Machine Learning using Python

<img src="https://img.shields.io/badge/Python-3.12-blue?style=for-the-badge&logo=python">
<img src="https://img.shields.io/badge/Pandas-Data%20Analysis-green?style=for-the-badge">
<img src="https://img.shields.io/badge/Scikit--Learn-Machine%20Learning-orange?style=for-the-badge">
<img src="https://img.shields.io/badge/Matplotlib-Charts-red?style=for-the-badge">
<img src="https://img.shields.io/badge/Seaborn-Visualization-yellow?style=for-the-badge">

---

### 📊 Summer AI Internship 2026 Project

An end-to-end Data Analytics and Machine Learning project built on the **NYC Yellow Taxi Trip Records** dataset. The project covers data cleaning, exploratory data analysis, feature engineering, demand forecasting, model evaluation, and business insight generation.

</div>

---

# 📌 Project Overview

This repository presents an end-to-end data analytics and machine learning pipeline using the NYC Yellow Taxi Trip Records dataset.

The project is divided into two major tasks:

## Task 1: Exploratory Data Analysis (EDA)

- Data Cleaning and Validation
- Missing Value Handling
- Outlier Detection
- Statistical Analysis
- Data Visualization
- Business Insight Generation

## Task 2: Demand Forecasting

- Hourly Pickup Aggregation
- Feature Engineering
- Baseline Forecasting
- Linear Regression Model
- Random Forest Model
- Model Evaluation
- Failure Analysis

The project demonstrates the complete lifecycle of a real-world data science project, from understanding historical taxi patterns to predicting future taxi demand.

---

# 🎯 Project Objectives

- Load and validate raw taxi trip data
- Clean and preprocess the dataset
- Perform Exploratory Data Analysis (EDA)
- Generate business insights and visualizations
- Aggregate taxi pickups at hourly granularity
- Create time-based and lag features
- Build forecasting models
- Evaluate model performance
- Perform failure analysis
- Develop an end-to-end analytics pipeline

---

# 🗂 Dataset Information

| Property | Details |
|----------|---------|
| Dataset | NYC Yellow Taxi Trip Records |
| Source | NYC Taxi & Limousine Commission (TLC) |
| File Format | Parquet (.parquet) |
| Data Type | Real-world Transportation Data |
| Analysis Type | Exploratory Data Analysis & Demand Forecasting |
| Forecast Target | Hourly Taxi Pickup Demand |

---

# 🛠 Technologies Used

| Technology | Purpose |
|------------|---------|
| Python | Programming Language |
| Pandas | Data Cleaning & Analysis |
| NumPy | Numerical Computation |
| Matplotlib | Data Visualization |
| Seaborn | Statistical Visualization |
| Scikit-learn | Machine Learning |
| PyArrow | Reading Parquet Files |
| Joblib | Model Serialization |
| Git | Version Control |
| GitHub | Project Hosting |

---

# 📁 Project Structure

```text
nyc-taxi-trip-analysis/

│
├── data/
│   ├── raw/
│   └── processed/
│
├── images/
├── reports/
│
├── models/
│   └── random_forest.pkl
│
├── src/
│   ├── data_cleaning.py
│   ├── visualization.py
│   ├── features.py
│   ├── models.py
│   └── utils.py
│
├── main.py
├── task2_main.py
├── predict_cli.py
├── README.md
└── pyproject.toml
```

---

# ⚙️ Project Workflow

```text
Raw NYC Taxi Dataset
        │
        ▼
Task 1: Exploratory Data Analysis
        │
        ├── Data Validation
        ├── Data Cleaning
        ├── Missing Value Handling
        ├── Outlier Detection
        ├── Visualizations
        └── Business Insights
        │
        ▼
Cleaned Dataset
        │
        ▼
Task 2: Demand Forecasting
        │
        ├── Hourly Aggregation
        ├── Feature Engineering
        ├── Baseline Model
        ├── Linear Regression
        ├── Random Forest
        ├── RMSE & MAE Evaluation
        └── Failure Analysis
        │
        ▼
Demand Predictions & Reports
```

---

# 📈 Task 1 – Exploratory Data Analysis (EDA)

✔ Data Cleaning

✔ Missing Value Handling

✔ Duplicate Removal

✔ Outlier Detection

✔ Statistical Analysis

✔ Data Visualization

✔ Business Insight Generation

---

# 🤖 Task 2 – Demand Forecasting

The forecasting module predicts the number of taxi pickups expected during the next hour.

✔ Hourly Pickup Aggregation

✔ Time-Based Feature Engineering

✔ Lag Feature Creation

✔ Baseline Forecasting

✔ Linear Regression Model

✔ Random Forest Model

✔ RMSE and MAE Evaluation

✔ Failure Analysis

---

# 🧠 Features Used for Forecasting

- Hour of Day
- Day of Week
- Weekend Indicator
- Previous Hour Pickup Count
- Previous Day Pickup Count
- Previous Week Pickup Count

---

# 📊 Machine Learning Models

| Model | Purpose |
|-------|----------|
| Naive Baseline | Uses last week's demand as a benchmark |
| Linear Regression | Learns linear demand patterns |
| Random Forest | Learns complex and non-linear demand patterns |

---

# 📏 Evaluation Metrics

The forecasting models are evaluated using:

- Mean Absolute Error (MAE)
- Root Mean Squared Error (RMSE)

Lower metric values indicate better prediction performance.

---

# 📷 Output

The project automatically generates:

- Cleaned Dataset
- Statistical Summary
- Distribution Charts
- Business Insight Graphs
- Engineered Features
- Demand Forecasts
- Evaluation Reports
- Failure Analysis Reports

---

# 🚀 Installation

Clone the repository

```bash
git clone https://github.com/SaadKhawer/nyc-taxi-trip-analysis.git
```

Move into the project

```bash
cd nyc-taxi-trip-analysis
```

Create Virtual Environment

```bash
python -m venv venv
```

Activate Environment

```bash
venv\Scripts\activate
```

Install Dependencies

```bash
pip install pandas numpy matplotlib seaborn scikit-learn pyarrow joblib
```

---

# ▶ Run Project

### Task 1 – EDA

```bash
python main.py
```

### Task 2 – Demand Forecasting

```bash
python task2_main.py
```

### Prediction CLI

```bash
python predict_cli.py
```

---

# 📚 Skills Demonstrated

- Data Cleaning
- Data Wrangling
- Exploratory Data Analysis
- Data Visualization
- Statistical Analysis
- Feature Engineering
- Time-Series Forecasting
- Machine Learning
- Failure Analysis
- Model Evaluation
- Python Programming
- Git & GitHub
- End-to-End Data Science Pipeline Development

---

# 👨‍💻 Author

**Muhammad Saad**

Computer Science Student



GitHub:
https://github.com/SaadKhawer

---

<div align="center">

### ⭐ End-to-End NYC Taxi Analytics & Demand Forecasting Project

Made with ❤️ using Python, Data Analysis and Machine Learning 🚕🤖📊

</div>
