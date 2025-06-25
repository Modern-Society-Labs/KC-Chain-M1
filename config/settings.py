import os
from pathlib import Path
from dotenv import load_dotenv
from web3 import Web3, HTTPProvider
from web3.middleware import geth_poa_middleware

# Load environment variables from .env file at project root if present
load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / ".env")

# ----------------------------
# Chain / RPC Configuration
# ----------------------------

RPC_HTTP_URL = os.getenv(
    "RPC_HTTP_URL",
    "https://your.rpc.url",  # placeholder – must be set in .env or Railway env
)
RPC_WS_URL = os.getenv(
    "RPC_WS_URL",
    "wss://your.ws.url",  # placeholder – must be set in .env or Railway env
)
CHAIN_ID = int(os.getenv("CHAIN_ID", 1205614515668104))

# ----------------------------
# lcore-node MVP Configuration
# ----------------------------

LCORE_NODE_URL = os.getenv("LCORE_NODE_URL", "http://127.0.0.1:3000")
LCORE_NODE_TIMEOUT = int(os.getenv("LCORE_NODE_TIMEOUT", 30))
LCORE_NODE_MAX_RETRIES = int(os.getenv("LCORE_NODE_MAX_RETRIES", 3))

# MVP IoT Processor Contract Address (deployed on KC-Chain)
MVP_IOT_PROCESSOR_ADDRESS = os.getenv(
    "MVP_IOT_PROCESSOR_ADDRESS",
    "0xYourContractAddress"  # placeholder – must be set in env
)

# ----------------------------
# Account Configuration
# ----------------------------

# WARNING: Never commit real private keys. Use dummy keys or environment variables.
PRIVATE_KEYS = [
    os.getenv("PRIVATE_KEY", "0x0123456789012345678901234567890123456789012345678901234567890123"),
    os.getenv("PRIVATE_KEY_2", "0x1123456789012345678901234567890123456789012345678901234567890123"),
    os.getenv("PRIVATE_KEY_3", "0x2123456789012345678901234567890123456789012345678901234567890123"),
]

# ----------------------------
# Gas Configuration
# ----------------------------

DEFAULT_GAS_LIMIT = int(os.getenv("DEFAULT_GAS_LIMIT", 3000000))  # High limit for Stylus contracts
FIXED_GAS_PRICE_WEI = int(os.getenv("FIXED_GAS_PRICE_WEI", 0))  # 0 = use network gas price

# ----------------------------
# IoT Simulation Configuration
# ----------------------------

# Number of IoT devices to simulate
IOT_DEVICE_COUNT = int(os.getenv("IOT_DEVICE_COUNT", 15))

# Data submission rates (per second)
IOT_REGISTRATION_RATE = float(os.getenv("IOT_REGISTRATION_RATE", 0.1))  # 1 registration per 10 seconds
IOT_DATA_SUBMISSION_RATE = float(os.getenv("IOT_DATA_SUBMISSION_RATE", 0.2))  # 1 submission per 5 seconds

# Performance targets
TARGET_DAILY_ENTRIES = int(os.getenv("TARGET_DAILY_ENTRIES", 500))
TARGET_SUCCESS_RATE = float(os.getenv("TARGET_SUCCESS_RATE", 0.95))
TARGET_MAX_LATENCY_SEC = float(os.getenv("TARGET_MAX_LATENCY_SEC", 30.0))

# ----------------------------
# Web3 Setup
# ----------------------------

web3_http = Web3(HTTPProvider(RPC_HTTP_URL))
web3_http.middleware_onion.inject(geth_poa_middleware, layer=0)

def get_account(index: int = 0):
    """Get account from private key by index"""
    if index >= len(PRIVATE_KEYS):
        index = 0
    return web3_http.eth.account.from_key(PRIVATE_KEYS[index])

# ----------------------------
# Funding Defaults
# ----------------------------

# Default ETH amount to drip into each managed wallet when using FundingHelper
DEFAULT_FUNDING_AMOUNT_ETH = float(os.getenv("DEFAULT_FUNDING_AMOUNT_ETH", 0.005)) 