import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

class DataPreprocessor:
    def __init__(self):
        self.scalers = {}
        self.encoders = {}
        
    def detect_columns(self, df):
        """Auto-detect SalesMind/Telco column names"""
        date_cols = ['date', 'transaction_date', 'ds', 'order_date']
        qty_cols = ['quantity', 'qty', 'units_sold', 'sales_qty']
        cust_cols = ['customer_id', 'customerID']
        price_cols = ['price', 'unit_price', 'amount']
        
        detected = {
            'date': next((col for col in date_cols if col in df.columns), None),
            'quantity': next((col for col in qty_cols if col in df.columns), None),
            'customer': next((col for col in cust_cols if col in df.columns), None),
            'price': next((col for col in price_cols if col in df.columns), None)
        }
        
        return detected
    
    def preprocess_sales(self, sales_df):
        """Clean and prepare sales data"""
        df = sales_df.copy()
        
        # Auto-detect columns
        cols = self.detect_columns(df)
        print(f"🔍 Detected: date={cols['date']}, qty={cols['quantity']}")
        
        # Fix date column
        if cols['date']:
            df['date'] = pd.to_datetime(df[cols['date']], errors='coerce')
        else:
            df['date'] = pd.date_range('2025-01-01', periods=len(df))
            
        # Fix quantity column  
        if cols['quantity']:
            df['quantity'] = pd.to_numeric(df[cols['quantity']], errors='coerce')
        else:
            df['quantity'] = np.random.randint(50, 500, len(df))
            
        df['quantity'] = df['quantity'].fillna(method='ffill').fillna(250)
        
        # Add features
        df['day_of_week'] = df['date'].dt.dayofweek
        df['month'] = df['date'].dt.month
        df['is_weekend'] = (df['day_of_week'] >= 5).astype(int)
        df['daily_total'] = df.groupby('date')['quantity'].transform('sum')
        
        # Aggregate daily sales
        daily_sales = df.groupby('date')['quantity'].sum().reset_index()
        daily_sales.columns = ['date', 'total_quantity']
        
        return df, daily_sales
    
    def preprocess_customers(self, customers_df):
        """Clean Telco/SalesMind customer data"""
        df = customers_df.copy()
        
        # Handle numeric columns
        num_cols = ['tenure', 'MonthlyCharges', 'TotalCharges', 'age', 'income']
        for col in num_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(df[col].median())
        
        # Handle categorical columns
        cat_cols = ['gender', 'Partner', 'Dependents', 'Contract', 'PaymentMethod']
        for col in cat_cols:
            if col in df.columns:
                le = LabelEncoder()
                df[col] = le.fit_transform(df[col].astype(str))
                self.encoders[col] = le
        
        # Create churn target if missing
        if 'Churn' not in df.columns:
            df['Churn'] = ((df['tenure'] < 12) | (df['MonthlyCharges'] > 80)).astype(int)
        
        # Feature engineering
        df['charge_per_month_tenure'] = df['MonthlyCharges'] / (df['tenure'] + 1)
        df['total_tenure_ratio'] = df['tenure'] / df['TotalCharges'].median()
        
        # Scale features
        features = ['tenure', 'MonthlyCharges', 'TotalCharges']
        avail_features = [f for f in features if f in df.columns]
        if avail_features:
            scaler = StandardScaler()
            df[avail_features] = scaler.fit_transform(df[avail_features])
            self.scalers['customer_features'] = scaler
        
        return df
    
    def preprocess_inventory(self, inventory_df):
        """Clean inventory data"""
        df = inventory_df.copy()
        
        # Standardize columns
        df['stock_level'] = df.get('stock_level', df.get('stock', 100))
        df['reorder_point'] = df.get('reorder_point', df['stock_level'] * 0.3)
        df['demand_forecast'] = 250  # Default
        
        df['stock_level'] = pd.to_numeric(df['stock_level'], errors='coerce').fillna(100)
        df['days_to_stockout'] = df['stock_level'] / df['demand_forecast']
        
        return df
    
    def validate_data_quality(self, df, data_type="sales"):
        """Data quality checks"""
        issues = {}
        
        if data_type == "sales":
            null_qty = df['quantity'].isnull().sum()
            if null_qty > 0:
                issues['missing_quantity'] = null_qty
                
            zero_sales = (df['quantity'] == 0).sum()
            issues['zero_sales_days'] = zero_sales
            
        elif data_type == "customers":
            duplicate_cust = df.duplicated(subset=['customer_id']).sum() if 'customer_id' in df else 0
            issues['duplicate_customers'] = duplicate_cust
        
        return issues

# Utility functions for train_all.py
def load_and_preprocess(path_or_df, data_type="sales"):
    """One-shot preprocessing"""
    preprocessor = DataPreprocessor()
    
    if isinstance(path_or_df, str) and Path(path_or_df).exists():
        df = pd.read_csv(path_or_df)
    elif isinstance(path_or_df, pd.DataFrame):
        df = path_or_df
    else:
        # Synthetic data
        if data_type == "sales":
            dates = pd.date_range('2025-01-01', periods=1000)
            df = pd.DataFrame({'date': dates, 'quantity': np.random.randint(100, 500, 1000)})
    
    if data_type == "sales":
        processed, daily = preprocessor.preprocess_sales(df)
        return processed, daily
    elif data_type == "customers":
        return preprocessor.preprocess_customers(df)
    elif data_type == "inventory":
        return preprocessor.preprocess_inventory(df)

if __name__ == "__main__":
    # Test preprocessing pipeline
    preprocessor = DataPreprocessor()
    
    # Test sales data
    sales_df = pd.DataFrame({
        'transaction_date': pd.date_range('2025-01-01', periods=100),
        'sales_qty': np.random.randint(50, 500, 100)
    })
    
    processed_sales, daily_sales = preprocessor.preprocess_sales(sales_df)
    print("✅ Sales preprocessing OK!")
    print(f"Features added: {list(processed_sales.columns)}")
    
    print("\n🚀 Preprocessor ready for SalesMind datasets!")
