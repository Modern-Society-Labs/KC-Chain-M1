import asyncio
import aiohttp
import json
import time
from typing import Dict, Any, Optional, Tuple
from datetime import datetime
import logging

from utils.device_simulator import IoTDevice
from config.settings import LCORE_NODE_URL, LCORE_NODE_TIMEOUT, LCORE_NODE_MAX_RETRIES


class LcoreClientError(Exception):
    """Raised when lcore-node API calls fail"""
    pass


class LcoreClient:
    """HTTP client for lcore-node MVP API endpoints"""
    
    def __init__(self, base_url: str = "http://127.0.0.1:3000", timeout: int = 30, max_retries: int = 3):
        self.base_url = base_url.rstrip('/')
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.max_retries = max_retries
        self.session: Optional[aiohttp.ClientSession] = None
        
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create HTTP session"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(timeout=self.timeout)
        return self.session
    
    async def close(self):
        """Close the HTTP session"""
        if self.session and not self.session.closed:
            await self.session.close()
    
    async def _make_request(self, method: str, endpoint: str, data: Optional[Dict[str, Any]] = None) -> Tuple[bool, Dict[str, Any]]:
        """Make HTTP request with retry logic
        
        Returns:
            Tuple of (success: bool, response_data: dict)
        """
        url = f"{self.base_url}{endpoint}"
        
        for attempt in range(self.max_retries):
            try:
                session = await self._get_session()
                
                if method.upper() == "POST":
                    async with session.post(url, json=data, headers={'Content-Type': 'application/json'}) as response:
                        response_data = await response.json()
                        
                        if 200 <= response.status < 300:
                            return True, response_data
                        else:
                            logging.warning(f"lcore-node API error: {response.status} - {response_data}")
                            if attempt == self.max_retries - 1:
                                return False, {"error": f"HTTP {response.status}", "details": response_data}
                
                elif method.upper() == "GET":
                    async with session.get(url) as response:
                        response_data = await response.json()
                        
                        if 200 <= response.status < 300:
                            return True, response_data
                        else:
                            logging.warning(f"lcore-node API error: {response.status} - {response_data}")
                            if attempt == self.max_retries - 1:
                                return False, {"error": f"HTTP {response.status}", "details": response_data}
                
            except aiohttp.ClientError as e:
                logging.warning(f"lcore-node connection error (attempt {attempt + 1}): {e}")
                if attempt == self.max_retries - 1:
                    return False, {"error": "connection_failed", "details": str(e)}
                
                # Exponential backoff
                await asyncio.sleep(2 ** attempt)
            
            except Exception as e:
                logging.error(f"Unexpected error in lcore-node request: {e}")
                return False, {"error": "unexpected_error", "details": str(e)}
        
        return False, {"error": "max_retries_exceeded"}
    
    async def register_device(self, device: IoTDevice) -> Tuple[bool, Dict[str, Any], float]:
        """Register a device with lcore-node
        
        Args:
            device: IoTDevice to register
            
        Returns:
            Tuple of (success: bool, response_data: dict, latency: float)
        """
        start_time = time.time()
        
        payload = {
            "device_id": device.device_id,
            "public_key": device.public_key
        }
        
        success, response = await self._make_request("POST", "/device/register", payload)
        latency = time.time() - start_time
        
        return success, response, latency
    
    async def submit_device_data(self, device: IoTDevice, sensor_data: str) -> Tuple[bool, Dict[str, Any], float]:
        """Submit IoT sensor data through lcore-node
        
        Args:
            device: IoTDevice submitting data
            sensor_data: JSON string of sensor data
            
        Returns:
            Tuple of (success: bool, response_data: dict, latency: float)
        """
        start_time = time.time()
        
        # Create timestamp for this submission
        timestamp = int(time.time())
        
        payload = {
            "device_id": device.device_id,
            "data": sensor_data,
            "timestamp": timestamp
        }
        
        success, response = await self._make_request("POST", "/device/data", payload)
        latency = time.time() - start_time
        
        return success, response, latency
    
    async def get_status(self) -> Tuple[bool, Dict[str, Any], float]:
        """Get lcore-node health status
        
        Returns:
            Tuple of (success: bool, response_data: dict, latency: float)
        """
        start_time = time.time()
        
        success, response = await self._make_request("GET", "/status")
        latency = time.time() - start_time
        
        return success, response, latency
    
    async def health_check(self) -> bool:
        """Simple health check for lcore-node availability
        
        Returns:
            bool: True if lcore-node is responsive
        """
        try:
            success, _, _ = await self.get_status()
            return success
        except Exception:
            return False


# Global lcore client instance
lcore_client = LcoreClient(
    base_url=LCORE_NODE_URL,
    timeout=LCORE_NODE_TIMEOUT,
    max_retries=LCORE_NODE_MAX_RETRIES,
) 