#!/usr/bin/env python3
"""
KC-Chain Stress Test Wallet Setup

This script initializes the wallet management system and provides
funding instructions for the enhanced stress test simulator.
"""

import asyncio
from utils.wallet_manager import wallet_manager
from utils.funding_helper import funding_helper


def main():
    print("🚀 KC-Chain Stress Test Wallet Setup")
    print("=" * 50)
    
    # Initialize wallet manager (creates wallets if needed)
    print("Initializing wallet management system...")
    
    # Print wallet summary
    wallet_manager.print_wallet_summary()
    
    # Update balances from blockchain
    print("\nChecking current wallet balances...")
    wallet_manager.update_all_balances()
    
    # Print funding instructions
    funding_helper.print_funding_instructions(amount_per_wallet_eth=0.08)
    
    print("\n📁 Files created:")
    print("  wallets.csv - Wallet addresses, private keys, and metadata")
    print("  logs/tx_metrics.csv - Transaction logs")
    print("  logs/iot_metrics.csv - IoT pipeline metrics")
    
    print("\n🔄 Next steps:")
    print("1. Fund the main funder wallet with your 1 ETH")
    print("2. Run the auto-funding: python -c \"import asyncio; from utils.funding_helper import funding_helper; asyncio.run(funding_helper.fund_all_from_funder())\"")
    print("3. Start the enhanced stress test: python main.py")


if __name__ == "__main__":
    main() 