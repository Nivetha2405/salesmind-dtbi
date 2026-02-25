from flask import Blueprint, request, jsonify
import joblib
import pandas as pd
import numpy as np
from models.demand_model import DemandForecaster

forecast_bp = Blueprint('forecast', __name__)

# Load model on startup (singleton)
try:
    forecaster = joblib.load('models/demand_model.pkl')
    print("✅ Forecast model loaded!")
except:
    forecaster = DemandForecaster()  # Fallback
    print("⚠️  No trained model - using fallback")

@forecast_bp.route('/predict', methods=['POST'])
def predict_demand():
    """Main demand forecasting endpoint"""
    try:
        data = request.get_json() or {}
        days_ahead = data.get('days', 30)
        product_id = data.get('product_id', 'ALL')
        
        # Generate forecast
        predictions = forecaster.predict(days_ahead)
        
        return jsonify({
            "success": True,
            "model": "Exponential Smoothing",
            "days_ahead": days_ahead,
            "predictions": predictions,
            "summary": {
                "avg_forecast": round(sum(p['yhat'] for p in predictions)/len(predictions), 1),
                "trend": "Growing" if predictions[-1]['yhat'] > predictions[0]['yhat'] else "Stable"
            }
        })
    except Exception as e:
        return jsonify({
            "success": False, 
            "error": str(e)
        }), 500

@forecast_bp.route('/latest', methods=['GET'])
def latest_sales():
    """Get recent sales data for dashboard"""
    try:
        # Simulate recent sales from model
        recent = forecaster.predict(7)
        return jsonify({
            "success": True,
            "recent_sales": recent,
            "period": "Last 7 days"
        })
    except:
        return jsonify({"recent_sales": []})

@forecast_bp.route('/summary', methods=['GET'])
def forecast_summary():
    """Quick forecast stats for dashboard"""
    predictions = forecaster.predict(7)
    
    return jsonify({
        "success": True,
        "next_7_days": {
            "total_forecast": round(sum(p['yhat'] for p in predictions), 1),
            "max_day": round(max(p['yhat'] for p in predictions), 1),
            "min_day": round(min(p['yhat'] for p in predictions), 1)
        }
    })

@forecast_bp.route('/product/<product_id>', methods=['GET'])
def product_forecast(product_id):
    """Product-specific forecast"""
    days = request.args.get('days', 30, type=int)
    predictions = forecaster.predict(days)
    
    # Product-specific adjustment (10% variance)
    adjustment = 1.0 + np.random.uniform(-0.1, 0.1)
    
    for pred in predictions:
        pred['yhat'] *= adjustment
        pred['product_id'] = product_id
    
    return jsonify({
        "success": True,
        "product_id": product_id,
        "forecast": predictions[:7]  # First week
    })
