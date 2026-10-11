import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import root_mean_squared_error
from scipy.stats import norm
import os

def load_and_preprocess(filepath="data/sales_inventory_data.csv"):
    if not os.path.exists(filepath):
        from generate_data import generate_retail_sales_data
        generate_retail_sales_data(filepath)
        
    df = pd.read_csv(filepath)
    df["week_start"] = pd.to_datetime(df["week_start"])
    df = df.sort_values(["sku_id", "channel", "week_start"]).reset_index(drop=True)
    return df

def calculate_wape(y_true, y_pred):
    """Weighted Absolute Percentage Error (standard metric in retail supply chain)"""
    y_true, y_pred = np.array(y_true), np.array(y_pred)
    sum_true = np.sum(y_true)
    if sum_true == 0:
        return 0.0
    return np.sum(np.abs(y_true - y_pred)) / sum_true

def train_demand_model_for_sku(df, sku_id, test_weeks=8):
    """Trains a demand forecasting model for a selected SKU aggregated across channels"""
    sku_df = df[df["sku_id"] == sku_id].groupby("week_start").agg({
        "units_sold": "sum",
        "revenue_inr": "sum",
        "discount_pct": "mean",
        "is_promo": "max",
        "stock_on_hand": "sum",
        "lead_time_days": "first",
        "moq": "first",
        "base_price": "first"
    }).reset_index()
    
    sku_df["month"] = sku_df["week_start"].dt.month
    sku_df["week_num"] = sku_df["week_start"].dt.isocalendar().week
    
    # Lag and Rolling features
    for lag in [1, 2, 4]:
        sku_df[f"lag_{lag}"] = sku_df["units_sold"].shift(lag)
    sku_df["rolling_mean_4"] = sku_df["units_sold"].shift(1).rolling(4).mean()
    sku_df["rolling_std_4"] = sku_df["units_sold"].shift(1).rolling(4).std().fillna(0)
    
    clean_df = sku_df.dropna().reset_index(drop=True)
    if len(clean_df) <= test_weeks:
        return None, clean_df, None
        
    features = ["month", "week_num", "discount_pct", "is_promo", "lag_1", "lag_2", "lag_4", "rolling_mean_4", "rolling_std_4"]
    target = "units_sold"
    
    train = clean_df.iloc[:-test_weeks]
    test = clean_df.iloc[-test_weeks:]
    
    model = RandomForestRegressor(n_estimators=100, random_state=42, max_depth=6)
    model.fit(train[features], train[target])
    
    test_preds = model.predict(test[features])
    wape = calculate_wape(test[target], test_preds)
    rmse = root_mean_squared_error(test[target], test_preds)
    
    metrics = {
        "wape": round(wape * 100, 2),
        "rmse": round(rmse, 2),
        "avg_weekly_demand": round(train[target].mean(), 1)
    }
    
    clean_df["predicted_units"] = np.nan
    clean_df.loc[clean_df.index[-test_weeks:], "predicted_units"] = np.round(test_preds, 0)
    
    return model, clean_df, metrics

def calculate_replenishment_plan(df, service_level=0.95):
    """Calculates Safety Stock, Reorder Point (ROP), and Order Recommendations across all SKUs"""
    z_score = norm.ppf(service_level)
    
    results = []
    for sku_id, group in df.groupby("sku_id"):
        weekly_group = group.groupby("week_start").agg({
            "units_sold": "sum",
            "stock_on_hand": "sum",
            "sku_name": "first",
            "category": "first",
            "lead_time_days": "first",
            "moq": "first",
            "base_price": "first"
        }).reset_index()
        
        avg_demand_per_day = weekly_group["units_sold"].mean() / 7.0
        demand_std_per_day = (weekly_group["units_sold"].std() / np.sqrt(7.0)) if len(weekly_group) > 1 else 10.0
        
        lead_time = weekly_group["lead_time_days"].iloc[0]
        moq = weekly_group["moq"].iloc[0]
        current_stock = weekly_group["stock_on_hand"].iloc[-1]
        
        # Safety Stock formula: Z * sqrt(LeadTime) * sigma_daily
        safety_stock = int(np.ceil(z_score * np.sqrt(lead_time) * demand_std_per_day))
        
        # Lead time demand = average daily demand * lead time in days
        lead_time_demand = int(np.ceil(avg_demand_per_day * lead_time))
        
        # Reorder Point (ROP) = Lead Time Demand + Safety Stock
        reorder_point = lead_time_demand + safety_stock
        
        # Stockout Risk: if current stock <= ROP
        stockout_risk = "HIGH (Action Needed)" if current_stock < reorder_point else "OPTIMAL"
        
        # Suggested Order Quantity
        units_to_order = 0
        if current_stock < reorder_point:
            needed = reorder_point - current_stock
            units_to_order = int(np.ceil(needed / moq) * moq)  # rounded to MOQ
            
        capital_required = units_to_order * weekly_group["base_price"].iloc[0]
        
        results.append({
            "SKU ID": sku_id,
            "Product Name": weekly_group["sku_name"].iloc[0],
            "Category": weekly_group["category"].iloc[0],
            "Current Stock": current_stock,
            "Lead Time (Days)": lead_time,
            "Safety Stock (Units)": safety_stock,
            "Reorder Point (ROP)": reorder_point,
            "Stockout Status": stockout_risk,
            "Recommended Order": units_to_order,
            "Working Capital (INR)": capital_required
        })
        
    return pd.DataFrame(results)
