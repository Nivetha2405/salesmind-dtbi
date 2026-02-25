import io
import csv
import os
from flask import Flask, jsonify, send_file , request
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
CORS(app)


@app.route("/")
def home():
    return {"message": "SalesMind DTBI API is Running"}

@app.route('/api/reports/<report_type>')
def generate_report(report_type):
    if report_type == 'forecast':
        buffer = io.StringIO()
        writer = csv.writer(buffer)
        writer.writerow(['Date', 'Predicted Demand', 'Lower CI', 'Upper CI'])
        
        # Mock forecast data
        for i in range(30):
            date = f"2026-03-{i+1:02d}"
            demand = 250 + i * 2 + (i % 7 * 20)
            writer.writerow([date, demand, demand*0.9, demand*1.1])
        
        buffer.seek(0)
        return send_file(
            io.BytesIO(buffer.getvalue().encode('utf-8')),
            mimetype='text/csv',
            as_attachment=True,
            download_name=f'salesmind-forecast-{datetime.now().strftime("%Y%m%d")}.csv'
        )
    
    return "Report not found", 404

@app.route('/api/health')
def health():
    return jsonify({"status": "healthy"})

@app.route('/api/dashboard/metrics')
def dashboard_metrics():
    return jsonify({
        "revenue": 125400,
        "growth": 12.5,
        "customers": 2450,
        "orders": 890
    })

@app.route('/api/forecast/predict')
def forecast_predict():
    return jsonify({
        "predictions": [
            {"date": "2026-02-25", "demand": 285},
            {"date": "2026-02-26", "demand": 312}
        ]
    })


# SALES FORECAST (Actual vs Predicted) 
@app.route('/api/forecast/detailed')
def forecast_detailed():
    dates = [f"2026-0{i:02d}-01" for i in range(1, 13)]
    actual = [250, 280, 320, 290, 350, 380, 410, 390, 420, 450, 470, 500]
    predicted = [255, 275, 315, 295, 355, 385, 405, 395, 425, 455, 465, 495]
    
    return jsonify({
        "dates": dates,
        "actual": actual,
        "predicted": predicted,
        "rmse": 12.5,
        "mae": 8.2,
        "accuracy": 94.7
    })

# STOCK LEVEL PREDICTION 
@app.route('/api/stock/predict')
def stock_predict():
    return jsonify({
        "current_stock": 1245,
        "predicted_demand_30d": 8500,
        "reorder_level": 2000,
        "days_to_reorder": 7,
        "optimal_order_qty": 3200
    })

# SIMULATION (What-if Analysis) - 
@app.route('/api/simulation')
def simulation():
    scenario = request.args.get('demand_increase', '10')
    return jsonify({
        "scenario": f"Demand +{scenario}%",
        "revenue_impact": 24500,
        "stock_needed": 9350,
        "risk_level": "LOW"
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)



