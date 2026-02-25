from flask import Blueprint, request, jsonify, send_file
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from models.demand_model import DemandForecaster
from models.bi_model import BIModel
import io
import json

reports_bp = Blueprint('reports', __name__)

def generate_forecast_report(days=30):
    """Generate forecast data for reports"""
    forecaster = DemandForecaster()
    predictions = forecaster.predict(days)
    
    df = pd.DataFrame(predictions)
    df['day'] = range(1, len(df) + 1)
    return df

def generate_customer_report():
    """Generate customer analytics data"""
    bi_model = BIModel()
    segments = bi_model.get_segment_profiles(pd.DataFrame())
    return segments

@reports_bp.route('/forecast-pdf', methods=['GET'])
def forecast_pdf():
    """Download forecast as PDF/CSV"""
    format_type = request.args.get('format', 'csv')
    days = int(request.args.get('days', 30))
    
    forecast_df = generate_forecast_report(days)
    
    if format_type == 'csv':
        csv_buffer = io.StringIO()
        forecast_df.to_csv(csv_buffer, index=False)
        return send_file(
            io.BytesIO(csv_buffer.getvalue().encode()),
            mimetype='text/csv',
            as_attachment=True,
            download_name=f'sales_forecast_{datetime.now().strftime("%Y%m%d")}.csv'
        )
    
    # Simple text "PDF" (HTML styled)
    html_content = f"""
    <html>
    <head><title>SalesMind Forecast Report</title>
    <style>
        body {{ font-family: Arial; margin: 40px; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #ddd; padding: 12px; text-align: right; }}
        th {{ background-color: #f2f2f2; }}
        .header {{ text-align: center; font-size: 24px; margin-bottom: 30px; }}
        .summary {{ background: #e8f4f8; padding: 20px; margin: 20px 0; }}
    </style>
    </head>
    <body>
        <div class="header">SalesMind AI - Demand Forecast Report</div>
        <div class="summary">
            <strong>Generated:</strong> {datetime.now().strftime("%Y-%m-%d %H:%M")}<br>
            <strong>Period:</strong> Next {days} days<br>
            <strong>Avg Daily Forecast:</strong> {forecast_df['yhat'].mean():.0f} units
        </div>
        <table>
            <tr><th>Day</th><th>Date</th><th>Forecast</th><th>Lower 85%</th><th>Upper 115%</th></tr>
            {''.join([f'<tr><td>{row.day}</td><td>{row.ds}</td><td>{row.yhat:.0f}</td><td>{row.yhat_lower:.0f}</td><td>{row.yhat_upper:.0f}</td></tr>' for row in forecast_df.itertuples()])}
        </table>
    </body>
    </html>
    """
    
    return send_file(
        io.BytesIO(html_content.encode()),
        mimetype='text/html',
        as_attachment=True,
        download_name=f'forecast_report_{datetime.now().strftime("%Y%m%d")}.html'
    )

@reports_bp.route('/customer-summary', methods=['GET'])
def customer_summary_report():
    """Customer analytics report"""
    format_type = request.args.get('format', 'json')
    
    segments = generate_customer_report()
    
    if format_type == 'csv':
        df = pd.DataFrame(segments)
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False)
        return send_file(
            io.BytesIO(csv_buffer.getvalue().encode()),
            mimetype='text/csv',
            download_name='customer_segments.csv'
        )
    
    return jsonify({
        "success": True,
        "report_type": "Customer Segments",
        "data": segments,
        "generated": datetime.now().isoformat()
    })

@reports_bp.route('/executive-summary', methods=['GET'])
def executive_summary():
    """One-page executive dashboard"""
    forecast = generate_forecast_report(7)
    total_forecast = forecast['yhat'].sum()
    
    return jsonify({
        "success": True,
        "executive_summary": {
            "period": "Next 7 days",
            "total_sales_forecast": f"{total_forecast:.0f} units",
            "avg_daily_forecast": f"{forecast['yhat'].mean():.0f} units",
            "trend": "📈 Growing" if forecast['yhat'].iloc[-1] > forecast['yhat'].iloc[0] else "➡️ Stable",
            "customer_churn": "14.5%",
            "high_value_customers": "1,593 (22.6%)",
            "recommendations": [
                "Increase inventory by 15%",
                "Target at-risk segment (892 customers)",
                "Launch retention campaign"
            ]
        },
        "generated": datetime.now().strftime("%Y-%m-%d %H:%M IST")
    })

@reports_bp.route('/full-report', methods=['POST'])
def full_business_report():
    """Complete business intelligence report"""
    data = request.get_json() or {}
    days = data.get('days', 30)
    
    report = {
        "timestamp": datetime.now().isoformat(),
        "forecast": generate_forecast_report(days),
        "customer_segments": generate_customer_report(),
        "kpis": {
            "total_customers": 7043,
            "churn_rate": 14.5,
            "forecast_total": generate_forecast_report(7)['yhat'].sum()
        }
    }
    
    return jsonify(report)
