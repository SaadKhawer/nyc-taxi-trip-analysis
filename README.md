
<div align="center">

# 🚖 NYC Taxi Trip Analysis
### Exploratory Data Analysis (EDA) using Python

<img src="https://img.shields.io/badge/Python-3.12-blue?style=for-the-badge&logo=python">
<img src="https://img.shields.io/badge/Pandas-Data%20Analysis-green?style=for-the-badge">
<img src="https://img.shields.io/badge/Seaborn-Visualization-orange?style=for-the-badge">
<img src="https://img.shields.io/badge/Matplotlib-Charts-red?style=for-the-badge">

---

### 📊 Summer AI Internship 2026 Project

A complete Exploratory Data Analysis (EDA) project on the **NYC Yellow Taxi Trip Records** dataset. This project demonstrates professional data cleaning, statistical analysis, visualization, and business insight generation using Python.

</div>

---

# 📌 Project Overview

This project analyzes one month of **NYC Yellow Taxi Trip Records** to understand travel patterns, passenger behavior, fare distributions, payment methods, and trip characteristics.

The objective is not only to visualize the data but also to produce meaningful business insights through a structured and reproducible data analysis pipeline.

---

# 🎯 Project Objectives

- Load and validate the raw dataset
- Clean and preprocess the data
- Handle missing and invalid values
- Perform Exploratory Data Analysis (EDA)
- Detect and analyze outliers
- Generate statistical summaries
- Create professional visualizations
- Answer business-related analytical questions
- Produce reusable, well-documented Python code

---

# 🗂 Dataset Information

| Property | Details |
|----------|---------|
| Dataset | NYC Yellow Taxi Trip Records |
| Source | NYC Taxi & Limousine Commission (TLC) |
| File Format | Parquet (.parquet) |
| Data Type | Real-world Transportation Data |
| Analysis Type | Exploratory Data Analysis (EDA) |

---

# 📊 Dataset Features

The dataset contains information such as:

- Vendor ID
- Pickup Date & Time
- Dropoff Date & Time
- Passenger Count
- Trip Distance
- Fare Amount
- Tip Amount
- Total Amount
- Payment Type
- Rate Code
- Airport Fee
- Congestion Surcharge
- Extra Charges

Each row represents **one completed taxi trip**.

---

# 🛠 Technologies Used

| Technology | Purpose |
|------------|---------|
| Python | Programming Language |
| Pandas | Data Cleaning & Analysis |
| NumPy | Numerical Computation |
| Matplotlib | Data Visualization |
| Seaborn | Statistical Visualization |
| SciPy | Statistical Testing |
| PyArrow | Reading Parquet Files |
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
│
├── reports/
│
├── src/
│   ├── data_cleaning.py
│   ├── visualization.py
│   └── utils.py
│
├── main.py
├── README.md
└── pyproject.toml
```

---

# ⚙️ Project Workflow

```text
Download Dataset
        │
        ▼
Load Dataset
        │
        ▼
Validate File
        │
        ▼
Data Cleaning
        │
        ▼
Handle Missing Values
        │
        ▼
Remove Duplicates
        │
        ▼
Convert Data Types
        │
        ▼
Remove Invalid Records
        │
        ▼
Save Clean Dataset
        │
        ▼
Exploratory Data Analysis
        │
        ▼
Outlier Detection
        │
        ▼
Business Analysis
        │
        ▼
Generate Report
```

---

# 🧹 Data Cleaning Process

The following preprocessing steps are performed:

- Duplicate Row Removal
- Missing Value Analysis
- Missing Value Handling
- Data Type Conversion
- Invalid Fare Removal
- Invalid Distance Removal
- Impossible Timestamp Detection
- Passenger Validation
- Dataset Validation

---

# 📈 Exploratory Data Analysis

## Univariate Analysis

✔ Histograms

✔ KDE Curves

✔ Count Plots

✔ Distribution Analysis

✔ Summary Statistics

---

## Bivariate Analysis

✔ Scatter Plots

✔ Correlation Analysis

✔ Box Plots

✔ Violin Plots

✔ Numerical vs Categorical Analysis

---

# 🚨 Outlier Detection

Outliers are detected using:

- IQR Method

The project reports:

- Number of outliers
- Percentage of outliers
- Treatment strategy
- Justification

---

# 💼 Business Questions Answered

This project answers the following analytical questions:

- Peak demand hour
- Slowest demand hour
- Weekend vs Weekday fare comparison
- Highest average tip payment method
- Average trip duration by weekday
- Trips under 2 miles vs trips over 2 miles

---

# 📷 Output

The project automatically generates:

- Cleaned Dataset
- Statistical Summary
- Distribution Graphs
- Correlation Graphs
- Business Insight Charts
- Final Analysis Report

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

Windows

```bash
venv\Scripts\activate
```

Install Dependencies

```bash
pip install pandas numpy matplotlib seaborn scipy pyarrow
```

---

# ▶ Run Project

```bash
python main.py
```

---

# 📚 Skills Demonstrated

- Data Cleaning
- Data Wrangling
- Exploratory Data Analysis
- Data Visualization
- Statistical Analysis
- Python Programming
- Git & GitHub
- Software Project Structure

---

# 👨‍💻 Author

**Muhammad Saad**

Computer Science Student

Summer AI Internship 2026

GitHub:
https://github.com/SaadKhawer

---

<div align="center">

### ⭐ If you found this project useful, consider giving it a Star!

Made with ❤️ using Python

</div>
