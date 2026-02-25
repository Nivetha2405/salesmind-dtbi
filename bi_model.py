import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import accuracy_score, silhouette_score
from sklearn.decomposition import PCA
import joblib
import warnings
warnings.filterwarnings('ignore')

class BIModel:
    def __init__(self):
        self.segment_model = None
        self.churn_model = None
        self.scaler = StandardScaler()
        self.label_encoders = {}
        self.pca = None
        self.segments = None
        
    def preprocess_customers(self, customers_df):
        """Handle Telco Churn + SalesMind customer data"""
        df = customers_df.copy()
        
        # Telco Churn columns
        telco_cols = ['tenure', 'MonthlyCharges', 'TotalCharges', 'gender', 
                     'SeniorCitizen', 'Partner', 'Dependents', 'Contract']
        
        # SalesMind customer columns  
        salesmind_cols = ['customer_id', 'age', 'income', 'spending_score', 'tenure']
        
        # Select available features
        num_features = ['tenure', 'MonthlyCharges', 'TotalCharges', 'age', 'income', 'spending_score']
        cat_features = ['gender', 'SeniorCitizen', 'Partner', 'Dependents', 'Contract']
        
        available_num = [col for col in num_features if col in df.columns]
        available_cat = [col for col in cat_features if col in df.columns]
        
        print(f"🔧 Using features: {available_num} | {available_cat}")
        
        # Encode categorical
        for col in available_cat:
            le = LabelEncoder()
            df[col] = le.fit_transform(df[col].astype(str))
            self.label_encoders[col] = le
        
        # Fill missing values
        for col in available_num:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(df[col].median())
        
        # Select final features
        X = df[available_num + available_cat].fillna(0)
        return X
    
    def train_segmentation(self, customers_df, n_clusters=4):
        """KMeans customer segmentation (Mall/Telco style)"""
        print("🎯 Training Customer Segmentation...")
        
        X = self.preprocess_customers(customers_df)
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # KMeans clustering
        self.segment_model = KMeans(
            n_clusters=n_clusters, 
            random_state=42, 
            n_init=10,
            max_iter=300
        )
        
        self.segments = self.segment_model.fit_predict(X_scaled)
        
        # PCA for visualization (2D)
        self.pca = PCA(n_components=2)
        self.pca_result = self.pca.fit_transform(X_scaled)
        
        silhouette = silhouette_score(X_scaled, self.segments)
        print(f"✅ Segments trained! Silhouette Score: {silhouette:.3f}")
        
        return self.segments
    
    def train_churn(self, customers_df):
        """Churn prediction using RandomForest"""
        print("🚫 Training Churn Prediction...")
        
        df = customers_df.copy()
        X = self.preprocess_customers(df)
        
        # Create target if missing
        if 'Churn' not in df.columns:
            # Synthetic churn based on low tenure/high charges
            df['Churn'] = ((df['tenure'] < 12) | (df['MonthlyCharges'] > 80)).astype(int)
            print("ℹ️  Created synthetic Churn target")
        
        y = df['Churn'].astype(int)
        
        # Train model
        self.churn_model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
        self.churn_model.fit(X, y)
        
        # Accuracy
        train_pred = self.churn_model.predict(X)
        accuracy = accuracy_score(y, train_pred)
        print(f"✅ Churn model trained! Accuracy: {accuracy:.1%}")
        
        return accuracy
    
    def predict_churn(self, customer_data):
        """Predict churn probability for single customer"""
        if not self.churn_model:
            return 0.15  # Default churn rate
        
        X = self.preprocess_customer(customer_data)
        X_scaled = self.scaler.transform(X)
        prob = self.churn_model.predict_proba(X_scaled)[0][1]
        return float(prob)
    
    def preprocess_customer(self, customer_data):
        """Preprocess single customer (API input)"""
        df = pd.DataFrame([customer_data])
        X = self.preprocess_customers(df)
        return X
    
    def get_segment_profiles(self, customers_df):
        """Analyze segment characteristics"""
        if self.segments is None:
            return []
        
        df = customers_df.copy()
        df['segment'] = self.segments
        
        profiles = []
        for i in range(len(np.unique(self.segments))):
            segment_data = df[df['segment'] == i]
            profile = {
                'segment_id': int(i),
                'size': len(segment_data),
                'percentage': f"{len(segment_data)/len(df)*100:.1f}%",
                'avg_tenure': float(segment_data.get('tenure', 0).mean()),
                'avg_charges': float(segment_data.get('MonthlyCharges', 0).mean())
            }
            profiles.append(profile)
        
        return profiles
    
    def get_pca_visualization(self):
        """2D PCA coordinates for frontend plotting"""
        if self.pca_result is not None:
            return [
                {
                    'segment': int(seg),
                    'x': float(x), 
                    'y': float(y)
                }
                for seg, (x, y) in enumerate(self.pca_result)
            ]
        return []

# Test standalone
if __name__ == "__main__":
    # Synthetic Telco data test
    np.random.seed(42)
    data = pd.DataFrame({
        'customerID': range(1000),
        'tenure': np.random.randint(1, 72, 1000),
        'MonthlyCharges': np.random.uniform(18, 118, 1000),
        'TotalCharges': np.random.uniform(100, 8000, 1000),
        'gender': np.random.choice(['Male', 'Female'], 1000),
        'SeniorCitizen': np.random.choice([0, 1], 1000),
        'Churn': np.random.choice([0, 1], 1000, p=[0.85, 0.15])
    })
    
    model = BIModel()
    model.train_segmentation(data)
    model.train_churn(data)
    
    print("✅ BI Model Test Complete!")
    print("Segments:", np.bincount(model.segments))
