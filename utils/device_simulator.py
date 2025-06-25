import random
import secrets
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from utils.data_parsers import data_parser, EVSensorData, GreenhouseSensorData, SalesTransactionData


class DeviceType(Enum):
    """Types of IoT devices supported"""
    EV_SENSOR = "ev_sensor"
    GREENHOUSE = "greenhouse"
    POS_TERMINAL = "pos_terminal"


@dataclass
class IoTDevice:
    """Represents an IoT device with unique identity"""
    device_id: str
    device_type: DeviceType
    location: str
    public_key: str
    is_registered: bool = False
    last_data_timestamp: Optional[str] = None
    total_submissions: int = 0
    failed_submissions: int = 0


class DeviceSimulator:
    """Manages a fleet of simulated IoT devices"""
    
    def __init__(self, num_devices: int = 10):
        self.devices: Dict[str, IoTDevice] = {}
        self.device_pool: List[str] = []
        self._initialize_devices(num_devices)
    
    def _initialize_devices(self, num_devices: int):
        """Initialize a fleet of diverse IoT devices"""
        device_types = [
            (DeviceType.EV_SENSOR, "EV", ["Downtown", "Suburb", "Highway", "Parking_Lot"]),
            (DeviceType.GREENHOUSE, "GH", ["Farm_A", "Farm_B", "Research_Lab", "Urban_Garden"]),
            (DeviceType.POS_TERMINAL, "POS", ["Store_1", "Store_2", "Mall", "Airport"])
        ]
        
        devices_per_type = max(1, num_devices // len(device_types))
        
        for device_type, prefix, locations in device_types:
            for i in range(devices_per_type):
                device_id = f"{prefix}_{random.randint(1000, 9999)}"
                location = random.choice(locations)
                
                device = IoTDevice(
                    device_id=device_id,
                    device_type=device_type,
                    location=location,
                    public_key=secrets.token_hex(32)
                )
                
                self.devices[device_id] = device
                self.device_pool.append(device_id)
        
        # Fill remaining slots with random devices
        while len(self.devices) < num_devices:
            device_type, prefix, locations = random.choice(device_types)
            device_id = f"{prefix}_{random.randint(1000, 9999)}"
            
            if device_id not in self.devices:
                device = IoTDevice(
                    device_id=device_id,
                    device_type=device_type,
                    location=random.choice(locations),
                    public_key=secrets.token_hex(32)
                )
                self.devices[device_id] = device
                self.device_pool.append(device_id)
    
    def get_random_device(self) -> IoTDevice:
        """Get a random device from the fleet"""
        device_id = random.choice(self.device_pool)
        return self.devices[device_id]
    
    def get_device_by_id(self, device_id: str) -> Optional[IoTDevice]:
        """Get a specific device by ID"""
        return self.devices.get(device_id)
    
    def get_unregistered_devices(self) -> List[IoTDevice]:
        """Get list of devices that haven't been registered yet"""
        return [device for device in self.devices.values() if not device.is_registered]
    
    def get_registered_devices(self) -> List[IoTDevice]:
        """Get list of registered devices"""
        return [device for device in self.devices.values() if device.is_registered]
    
    def mark_device_registered(self, device_id: str) -> bool:
        """Mark a device as registered"""
        if device_id in self.devices:
            self.devices[device_id].is_registered = True
            return True
        return False
    
    def generate_sensor_data(self, device: IoTDevice) -> Tuple[str, str]:
        """Generate sensor data for a specific device
        
        Returns:
            Tuple of (device_id, json_payload)
        """
        if device.device_type == DeviceType.EV_SENSOR:
            sensor_data = data_parser.get_random_ev_data(device.device_id)
        elif device.device_type == DeviceType.GREENHOUSE:
            sensor_data = data_parser.get_random_greenhouse_data(device.device_id)
        elif device.device_type == DeviceType.POS_TERMINAL:
            sensor_data = data_parser.get_random_sales_data(device.device_id)
        else:
            # Fallback to EV data
            sensor_data = data_parser.get_random_ev_data(device.device_id)
        
        payload = data_parser.to_iot_payload(sensor_data)
        return device.device_id, payload
    
    def update_device_stats(self, device_id: str, success: bool, timestamp: str):
        """Update device statistics after data submission"""
        if device_id in self.devices:
            device = self.devices[device_id]
            device.total_submissions += 1
            device.last_data_timestamp = timestamp
            
            if not success:
                device.failed_submissions += 1
    
    def get_device_success_rate(self, device_id: str) -> float:
        """Get success rate for a specific device"""
        device = self.devices.get(device_id)
        if not device or device.total_submissions == 0:
            return 0.0
        
        success_count = device.total_submissions - device.failed_submissions
        return success_count / device.total_submissions
    
    def get_fleet_stats(self) -> Dict[str, any]:
        """Get overall fleet statistics"""
        total_devices = len(self.devices)
        registered_devices = len(self.get_registered_devices())
        total_submissions = sum(device.total_submissions for device in self.devices.values())
        total_failures = sum(device.failed_submissions for device in self.devices.values())
        
        success_rate = 0.0
        if total_submissions > 0:
            success_rate = (total_submissions - total_failures) / total_submissions
        
        device_type_counts = {}
        for device in self.devices.values():
            device_type = device.device_type.value
            device_type_counts[device_type] = device_type_counts.get(device_type, 0) + 1
        
        return {
            "total_devices": total_devices,
            "registered_devices": registered_devices,
            "registration_rate": registered_devices / total_devices if total_devices > 0 else 0,
            "total_submissions": total_submissions,
            "total_failures": total_failures,
            "success_rate": success_rate,
            "device_types": device_type_counts
        }
    
    def get_device_for_registration(self) -> Optional[IoTDevice]:
        """Get a device that needs registration"""
        unregistered = self.get_unregistered_devices()
        return random.choice(unregistered) if unregistered else None
    
    def get_device_for_data_submission(self) -> Optional[IoTDevice]:
        """Get a registered device for data submission"""
        registered = self.get_registered_devices()
        return random.choice(registered) if registered else None


# Global device simulator instance
device_simulator = DeviceSimulator(num_devices=15) 