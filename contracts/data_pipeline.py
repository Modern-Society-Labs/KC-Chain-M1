import asyncio
import random
import logging
from datetime import datetime

from utils.device_simulator import device_simulator, IoTDevice
from utils.lcore_client import lcore_client
from utils.iot_metrics import log_iot_metric, iot_metrics_tracker, log_device_stats
from config.settings import LCORE_NODE_URL, IOT_REGISTRATION_RATE, IOT_DATA_SUBMISSION_RATE


async def register_iot_device():
    """Register a new IoT device through lcore-node MVP"""
    try:
        # Get a device that needs registration
        device = device_simulator.get_device_for_registration()
        if not device:
            logging.debug("No devices need registration")
            return
        
        logging.info(f"Registering IoT device: {device.device_id} ({device.device_type.value})")
        
        # Register device through lcore-node API
        success, response, latency = await lcore_client.register_device(device)
        
        if success:
            # Mark device as registered
            device_simulator.mark_device_registered(device.device_id)
            logging.info(f"Device {device.device_id} registered successfully in {latency:.2f}s")
            
            # Log metrics
            log_iot_metric(
                device=device,
                operation="registration",
                success=True,
                latency_sec=latency,
                pipeline_stage="lcore_api"
            )
            iot_metrics_tracker.record_operation(True, latency, "registration")
            
        else:
            error_details = response.get("error", "unknown_error")
            logging.warning(f"Device registration failed for {device.device_id}: {error_details}")
            
            # Log failure metrics
            log_iot_metric(
                device=device,
                operation="registration",
                success=False,
                latency_sec=latency,
                pipeline_stage="lcore_api",
                error_details=str(error_details)
            )
            iot_metrics_tracker.record_operation(False, latency, "registration")
    
    except Exception as e:
        logging.error(f"Exception in device registration: {e}")


async def submit_iot_sensor_data():
    """Submit real IoT sensor data through lcore-node dual-encryption pipeline"""
    try:
        # Get a registered device for data submission
        device = device_simulator.get_device_for_data_submission()
        if not device:
            logging.debug("No registered devices available for data submission")
            return
        
        # Generate realistic sensor data based on device type
        device_id, sensor_payload = device_simulator.generate_sensor_data(device)
        data_size = len(sensor_payload.encode('utf-8'))
        
        logging.info(f"Submitting sensor data from {device_id} ({device.device_type.value}) - {data_size} bytes")
        
        # Submit data through lcore-node API (dual encryption + on-chain commitment)
        success, response, latency = await lcore_client.submit_device_data(device, sensor_payload)
        
        # Update device statistics
        timestamp = datetime.now().isoformat()
        device_simulator.update_device_stats(device_id, success, timestamp)
        
        if success:
            # Extract transaction hash if available
            tx_hash = ""
            if "tx" in str(response):
                # Parse tx hash from response message like "Data submitted; tx 0x..."
                response_str = str(response)
                if "tx 0x" in response_str:
                    tx_hash = response_str.split("tx ")[1].split()[0]
            
            logging.info(f"IoT data submitted successfully from {device_id} in {latency:.2f}s")
            if tx_hash:
                logging.info(f"On-chain commitment: {tx_hash}")
                iot_metrics_tracker.record_on_chain_commitment(True)
            
            # Log success metrics
            log_iot_metric(
                device=device,
                operation="data_submission",
                success=True,
                latency_sec=latency,
                pipeline_stage="complete_pipeline",
                tx_hash=tx_hash,
                data_size_bytes=data_size
            )
            iot_metrics_tracker.record_operation(True, latency, "data_submission")
            
        else:
            error_details = response.get("error", "unknown_error")
            logging.warning(f"IoT data submission failed for {device_id}: {error_details}")
            
            # Log failure metrics
            log_iot_metric(
                device=device,
                operation="data_submission",
                success=False,
                latency_sec=latency,
                pipeline_stage="lcore_api",
                error_details=str(error_details),
                data_size_bytes=data_size
            )
            iot_metrics_tracker.record_operation(False, latency, "data_submission")
        
        # Periodically log device stats
        if random.random() < 0.1:  # 10% chance to log stats
            log_device_stats(device)
    
    except Exception as e:
        logging.error(f"Exception in IoT data submission: {e}")


async def monitor_iot_pipeline():
    """Monitor IoT pipeline health and performance"""
    try:
        # Check lcore-node health
        is_healthy = await lcore_client.health_check()
        
        if not is_healthy:
            logging.warning("lcore-node health check failed - may impact IoT operations")
        
        # Print metrics summary periodically
        if random.random() < 0.05:  # 5% chance to print summary
            iot_metrics_tracker.print_metrics_summary()
            
            # Print fleet statistics
            fleet_stats = device_simulator.get_fleet_stats()
            logging.info(f"IoT Fleet Status: {fleet_stats['registered_devices']}/{fleet_stats['total_devices']} devices registered, "
                        f"{fleet_stats['total_submissions']} total submissions, "
                        f"{fleet_stats['success_rate']:.1%} success rate")
    
    except Exception as e:
        logging.error(f"Exception in IoT pipeline monitoring: {e}")


# Main IoT simulation functions for the stress test orchestrator
async def simulate_iot_device_registration():
    """Main function for IoT device registration simulation"""
    while True:
        await register_iot_device()
        # Use configured registration rate
        await asyncio.sleep(1.0 / IOT_REGISTRATION_RATE)


async def simulate_iot_data_pipeline():
    """Main function for IoT data pipeline simulation"""
    while True:
        await submit_iot_sensor_data()
        await monitor_iot_pipeline()
        # Use configured data submission rate
        await asyncio.sleep(1.0 / IOT_DATA_SUBMISSION_RATE)


# Legacy function name for backward compatibility with main.py
async def send_sensor_data():
    """Legacy function name - now routes to IoT data pipeline"""
    await submit_iot_sensor_data() 