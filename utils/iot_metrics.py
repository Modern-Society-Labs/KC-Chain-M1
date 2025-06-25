import csv
import os
import time
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

from utils.device_simulator import IoTDevice, DeviceType


LOG_DIR = Path(os.getenv("LOG_DIR", "logs"))
LOG_DIR.mkdir(parents=True, exist_ok=True)

IOT_METRICS_FILE = LOG_DIR / "iot_metrics.csv"
DEVICE_STATS_FILE = LOG_DIR / "device_stats.csv"

# Ensure IoT metrics CSV header
if not IOT_METRICS_FILE.exists():
    with open(IOT_METRICS_FILE, "w", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "timestamp",
                "device_id",
                "device_type",
                "operation",  # "registration" or "data_submission"
                "success",
                "latency_sec",
                "pipeline_stage",  # "lcore_api", "encryption", "on_chain"
                "tx_hash",
                "error_details",
                "data_size_bytes"
            ],
        )
        writer.writeheader()

# Ensure device stats CSV header
if not DEVICE_STATS_FILE.exists():
    with open(DEVICE_STATS_FILE, "w", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "timestamp",
                "device_id",
                "device_type",
                "location",
                "is_registered",
                "total_submissions",
                "failed_submissions",
                "success_rate",
                "last_submission_timestamp"
            ],
        )
        writer.writeheader()


def log_iot_metric(
    device: IoTDevice,
    operation: str,
    success: bool,
    latency_sec: float,
    pipeline_stage: str = "unknown",
    tx_hash: str = "",
    error_details: str = "",
    data_size_bytes: int = 0
):
    """Log IoT-specific metrics to CSV file
    
    Args:
        device: IoTDevice that performed the operation
        operation: Type of operation ("registration" or "data_submission")
        success: Whether the operation succeeded
        latency_sec: Time taken for the operation
        pipeline_stage: Which stage of pipeline ("lcore_api", "encryption", "on_chain")
        tx_hash: Transaction hash if applicable
        error_details: Error message if failed
        data_size_bytes: Size of data payload
    """
    with open(IOT_METRICS_FILE, "a", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "timestamp",
                "device_id",
                "device_type",
                "operation",
                "success",
                "latency_sec",
                "pipeline_stage",
                "tx_hash",
                "error_details",
                "data_size_bytes"
            ],
        )
        writer.writerow({
            "timestamp": datetime.now().isoformat(),
            "device_id": device.device_id,
            "device_type": device.device_type.value,
            "operation": operation,
            "success": success,
            "latency_sec": round(latency_sec, 3),
            "pipeline_stage": pipeline_stage,
            "tx_hash": tx_hash,
            "error_details": error_details,
            "data_size_bytes": data_size_bytes
        })


def log_device_stats(device: IoTDevice):
    """Log current device statistics
    
    Args:
        device: IoTDevice to log stats for
    """
    success_rate = 0.0
    if device.total_submissions > 0:
        success_count = device.total_submissions - device.failed_submissions
        success_rate = success_count / device.total_submissions
    
    with open(DEVICE_STATS_FILE, "a", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "timestamp",
                "device_id",
                "device_type",
                "location",
                "is_registered",
                "total_submissions",
                "failed_submissions",
                "success_rate",
                "last_submission_timestamp"
            ],
        )
        writer.writerow({
            "timestamp": datetime.now().isoformat(),
            "device_id": device.device_id,
            "device_type": device.device_type.value,
            "location": device.location,
            "is_registered": device.is_registered,
            "total_submissions": device.total_submissions,
            "failed_submissions": device.failed_submissions,
            "success_rate": round(success_rate, 3),
            "last_submission_timestamp": device.last_data_timestamp or ""
        })


class IoTMetricsTracker:
    """Track and analyze IoT pipeline performance metrics"""
    
    def __init__(self):
        self.start_time = time.time()
        self.total_operations = 0
        self.successful_operations = 0
        self.total_latency = 0.0
        self.registration_count = 0
        self.data_submission_count = 0
        self.on_chain_commitments = 0
        
        # Performance targets from METRICS.md
        self.target_daily_entries = 500
        self.target_success_rate = 0.95
        self.target_latency_sec = 30.0
    
    def record_operation(self, success: bool, latency_sec: float, operation_type: str):
        """Record an operation for metrics tracking"""
        self.total_operations += 1
        self.total_latency += latency_sec
        
        if success:
            self.successful_operations += 1
        
        if operation_type == "registration":
            self.registration_count += 1
        elif operation_type == "data_submission":
            self.data_submission_count += 1
    
    def record_on_chain_commitment(self, success: bool):
        """Record an on-chain commitment"""
        if success:
            self.on_chain_commitments += 1
    
    def get_current_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics"""
        runtime_hours = (time.time() - self.start_time) / 3600
        
        success_rate = 0.0
        if self.total_operations > 0:
            success_rate = self.successful_operations / self.total_operations
        
        avg_latency = 0.0
        if self.total_operations > 0:
            avg_latency = self.total_latency / self.total_operations
        
        # Extrapolate daily rate
        daily_rate = 0.0
        if runtime_hours > 0:
            daily_rate = (self.data_submission_count / runtime_hours) * 24
        
        return {
            "runtime_hours": round(runtime_hours, 2),
            "total_operations": self.total_operations,
            "successful_operations": self.successful_operations,
            "success_rate": round(success_rate, 3),
            "avg_latency_sec": round(avg_latency, 3),
            "registrations": self.registration_count,
            "data_submissions": self.data_submission_count,
            "on_chain_commitments": self.on_chain_commitments,
            "daily_submission_rate": round(daily_rate, 1),
            
            # Target comparisons
            "meets_success_target": success_rate >= self.target_success_rate,
            "meets_latency_target": avg_latency <= self.target_latency_sec,
            "meets_volume_target": daily_rate >= self.target_daily_entries,
            
            "targets": {
                "daily_entries": self.target_daily_entries,
                "success_rate": self.target_success_rate,
                "max_latency_sec": self.target_latency_sec
            }
        }
    
    def print_metrics_summary(self):
        """Print current metrics summary to console"""
        metrics = self.get_current_metrics()
        
        print("\n" + "="*60)
        print("IoT PIPELINE PERFORMANCE METRICS")
        print("="*60)
        print(f"Runtime: {metrics['runtime_hours']} hours")
        print(f"Total Operations: {metrics['total_operations']}")
        print(f"Success Rate: {metrics['success_rate']:.1%} (Target: {metrics['targets']['success_rate']:.1%}) {'✅' if metrics['meets_success_target'] else '❌'}")
        print(f"Avg Latency: {metrics['avg_latency_sec']:.2f}s (Target: <{metrics['targets']['max_latency_sec']}s) {'✅' if metrics['meets_latency_target'] else '❌'}")
        print(f"Daily Rate: {metrics['daily_submission_rate']:.1f} entries/day (Target: {metrics['targets']['daily_entries']}) {'✅' if metrics['meets_volume_target'] else '❌'}")
        print(f"Device Registrations: {metrics['registrations']}")
        print(f"Data Submissions: {metrics['data_submissions']}")
        print(f"On-Chain Commitments: {metrics['on_chain_commitments']}")
        print("="*60)


# Global metrics tracker instance
iot_metrics_tracker = IoTMetricsTracker() 