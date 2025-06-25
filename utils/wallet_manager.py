import csv
import os
import secrets
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
from datetime import datetime

from web3 import Web3
from config.settings import web3_http as w3, CHAIN_ID


class WalletType(Enum):
    """Types of wallets for different transaction roles"""
    PAYMENT_USER = "payment_user"          # End users making payments
    MERCHANT = "merchant"                  # Businesses receiving payments
    LENDER = "lender"                     # Lending protocol operators
    BORROWER = "borrower"                 # Loan recipients
    IOT_DEVICE = "iot_device"             # IoT devices submitting data
    IOT_OPERATOR = "iot_operator"         # IoT network operators
    FUNDER = "funder"                     # Main wallet that funds others


@dataclass
class ManagedWallet:
    """Represents a managed wallet with metadata"""
    address: str
    private_key: str
    wallet_type: WalletType
    label: str
    balance_eth: float = 0.0
    nonce: int = 0
    total_transactions: int = 0
    total_gas_used: int = 0
    created_at: str = ""


class WalletManager:
    """Manages multiple wallets for different transaction types"""
    
    def __init__(self, wallets_csv_file: str = "logs/wallets.csv"):
        self.wallets_csv_file = Path(wallets_csv_file)
        self.wallets: Dict[str, ManagedWallet] = {}
        self.wallets_by_type: Dict[WalletType, List[ManagedWallet]] = {}
        
        # Ensure logs directory exists
        self.wallets_csv_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize CSV file
        self._init_csv()
        
        # Load existing wallets or create new ones
        self._load_or_create_wallets()
    
    def _init_csv(self):
        """Initialize the wallets CSV file with headers"""
        if not self.wallets_csv_file.exists():
            with open(self.wallets_csv_file, "w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=[
                    "address",
                    "private_key", 
                    "wallet_type",
                    "label",
                    "balance_eth",
                    "nonce",
                    "total_transactions",
                    "total_gas_used",
                    "created_at"
                ])
                writer.writeheader()
    
    def _generate_wallet(self, wallet_type: WalletType, label: str) -> ManagedWallet:
        """Generate a new wallet with the specified type and label"""
        # Generate random private key
        private_key = "0x" + secrets.token_hex(32)
        account = w3.eth.account.from_key(private_key)
        
        wallet = ManagedWallet(
            address=account.address,
            private_key=private_key,
            wallet_type=wallet_type,
            label=label,
            created_at=datetime.now().isoformat()
        )
        
        return wallet
    
    def _load_or_create_wallets(self):
        """Load existing wallets from CSV or create a new wallet set"""
        try:
            # Try to load existing wallets
            with open(self.wallets_csv_file, "r") as f:
                reader = csv.DictReader(f)
                existing_wallets = list(reader)
            
            if existing_wallets:
                print(f"Loading {len(existing_wallets)} existing wallets...")
                for row in existing_wallets:
                    wallet = ManagedWallet(
                        address=row["address"],
                        private_key=row["private_key"],
                        wallet_type=WalletType(row["wallet_type"]),
                        label=row["label"],
                        balance_eth=float(row["balance_eth"]),
                        nonce=int(row["nonce"]),
                        total_transactions=int(row["total_transactions"]),
                        total_gas_used=int(row["total_gas_used"]),
                        created_at=row["created_at"]
                    )
                    self._add_wallet_to_collections(wallet)
            else:
                print("No existing wallets found. Creating new wallet set...")
                self._create_default_wallet_set()
                
        except Exception as e:
            print(f"Error loading wallets: {e}. Creating new wallet set...")
            self._create_default_wallet_set()
    
    def _create_default_wallet_set(self):
        """Create a default set of wallets for different transaction types"""
        wallet_configs = [
            # Main funder wallet
            (WalletType.FUNDER, "main_funder"),
            
            # Payment users (3 wallets)
            (WalletType.PAYMENT_USER, "user_alice"),
            (WalletType.PAYMENT_USER, "user_bob"), 
            (WalletType.PAYMENT_USER, "user_charlie"),
            
            # Merchants (2 wallets)
            (WalletType.MERCHANT, "merchant_store_a"),
            (WalletType.MERCHANT, "merchant_store_b"),
            
            # Lending protocol (2 wallets)
            (WalletType.LENDER, "lending_protocol"),
            (WalletType.BORROWER, "borrower_alice"),
            
            # IoT ecosystem (3 wallets) 
            (WalletType.IOT_DEVICE, "iot_device_pool"),
            (WalletType.IOT_OPERATOR, "iot_operator_a"),
            (WalletType.IOT_OPERATOR, "iot_operator_b"),
        ]
        
        for wallet_type, label in wallet_configs:
            wallet = self._generate_wallet(wallet_type, label)
            self._add_wallet_to_collections(wallet)
        
        # Save all wallets to CSV
        self._save_all_wallets()
        print(f"Created {len(self.wallets)} new wallets")
    
    def _add_wallet_to_collections(self, wallet: ManagedWallet):
        """Add wallet to internal collections"""
        self.wallets[wallet.address] = wallet
        
        if wallet.wallet_type not in self.wallets_by_type:
            self.wallets_by_type[wallet.wallet_type] = []
        self.wallets_by_type[wallet.wallet_type].append(wallet)
    
    def _save_all_wallets(self):
        """Save all wallets to CSV file"""
        with open(self.wallets_csv_file, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=[
                "address",
                "private_key",
                "wallet_type", 
                "label",
                "balance_eth",
                "nonce",
                "total_transactions",
                "total_gas_used",
                "created_at"
            ])
            writer.writeheader()
            
            for wallet in self.wallets.values():
                writer.writerow({
                    "address": wallet.address,
                    "private_key": wallet.private_key,
                    "wallet_type": wallet.wallet_type.value,
                    "label": wallet.label,
                    "balance_eth": wallet.balance_eth,
                    "nonce": wallet.nonce,
                    "total_transactions": wallet.total_transactions,
                    "total_gas_used": wallet.total_gas_used,
                    "created_at": wallet.created_at
                })
    
    def get_wallets_by_type(self, wallet_type: WalletType) -> List[ManagedWallet]:
        """Get all wallets of a specific type"""
        return self.wallets_by_type.get(wallet_type, [])
    
    def get_random_wallet_by_type(self, wallet_type: WalletType) -> Optional[ManagedWallet]:
        """Get a random wallet of the specified type"""
        wallets = self.get_wallets_by_type(wallet_type)
        if wallets:
            import random
            return random.choice(wallets)
        return None
    
    def get_funder_wallet(self) -> Optional[ManagedWallet]:
        """Get the main funder wallet"""
        funder_wallets = self.get_wallets_by_type(WalletType.FUNDER)
        return funder_wallets[0] if funder_wallets else None
    
    def update_wallet_balance(self, address: str):
        """Update wallet balance from blockchain"""
        if address in self.wallets:
            try:
                balance_wei = w3.eth.get_balance(address)
                balance_eth = w3.from_wei(balance_wei, 'ether')
                self.wallets[address].balance_eth = float(balance_eth)
            except Exception as e:
                print(f"Error updating balance for {address}: {e}")
    
    def update_all_balances(self):
        """Update balances for all wallets"""
        print("Updating all wallet balances...")
        for address in self.wallets.keys():
            self.update_wallet_balance(address)
        self._save_all_wallets()
    
    def record_transaction(self, address: str, gas_used: int):
        """Record a transaction for the specified wallet"""
        if address in self.wallets:
            wallet = self.wallets[address]
            wallet.total_transactions += 1
            wallet.total_gas_used += gas_used
            wallet.nonce += 1
    
    def get_funding_summary(self) -> Dict[str, any]:
        """Get summary of funding needed for all wallets"""
        total_wallets = len(self.wallets)
        funded_wallets = sum(1 for w in self.wallets.values() if w.balance_eth > 0)
        total_balance = sum(w.balance_eth for w in self.wallets.values())
        
        wallets_by_type = {}
        for wallet_type in WalletType:
            wallets = self.get_wallets_by_type(wallet_type)
            if wallets:
                wallets_by_type[wallet_type.value] = {
                    "count": len(wallets),
                    "addresses": [w.address for w in wallets],
                    "total_balance": sum(w.balance_eth for w in wallets)
                }
        
        return {
            "total_wallets": total_wallets,
            "funded_wallets": funded_wallets,
            "total_balance_eth": round(total_balance, 6),
            "wallets_by_type": wallets_by_type,
            "funder_address": self.get_funder_wallet().address if self.get_funder_wallet() else None
        }
    
    def print_wallet_summary(self):
        """Print a summary of all wallets"""
        summary = self.get_funding_summary()
        
        print("\n" + "="*60)
        print("WALLET MANAGEMENT SUMMARY")
        print("="*60)
        print(f"Total Wallets: {summary['total_wallets']}")
        print(f"Funded Wallets: {summary['funded_wallets']}")
        print(f"Total Balance: {summary['total_balance_eth']} ETH")
        
        if summary['funder_address']:
            print(f"Main Funder: {summary['funder_address']}")
        
        print("\nWallets by Type:")
        for wallet_type, info in summary['wallets_by_type'].items():
            print(f"  {wallet_type}: {info['count']} wallets, {info['total_balance']:.6f} ETH")
            for addr in info['addresses']:
                print(f"    {addr}")
        print("="*60)

    def ensure_min_user_wallets(self, min_count: int = 18):
        """Ensure at least `min_count` PAYMENT_USER wallets exist."""
        current = len(self.wallets_by_type.get(WalletType.PAYMENT_USER, []))
        if current >= min_count:
            return
        needed = min_count - current
        for i in range(needed):
            label = f"auto_user_{current + i + 1}"
            wallet = self._generate_wallet(WalletType.PAYMENT_USER, label)
            self._add_wallet_to_collections(wallet)
        self._save_all_wallets()
        print(f"Added {needed} additional PAYMENT_USER wallets (total {min_count})")


# Global wallet manager instance
wallet_manager = WalletManager() 