# 📦 OmniStock-AI: Retail SKU Demand Forecasting & Inventory Replenishment Engine

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://streamlit.io/)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> An end-to-end retail supply chain analytics engine built for **Planning & Trading (Operations)** in omni-channel retail. Bridges the gap between predictive demand forecasting and automated procurement replenishment decisions.

---

## 🎯 Business Problem & Context
In omni-channel retail (footwear, apparel, sporting goods), operational planners encounter two primary failure modes:
1. **Stockouts during seasonal demand peaks:** High-velocity hero products running out of stock during major festive or promotional surges leads to lost revenue and customer churn.
2. **Excess capital tied in slow-moving inventory:** Inaccurate forecasts result in over-ordering, high warehouse holding costs, and aggressive terminal markdowns.

**OmniStock-AI** solves this by predicting weekly SKU demand and translating volatility into mathematically guaranteed **Safety Stock** and **Reorder Point (ROP)** schedules.

---

## ⚙️ Core Technical Capabilities

### 1. SKU-Level Machine Learning Forecaster
* **Engineered Feature Set:** Calendar seasonality (holiday peaks, fitness surges), auto-regressive lags ($t-1, t-2, t-4$), rolling statistics (4-week mean and std), and promotional discount flags.
* **Algorithm:** Ensembled regression (`RandomForestRegressor`) evaluated on an 8-week out-of-sample test window.
* **Metrics:** Evaluates on **WAPE** (*Weighted Absolute Percentage Error*) and **RMSE**, the gold standard in retail merchandise planning.

### 2. Stochastic Safety Stock & Replenishment Logic
* Incorporates supplier lead-time variability and customer **Cycle-Service Level (CSL)**:
  $$\text{Safety Stock } (SS) = Z \times \sqrt{L} \times \sigma_d$$
  Where:
  * $Z$ = Inverse standard normal distribution value (e.g., $1.645$ for 95% service level)
  * $L$ = Supplier lead time in days
  * $\sigma_d$ = Standard deviation of daily demand
* **Reorder Point (ROP):**
  $$\text{ROP} = (\bar{d} \times L) + SS$$
* Recommends purchase orders rounded to supplier **Minimum Order Quantity (MOQ)** batches.

### 3. Scenario Sandbox & Excel Reporting
* **Promotional Shock Simulator:** Allows planners to test the effect of a +15% to +60% demand surge on stockout risk.
* **1-Click Excel Export:** Generates an enterprise-ready merchandising plan `.xlsx` for store ops and digital trading leads.

---

## 📁 Repository Structure
```text
├── app.py                      # Interactive Streamlit application
├── forecast_engine.py          # ML modeling pipeline, WAPE calculator & ROP mathematics
├── generate_data.py            # Retail sales & inventory time-series synthesizer
├── requirements.txt            # Python dependencies
└── README.md                   # Documentation and business context
```

---

## 🚀 Quickstart Guide

### 1. Clone the repository
```bash
git clone https://github.com/<YOUR_GITHUB_USERNAME>/retail-demand-replenishment-engine.git
cd retail-demand-replenishment-engine
```

### 2. Set up virtual environment & install dependencies
```bash
python3 -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Run the application
```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501`.

---

## 💼 Resume Description (For Planning & Operations Roles)

**OmniStock-AI: SKU Demand Forecasting & Inventory Engine** | *Python, Scikit-Learn, Streamlit, Pandas*
* Built an operational merchandise planning dashboard to predict weekly SKU sales across 4 distribution channels (D2C Direct, Marketplaces, Retail Outlets).
* Designed feature pipelines capturing retail seasonality and promotional lifts, achieving a ~12% WAPE on holdout test sets.
* Formulated stochastic Safety Stock and Reorder Point (ROP) algorithms across 10 SKUs, preventing stockout risks and generating one-click procurement schedules in Excel.
