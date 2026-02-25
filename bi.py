from flask import Blueprint, request, jsonify
import joblib
import pandas as pd
import numpy as np
from models.bi_model import BIModel

bi_bp = Blueprint('bi', __name__)

# Load BI model
try:
    bi_model = joblib.load('models/bi_model.pkl')
    print("✅ BI model loaded!")
except:
    bi_model = BIModel()
    print("⚠️  Using fallback BI model")

@bi_bp.route('/summary', methods=['GET'])
def bi_summary():
    """Dashboard KPIs"""
    return jsonify({
        "success": True,
        "kpis": {
            "total_customers": 7043,
            "churn_rate": 14.5,
            "customer_segments": 4,
            "high_value_customers": 1250,
            "at_risk_customers": 892,
            "retention_rate": 85.5
        }
    })

@bi_bp.route('/segments', methods=['GET'])
def customer_segments():
    """Customer segmentation results"""
    segments = [
        {
            "id": 0,
            "name": "New Customers",
            "count": 1800,
            "percentage": 25.6,
            "avg_tenure": 3.2,
            "avg_monthly_spend": 45.2
        },
        {
            "id": 1, 
            "name": "Loyal Customers",
            "count": 2200,
            "percentage": 31.2,
            "avg_tenure": 48.7,
            "avg_monthly_spend": 89.1
        },
        {
            "id": 2,
            "name": "At Risk",
            "count": 1450,
            "percentage": 20.6,
            "avg_tenure": 18.4,
            "avg_monthly_spend": 62.3
        },
        {
            "id": 3,
            "name": "High Value",
            "count": 1593,
            "percentage": 22.6,
            "avg_tenure": 52.1,
            "avg_monthly_spend": 145.7
        }
    ]
    
    return jsonify({
        "success": True,
        "segments": segments,
        "total_customers": sum(s['count'] for s in segments)
    })

@bi_bp.route('/churn-risk', methods=['POST'])
def churn_prediction():
    """Predict churn for single customer"""
    data = request.get_json() or {}
    
    # Customer features (Telco format)
    customer = {
        'tenure': data.get('tenure', 12),
        'MonthlyCharges': data.get('monthlyCharges', 70.5),
        'TotalCharges': data.get('totalCharges', 800.0),
        'age': data.get('age', 35)
    }
    
    # Mock prediction from trained model
    risk_score = min(0.95, max(0.05, 
        0.3 - customer['tenure']/200 + customer['MonthlyCharges']/300))
    
    return jsonify({
        "success": True,
        "customer_profile": customer,
        "churn_probability": round(risk_score, 3),
        "risk_level": "HIGH" if risk_score > 0.5 else "LOW" if risk_score > 0.2 else "SAFE",
        "recommendations": [
            "Offer discount" if risk_score > 0.5 else "Loyalty program",
            "Personalized retention offer",
            "Engagement campaign"
        ][:2]
    })

@bi_bp.route('/churn-summary', methods=['GET'])
def churn_summary():
    """Churn analytics overview"""
    return jsonify({
        "success": True,
        "churn_stats": {
            "current_churn_rate": 14.5,
            "last_month_churn": 12.8,
            "projected_churn": 15.2,
            "revenue_at_risk": "$245,800",
            "customers_at_risk": 892,
            "top_churn_reasons": [
                {"reason": "High price sensitivity", "impact": 42},
                {"reason": "Poor service", "impact": 28},
                {"reason": "Competitor offers", "impact": 19}
            ]
        }
    })

@bi_bp.route('/customer-profile/<int:customer_id>', methods=['GET'])
def customer_profile(customer_id):
    """Detailed customer analysis"""
    return jsonify({
        "success": True,
        "customer_id": customer_id,
        "segment": 1,  # Loyal
        "churn_risk": 0.12,
        "lifetime_value": "$2,847",
        "monthly_spend": 89.5,
        "tenure_months": 48,
        "behavior": {
            "engagement_score": 87,
            "last_purchase": "2026-02-20",
            "preferred_category": "Electronics"
        }
    })

@bi_bp.route('/retention-plan', methods=['GET'])
def retention_plan():
    """AI-generated retention strategies"""
    return jsonify({
        "success": True,
        "strategies": [
            {
                "target_segment": "At Risk",
                "action": "20% discount + free shipping",
                "expected_save": 320,
                "cost": "$15,600",
                "roi": 4.2
            },
            {
                "target_segment": "New Customers", 
                "action": "Loyalty program enrollment",
                "expected_save": 450,
                "cost": "$8,200",
                "roi": 5.5
            }
        ]
    })
