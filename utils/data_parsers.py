import csv
import json
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from pathlib import Path


@dataclass
class EVSensorData:
    """EV predictive maintenance sensor data structure"""
    timestamp: str
    battery_voltage: float
    battery_current: float
    battery_temperature: float
    motor_temperature: float
    speed: float
    acceleration: float
    regenerative_braking: float
    energy_consumption: float
    distance_traveled: float
    device_id: str = "EV_001"


@dataclass
class GreenhouseSensorData:
    """Greenhouse agricultural sensor data structure"""
    timestamp: str
    temperature: float
    humidity: float
    soil_moisture: float
    light_intensity: float
    co2_level: float
    ph_level: float
    nutrient_level: float
    plant_height: float
    leaf_count: int
    growth_rate: float
    device_id: str = "GH_001"


@dataclass
class SalesTransactionData:
    """Sales transaction data structure"""
    timestamp: str
    transaction_id: str
    product_code: str
    quantity: int
    unit_price: float
    total_amount: float
    customer_segment: str
    location: str
    device_id: str = "POS_001"


class DataParser:
    """Base class for parsing CSV data and generating IoT device payloads"""
    
    def __init__(self, data_dir: str = "smartcity-test/data"):
        self.data_dir = Path(data_dir)
        self.ev_data_cache: List[Dict[str, Any]] = []
        self.greenhouse_data_cache: List[Dict[str, Any]] = []
        self.sales_data_cache: List[Dict[str, Any]] = []
        self._load_data()
    
    def _load_data(self):
        """Load and cache all CSV data"""
        try:
            # Load EV data
            ev_file = self.data_dir / "EV_Predictive_Maintenance_Dataset_15min.csv"
            if ev_file.exists():
                with open(ev_file, 'r') as f:
                    reader = csv.DictReader(f)
                    self.ev_data_cache = list(reader)
            
            # Load greenhouse data
            greenhouse_file = self.data_dir / "Greenhouse Plant Growth Metrics.csv"
            if greenhouse_file.exists():
                with open(greenhouse_file, 'r') as f:
                    reader = csv.DictReader(f)
                    self.greenhouse_data_cache = list(reader)
            
            # Load sales data
            sales_file = self.data_dir / "sales_data_sample.csv"
            if sales_file.exists():
                with open(sales_file, 'r') as f:
                    reader = csv.DictReader(f)
                    self.sales_data_cache = list(reader)
                    
        except Exception as e:
            print(f"Warning: Could not load CSV data: {e}")
            # Generate fallback synthetic data
            self._generate_fallback_data()
    
    def _generate_fallback_data(self):
        """Generate synthetic data if CSV files are not available"""
        # Generate synthetic EV data
        for i in range(100):
            timestamp = (datetime.now() - timedelta(hours=i)).isoformat()
            self.ev_data_cache.append({
                'timestamp': timestamp,
                'battery_voltage': round(random.uniform(350, 400), 2),
                'battery_current': round(random.uniform(-50, 50), 2),
                'battery_temperature': round(random.uniform(20, 35), 2),
                'motor_temperature': round(random.uniform(40, 80), 2),
                'speed': round(random.uniform(0, 120), 2),
                'acceleration': round(random.uniform(-3, 3), 2),
                'energy_consumption': round(random.uniform(15, 25), 2)
            })
        
        # Generate synthetic greenhouse data
        for i in range(100):
            timestamp = (datetime.now() - timedelta(hours=i)).isoformat()
            self.greenhouse_data_cache.append({
                'timestamp': timestamp,
                'temperature': round(random.uniform(18, 28), 2),
                'humidity': round(random.uniform(40, 80), 2),
                'soil_moisture': round(random.uniform(30, 70), 2),
                'light_intensity': round(random.uniform(200, 800), 2),
                'co2_level': round(random.uniform(300, 500), 2),
                'ph_level': round(random.uniform(6.0, 7.5), 2)
            })
        
        # Generate synthetic sales data
        for i in range(100):
            timestamp = (datetime.now() - timedelta(hours=i)).isoformat()
            self.sales_data_cache.append({
                'timestamp': timestamp,
                'transaction_id': f"TXN_{random.randint(10000, 99999)}",
                'product_code': f"PROD_{random.randint(100, 999)}",
                'quantity': random.randint(1, 10),
                'unit_price': round(random.uniform(10, 500), 2),
                'total_amount': round(random.uniform(10, 2000), 2)
            })
    
    def get_random_ev_data(self, device_id: Optional[str] = None) -> EVSensorData:
        """Get random EV sensor data with realistic variance"""
        if not self.ev_data_cache:
            self._generate_fallback_data()
        
        base_data = random.choice(self.ev_data_cache)
        
        # Add realistic variance to the data
        return EVSensorData(
            timestamp=datetime.now().isoformat(),
            battery_voltage=float(base_data.get('battery_voltage', 380)) + random.uniform(-5, 5),
            battery_current=float(base_data.get('battery_current', 0)) + random.uniform(-2, 2),
            battery_temperature=float(base_data.get('battery_temperature', 25)) + random.uniform(-1, 1),
            motor_temperature=float(base_data.get('motor_temperature', 60)) + random.uniform(-3, 3),
            speed=max(0, float(base_data.get('speed', 50)) + random.uniform(-10, 10)),
            acceleration=float(base_data.get('acceleration', 0)) + random.uniform(-0.5, 0.5),
            regenerative_braking=random.uniform(0, 1),
            energy_consumption=float(base_data.get('energy_consumption', 20)) + random.uniform(-2, 2),
            distance_traveled=random.uniform(0, 100),
            device_id=device_id or f"EV_{random.randint(100, 999)}"
        )
    
    def get_random_greenhouse_data(self, device_id: Optional[str] = None) -> GreenhouseSensorData:
        """Get random greenhouse sensor data with realistic variance"""
        if not self.greenhouse_data_cache:
            self._generate_fallback_data()
        
        base_data = random.choice(self.greenhouse_data_cache)
        
        return GreenhouseSensorData(
            timestamp=datetime.now().isoformat(),
            temperature=float(base_data.get('temperature', 23)) + random.uniform(-1, 1),
            humidity=float(base_data.get('humidity', 60)) + random.uniform(-5, 5),
            soil_moisture=float(base_data.get('soil_moisture', 50)) + random.uniform(-3, 3),
            light_intensity=float(base_data.get('light_intensity', 500)) + random.uniform(-50, 50),
            co2_level=float(base_data.get('co2_level', 400)) + random.uniform(-20, 20),
            ph_level=float(base_data.get('ph_level', 6.8)) + random.uniform(-0.2, 0.2),
            nutrient_level=random.uniform(5, 15),
            plant_height=random.uniform(10, 50),
            leaf_count=random.randint(5, 25),
            growth_rate=random.uniform(0.1, 0.5),
            device_id=device_id or f"GH_{random.randint(100, 999)}"
        )
    
    def get_random_sales_data(self, device_id: Optional[str] = None) -> SalesTransactionData:
        """Get random sales transaction data with realistic variance"""
        if not self.sales_data_cache:
            self._generate_fallback_data()
        
        base_data = random.choice(self.sales_data_cache)
        
        quantity = random.randint(1, 5)
        unit_price = float(base_data.get('unit_price', 50)) + random.uniform(-10, 10)
        
        return SalesTransactionData(
            timestamp=datetime.now().isoformat(),
            transaction_id=f"TXN_{random.randint(100000, 999999)}",
            product_code=base_data.get('product_code', f"PROD_{random.randint(100, 999)}"),
            quantity=quantity,
            unit_price=max(1, unit_price),
            total_amount=quantity * max(1, unit_price),
            customer_segment=random.choice(['Small', 'Medium', 'Large']),
            location=base_data.get('location', 'Unknown'),
            device_id=device_id or f"POS_{random.randint(100, 999)}"
        )
    
    def to_iot_payload(self, sensor_data) -> str:
        """Convert sensor data to JSON payload for IoT submission"""
        if isinstance(sensor_data, (EVSensorData, GreenhouseSensorData, SalesTransactionData)):
            # Convert dataclass to dict, excluding device_id (handled separately)
            data_dict = {k: v for k, v in sensor_data.__dict__.items() if k != 'device_id'}
            return json.dumps(data_dict, sort_keys=True)
        else:
            return json.dumps(sensor_data, sort_keys=True)


# Global instance for easy access
data_parser = DataParser() 