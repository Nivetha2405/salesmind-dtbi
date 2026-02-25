import pandas as pd
import numpy as np
import joblib
from datetime import datetime, timedelta

class DemandForecaster:
    def __init__(self):
        self.trend = 250
        self.seasonal_pattern = None
        
    def train(self, sales_df):
        """Simple Moving Average + Seasonal decomposition"""
        df = sales_df.sort_values('date').reset_index(drop=True)
        df['quantity'] = pd.to_numeric(df['quantity'], errors='coerce').fillna(250)
        
        # Calculate trend (30-day moving average)
        self.trend = df['quantity'].tail(30).mean()
        
        # Weekly seasonal pattern (7-day cycle)
        self.seasonal_pattern = df['quantity'].tail(28).groupby(df['date'].dt.dayofweek).mean()
        
        print(f"✅ Trained! Trend: {self.trend:.0f}")
        return True
    
    def predict(self, days_ahead=30):
        """Generate forecast using trend + seasonality"""
        dates = pd.date_range(start=datetime.now().date(), periods=days_ahead, freq='D')
        result = []
        
        for i, date in enumerate(dates):
            # Trend + weekly seasonality + noise
            day_of_week = date.dayofweek
            seasonal = self.seasonal_pattern.get(day_of_week, self.trend)
            forecast = self.trend + (seasonal - self.trend) * 0.3 + np.random.normal(0, 15)
            
            result.append({
                'ds': date.strftime('%Y-%m-%d'),
                'yhat': float(forecast),
                'yhat_lower': float(forecast * 0.85),
                'yhat_upper': float(forecast * 1.15)
            })
        return result
