import csv
import random
import os
from datetime import datetime, timedelta

def generate_retail_sales_data(output_path="data/sales_inventory_data.csv"):
    random.seed(42)
    
    skus = [
        {"sku_id": "FTW-RUN-001", "name": "Nitro Speed Performance Running Shoes", "category": "Footwear", "base_price": 11999, "lead_time_days": 18, "moq": 150},
        {"sku_id": "FTW-RUN-002", "name": "Carbon Elite Marathon Racing Shoes", "category": "Footwear", "base_price": 15999, "lead_time_days": 21, "moq": 100},
        {"sku_id": "FTW-LST-003", "name": "Classic Suede Heritage Sneakers", "category": "Footwear", "base_price": 6999, "lead_time_days": 14, "moq": 250},
        {"sku_id": "FTW-LST-004", "name": "Retro Court Unisex Streetwear Shoes", "category": "Footwear", "base_price": 8999, "lead_time_days": 15, "moq": 200},
        {"sku_id": "APP-TRN-101", "name": "AeroDry Moisture-Wicking Running Tee", "category": "Apparel", "base_price": 1999, "lead_time_days": 10, "moq": 500},
        {"sku_id": "APP-TRN-102", "name": "Thermal Tech Full-Zip Training Hoodie", "category": "Apparel", "base_price": 4499, "lead_time_days": 12, "moq": 300},
        {"sku_id": "APP-SPB-103", "name": "Pro Club Matchday Official Jersey", "category": "Apparel", "base_price": 4999, "lead_time_days": 20, "moq": 250},
        {"sku_id": "ACC-EQP-201", "name": "Pro Active Athletic Backpack 24L", "category": "Accessories", "base_price": 1499, "lead_time_days": 10, "moq": 400},
        {"sku_id": "ACC-EQP-202", "name": "Ergonomic Sports Water Bottle 750ml", "category": "Accessories", "base_price": 799, "lead_time_days": 7, "moq": 600},
        {"sku_id": "MTR-RAC-301", "name": "Motorsport Track Heritage Jacket", "category": "Motorsport", "base_price": 7999, "lead_time_days": 16, "moq": 150}
    ]
    
    channels = ["D2C Brand Store (Direct)", "Marketplaces (Myntra/Amazon)", "Exclusive Brand Outlets (EBO)", "Multi-Brand Retailers"]
    channel_shares = [0.35, 0.30, 0.25, 0.10]
    
    start_date = datetime(2025, 1, 1)
    weeks = 60
    dates = [start_date + timedelta(weeks=w) for w in range(weeks)]
    
    records = []
    
    for sku in skus:
        base_demand = random.randint(200, 500)
        
        for w_idx, current_date in enumerate(dates):
            month = current_date.month
            
            # Retail Seasonality:
            # Oct-Nov: Festive peak
            # Jan-Feb: Fitness / Marathon season
            # May-June: Summer sprint sales
            seasonality = 1.0
            if month in [10, 11]:
                seasonality = 1.45
            elif month in [1, 2]:
                seasonality = 1.30
            elif month in [5, 6]:
                seasonality = 1.20
            
            is_promo_week = 1 if (w_idx % 8 == 0 or month in [10, 11]) else 0
            discount_pct = random.choice([10, 15, 20, 30]) if is_promo_week else random.choice([0, 0, 5])
            promo_lift = 1.0 + (discount_pct / 100.0) * 1.2
            
            noise = random.gauss(1.0, 0.08)
            total_weekly_units = int(base_demand * seasonality * promo_lift * noise)
            total_weekly_units = max(total_weekly_units, 20)
            
            for ch, share in zip(channels, channel_shares):
                ch_units = int(total_weekly_units * share)
                selling_price = round(sku["base_price"] * (1 - discount_pct / 100.0), 2)
                revenue = ch_units * selling_price
                stock_on_hand = max(0, int(ch_units * random.uniform(1.2, 3.5)))
                
                records.append({
                    "week_start": current_date.strftime("%Y-%m-%d"),
                    "sku_id": sku["sku_id"],
                    "sku_name": sku["name"],
                    "category": sku["category"],
                    "channel": ch,
                    "units_sold": ch_units,
                    "base_price": sku["base_price"],
                    "discount_pct": discount_pct,
                    "effective_price": selling_price,
                    "revenue_inr": revenue,
                    "stock_on_hand": stock_on_hand,
                    "lead_time_days": sku["lead_time_days"],
                    "moq": sku["moq"],
                    "is_promo": is_promo_week
                })
                
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    headers = [
        "week_start", "sku_id", "sku_name", "category", "channel",
        "units_sold", "base_price", "discount_pct", "effective_price",
        "revenue_inr", "stock_on_hand", "lead_time_days", "moq", "is_promo"
    ]
    
    with open(output_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(records)
        
    print(f"Generated {len(records)} sales records written to {output_path}")

if __name__ == "__main__":
    generate_retail_sales_data()
