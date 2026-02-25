import pandas as pd
import numpy as np
from models.demand_model import DemandForecaster
from models.bi_model import BIModel
from utils.preprocess import DataPreprocessor
import json

class VisualizationEngine:
    def __init__(self):
        self.forecaster = DemandForecaster()
        self.bi_model = BIModel()
        self.preprocessor = DataPreprocessor()
    
    def forecast_chart_data(self, days=30):
        """Line chart data for forecast dashboard"""
        predictions = self.forecaster.predict(days)
        
        return {
            "type": "line",
            "labels": [p['ds'] for p in predictions],
            "datasets": [
                {
                    "label": "Forecast",
                    "data": [p['yhat'] for p in predictions],
                    "borderColor": "#4F46E5",
                    "backgroundColor": "rgba(79, 70, 229, 0.1)",
                    "fill": True,
                    "tension": 0.4
                },
                {
                    "label": "Lower Bound", 
                    "data": [p['yhat_lower'] for p in predictions],
                    "borderColor": "#10B981",
                    "borderDash": [5, 5],
                    "fill": False
                },
                {
                    "label": "Upper Bound",
                    "data": [p['yhat_upper'] for p in predictions],
                    "borderColor": "#10B981",
                    "borderDash": [5, 5],
                    "fill": False
                }
            ]
        }
    
    def sales_trend_data(self, days=90):
        """Sales trend with seasonality"""
        dates = pd.date_range(end=pd.Timestamp.now(), periods=days, freq='D')
        base_trend = 250
        
        sales_data = []
        for i, date in enumerate(dates):
            # Trend + weekly seasonality + noise
            seasonal = 1 + 0.15 * np.sin(2 * np.pi * i / 7)
            daily_sales = base_trend * seasonal * (1 + 0.02 * i / days)  # Growth
            sales_data.append(daily_sales + np.random.normal(0, 20))
        
        return {
            "type": "line",
            "labels": [d.strftime('%m-%d') for d in dates],
            "datasets": [
                {
                    "label": "Daily Sales",
                    "data": sales_data,
                    "borderColor": "#3B82F6",
                    "backgroundColor": "rgba(59, 130, 246, 0.1)",
                    "fill": True
                }
            ]
        }
    
    def customer_segment_chart(self):
        """Pie/doughnut chart for segments"""
        segments = [
            {"name": "New", "value": 1800, "color": "#10B981"},
            {"name": "Loyal", "value": 2200, "color": "#3B82F6"},
            {"name": "At Risk", "value": 1450, "color": "#F59E0B"},
            {"name": "High Value", "value": 1593, "color": "#8B5CF6"}
        ]
        
        return {
            "type": "doughnut",
            "labels": [s['name'] for s in segments],
            "datasets": [{
                "data": [s['value'] for s in segments],
                "backgroundColor": [s['color'] for s in segments],
                "borderWidth": 2
            }]
        }
    
    def churn_trend_data(self):
        """Churn rate over time"""
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
        churn_rates = [12.3, 13.8, 14.5, 13.2, 15.1, 14.5]
        
        return {
            "type": "bar",
            "labels": months,
            "datasets": [
                {
                    "label": "Churn Rate (%)",
                    "data": churn_rates,
                    "backgroundColor": "#EF4444",
                    "borderRadius": 4
                }
            ]
        }
    
    def inventory_status_data(self):
        """Gauge/bar chart for inventory health"""
        status = {
            "safe": 65,
            "low": 25, 
            "critical": 10
        }
        
        return {
            "type": "doughnut",
            "labels": ["Safe", "Low", "Critical"],
            "datasets": [{
                "data": [status['safe'], status['low'], status['critical']],
                "backgroundColor": ["#10B981", "#F59E0B", "#EF4444"]
            }]
        }
    
    def kpi_cards(self):
        """Dashboard KPI metrics"""
        return {
            "total_sales": 125000,
            "total_customers": 7043,
            "churn_rate": 14.5,
            "forecast_next_7d": 1850,
            "inventory_health": 92,
            "revenue_growth": 8.2
        }

# API-ready functions
def get_dashboard_charts():
    """All charts for main dashboard"""
    viz = VisualizationEngine()
    
    return {
        "forecast": viz.forecast_chart_data(14),
        "sales_trend": viz.sales_trend_data(30),
        "segments": viz.customer_segment_chart(),
        "churn": viz.churn_trend_data(),
        "inventory": viz.inventory_status_data(),
        "kpis": viz.kpi_cards()
    }

def get_forecast_chart(days=30):
    viz = VisualizationEngine()
    return viz.forecast_chart_data(days)

if __name__ == "__main__":
    # Test visualization data
    viz = VisualizationEngine()
    
    charts = get_dashboard_charts()
    print("✅ Visualization data ready!")
    print("📊 Sample forecast:", json.dumps(charts['forecast']['datasets'][0]['data'][:5], indent=2))
    
    print("\n🚀 Ready for React/Chart.js frontend!")
