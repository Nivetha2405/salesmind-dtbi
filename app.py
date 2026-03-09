import io
import pandas as pd
import csv
import os
from flask import Flask, jsonify, send_file, request, render_template
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
CORS(app)

# HEALTH CHECK ✅
@app.route('/api/health')
def health():
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()})

# HTML TEMPLATES - ALL 6 PAGES ✅
@app.route('/')
def index(): return render_template('index.html')

@app.route('/login')
def login(): return render_template('login.html')

@app.route('/dashboard')
def dashboard(): return render_template('dashboard.html')

@app.route('/forecast')
def forecast(): return render_template('forecast.html')

@app.route('/reports')
def reports(): return render_template('reports.html')

@app.route('/twin')
def twin(): return render_template('twin.html')

@app.route('/logout')
def logout():
    return render_template('login.html')

@app.route("/signup")
def signup():
    return render_template("signup.html")


# CSV REPORT GENERATOR - FIXED ✅
@app.route('/api/reports/<report_type>')
def generate_report(report_type):
    if report_type == 'forecast':
        buffer = io.StringIO()
        writer = csv.writer(buffer)
        writer.writerow(['Date', 'Predicted Demand', 'Lower CI', 'Upper CI'])
        
        # 30-Day forecast data
        for i in range(30):
            date = f"2026-03-{i+1:02d}"
            demand = 250 + i * 2 + (i % 7 * 20)
            lower_ci = round(demand * 0.9, 1)
            upper_ci = round(demand * 1.1, 1)
            writer.writerow([date, demand, lower_ci, upper_ci])
        
        buffer.seek(0)
        csv_content = buffer.getvalue().encode('utf-8')
        
        return send_file(
            io.BytesIO(csv_content),
            mimetype='text/csv',
            as_attachment=True,
            download_name=f'salesmind-forecast-{datetime.now().strftime("%Y%m%d")}.csv'
        )
    return jsonify({"error": "Report type not found"}), 404

# DASHBOARD METRICS ✅
@app.route('/api/dashboard/metrics')
def dashboard_metrics():
    return jsonify({
        "revenue": 125400,
        "growth": 12.5,
        "customers": 2450,
        "orders": 890
    })

# FORECAST PREDICTIONS ✅
@app.route('/api/forecast/predict')
def forecast_predict():
    return jsonify({
        "predictions": [
            {"date": "2026-02-25", "demand": 285},
            {"date": "2026-02-26", "demand": 312},
            {"date": "2026-02-27", "demand": 298}
        ],
        "accuracy": 94.7
    })

# DETAILED FORECAST (Chart data) ✅
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

# STOCK INTELLIGENCE ✅
@app.route('/api/stock/predict')
def stock_predict():
    return jsonify({
        "current_stock": 1245,
        "predicted_demand_30d": 8500,
        "reorder_level": 2000,
        "days_to_reorder": 7,
        "optimal_order_qty": 3200,
        "risk_level": "HIGH"
    })

# WHAT-IF SIMULATION ✅
@app.route('/api/simulation')
def simulation():
    scenario = request.args.get('demand_increase', '10')
    revenue_impact = 24500 if scenario == '10' else 61250 if scenario == '25' else 122500
    stock_needed = 9350 if scenario == '10' else 12750 if scenario == '25' else 21250
    
    return jsonify({
        "scenario": f"Demand +{scenario}%",
        "revenue_impact": revenue_impact,
        "stock_needed": stock_needed,
        "risk_level": "LOW"
    })

# DATASET UPLOAD API ✅
@app.route('/api/upload-dataset', methods=['POST'])
def upload_dataset():

    if 'dataset' not in request.files:
        return jsonify({"error": "No dataset file provided"}), 400

    file = request.files['dataset']

    try:
        df = pd.read_csv(file)

        return jsonify({
            "status": "success",
            "rows": len(df),
            "columns": list(df.columns),
            "message": "Dataset uploaded successfully"
        })

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
