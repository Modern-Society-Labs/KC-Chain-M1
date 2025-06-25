import asyncio
import logging
import threading

from contracts import payment_app, merchant_app, lending_app, data_pipeline
from utils.iot_metrics import iot_metrics_tracker
from utils.lcore_client import lcore_client
from config.settings import LCORE_NODE_URL, IOT_DEVICE_COUNT
from utils.wallet_manager import wallet_manager
from utils.funding_helper import FundingHelper
from utils.metrics_logger import print_dapp_summary  # imported here to expose summary in status task
from server import run as run_http_server

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s: %(message)s")

# Ensure at least 18 payment-user wallets and fund them once
wallet_manager.ensure_min_user_wallets(18)
_funding_helper = FundingHelper()

async def simulate_payment_activity():
    """Standard payment transactions for blockchain stress testing"""
    while True:
        await payment_app.simulate_transaction()
        await asyncio.sleep(0.5)  # ~2 tx/s


async def simulate_merchant_activity():
    """Merchant payment settlements for blockchain stress testing"""
    while True:
        await merchant_app.settle_payment()
        await asyncio.sleep(1)  # 1 tx/s


async def simulate_lending_activity():
    """Loan origination and repayment operations for blockchain stress testing"""
    while True:
        await lending_app.originate_loan()
        await lending_app.make_repayment()
        await asyncio.sleep(2)


async def simulate_iot_registration_activity():
    """IoT device registration through lcore-node MVP"""
    while True:
        await data_pipeline.register_iot_device()
        await asyncio.sleep(10)  # Register devices every 10 seconds


async def simulate_iot_data_activity():
    """Real IoT data submission through dual-encryption pipeline"""
    while True:
        await data_pipeline.submit_iot_sensor_data()
        await data_pipeline.monitor_iot_pipeline()
        await asyncio.sleep(5)  # Submit data every 5 seconds


async def print_status_summary():
    """Periodic status summary for all stress test components"""
    while True:
        await asyncio.sleep(60)  # Print summary every minute
        try:
            # Print IoT metrics summary
            iot_metrics_tracker.print_metrics_summary()
            
            # Print regular dApp transactions summary
            print_dapp_summary()
            
            # Check lcore-node connectivity
            is_healthy = await lcore_client.health_check()
            health_status = "✅ HEALTHY" if is_healthy else "❌ UNAVAILABLE"
            logging.info(f"lcore-node Status: {health_status} ({LCORE_NODE_URL})")
            
        except Exception as e:
            logging.error(f"Error in status summary: {e}")


async def cleanup_resources():
    """Cleanup resources on shutdown"""
    try:
        await lcore_client.close()
        logging.info("Resources cleaned up successfully")
    except Exception as e:
        logging.error(f"Error during cleanup: {e}")


async def main():
    logging.info("Starting KC-Chain Enhanced Stress Test Simulator with IoT Data Pipeline")
    logging.info(f"IoT Configuration: {IOT_DEVICE_COUNT} devices, lcore-node at {LCORE_NODE_URL}")
    
    try:
        # Check lcore-node availability before starting
        is_healthy = await lcore_client.health_check()
        if is_healthy:
            logging.info("✅ lcore-node is available - IoT pipeline enabled")
        else:
            logging.warning("⚠️  lcore-node is not available - IoT operations may fail")
        
        # One-time funding of all wallets (if needed)
        try:
            await _funding_helper.fund_all_from_funder()
            logging.info("Wallets funded successfully")
        except Exception as e:
            logging.error(f"Wallet funding failed: {e}")
        
        # Launch HTTP health & metrics server in background BEFORE async tasks start
        threading.Thread(target=run_http_server, daemon=True).start()
        logging.info("Health & metrics endpoint started on /health and /metrics")
        
        # Start all stress test components concurrently
        await asyncio.gather(
            # Traditional blockchain stress testing
            simulate_payment_activity(),
            simulate_merchant_activity(),
            simulate_lending_activity(),
            
            # Enhanced IoT data pipeline
            simulate_iot_registration_activity(),
            simulate_iot_data_activity(),
            
            # Monitoring and status
            print_status_summary(),
        )

    except KeyboardInterrupt:
        logging.info("Received shutdown signal...")
    except Exception as e:
        logging.error(f"Unexpected error in main: {e}")
    finally:
        await cleanup_resources()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Stress test simulator stopped.")
    except Exception as e:
        logging.error(f"Fatal error: {e}") 