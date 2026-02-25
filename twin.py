import pandas as pd
import numpy as np
from pathlib import Path
import joblib
from datetime import datetime, timedelta
from models.demand_model import DemandForecaster

class DigitalTwin:
    def __init__(self):
        self.inventory = None
        self.demand_forecast = None
        self.lead_time = 3  # Days
        self.safety_stock = 50
        
    def load_inventory(self, inventory_df):
        """Load SalesMind inventory data"""
        self.inventory = inventory_df.copy()
        
        # Standardize columns
        if 'stock_level' not in self.inventory.columns:
            self.inventory['stock_level'] = self.inventory.get('stock', 100)
        if 'reorder_point' not in self.inventory.columns:
            self.inventory['reorder_point'] = self.inventory['stock_level'] * 0.3
            
        print(f"✅ Loaded {len(self.inventory)} inventory items")
        return self.inventory
    
    def simulate_scenario(self, demand_multiplier=1.0, lead_time_days=3):
        """Run 'What-if' simulation"""
        if self.inventory is None:
            self._create_sample_inventory()
        
        # Get demand forecast
        forecaster = DemandForecaster()
        forecast = forecaster.predict(days_ahead=30)
        daily_demand = np.mean([f['yhat'] for f in forecast])
        
        # Simulate inventory over 30 days
        simulation_days = 30
        results = []
        
        current_inventory = self.inventory.copy()
        
        for day in range(simulation_days):
            date = (datetime.now() + timedelta(days=day)).strftime('%Y-%m-%d')
            
            # Daily demand (with scenario multiplier)
            day_demand = daily_demand * demand_multiplier * np.random.uniform(0.8, 1.2)
            
            # Update each product
            for idx, product in current_inventory.iterrows():
                stock = product['stock_level']
                
                # Demand impact
                product_demand = day_demand * (1/len(current_inventory))  # Even distribution
                new_stock = max(0, stock - product_demand)
                
                # Replenishment (lead time delay)
                if stock < product['reorder_point'] and day % lead_time_days == 0:
                    new_stock += 200  # Order quantity
                
                current_inventory.at[idx, 'stock_level'] = new_stock
                
                # Track critical items
                status = 'OK' if new_stock > self.safety_stock else 'LOW'
                if new_stock == 0:
                    status = 'STOCKOUT'
                
                results.append({
                    'day': day + 1,
                    'date': date,
                    'product_id': product.get('product_id', idx),
                    'demand': float(product_demand),
                    'stock_level': float(new_stock),
                    'status': status,
                    'reorder_needed': stock < product['reorder_point']
                })
        
        return pd.DataFrame(results)
    
    def get_kpi_summary(self):
        """Current inventory KPIs"""
        if self.inventory is None:
            self._create_sample_inventory()
        
        total_value = self.inventory['stock_level'].sum()
        low_stock = len(self.inventory[self.inventory['stock_level'] < self.safety_stock])
        stockouts = len(self.inventory[self.inventory['stock_level'] == 0])
        
        return {
            'total_items': len(self.inventory),
            'total_stock_value': float(total_value),
            'low_stock_items': int(low_stock),
            'stockouts': int(stockouts),
            'fill_rate': 95.5,  # Target
            'inventory_turnover': 4.2  # Annual
        }
    
    def optimize_reorder(self):
        """Calculate optimal reorder points"""
        if self.inventory is None:
            self._create_sample_inventory()
        
        forecaster = DemandForecaster()
        forecast = forecaster.predict(7)  # Weekly demand
        weekly_demand = np.mean([f['yhat'] for f in forecast])
        
        self.inventory['optimal_reorder'] = weekly_demand * self.lead_time + self.safety_stock
        self.inventory['order_qty'] = self.inventory['optimal_reorder'] * 1.5
        
        return self.inventory[['product_id', 'optimal_reorder', 'order_qty']].to_dict('records')
    
    def _create_sample_inventory(self):
        """Synthetic SalesMind inventory for demo"""
        products = [f'PROD_{i:03d}' for i in range(50)]
        self.inventory = pd.DataFrame({
            'product_id': products,
            'category': np.random.choice(['Electronics', 'Clothing', 'Food'], 50),
            'stock_level': np.random.randint(10, 500, 50),
            'reorder_point': np.random.randint(20, 100, 50),
            'unit_cost': np.random.uniform(10, 100, 50)
        })

# API Integration Functions
def run_simulation(scenario_params):
    """For Flask API - /api/twin/simulate"""
    twin = DigitalTwin()
    
    # Load real data if available
    data_path = Path('data')
    inventory_files = list(data_path.glob('*inventory*.csv'))
    if inventory_files:
        twin.load_inventory(pd.read_csv(inventory_files[0]))
    
    demand_mult = scenario_params.get('demand_increase', 0) / 100
    result = twin.simulate_scenario(1 + demand_mult)
    
    return {
        'summary': twin.get_kpi_summary(),
        'daily_results': result.tail(7).to_dict('records'),
        'recommendations': twin.optimize_reorder()
    }

if __name__ == "__main__":
    # Test twin simulation
    twin = DigitalTwin()
    twin.load_inventory(pd.DataFrame())  # Uses sample data
    
    scenario = run_simulation({'demand_increase': 20})
    print("✅ Digital Twin Test:")
    print(f"Stockouts: {scenario['summary']['stockouts']}")
    print("Recommendations:", scenario['recommendations'][:3])
