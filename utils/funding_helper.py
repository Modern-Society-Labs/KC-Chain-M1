import asyncio
import time
from typing import List, Dict, Any
from web3 import Web3

from config.settings import web3_http as w3, DEFAULT_GAS_LIMIT, DEFAULT_FUNDING_AMOUNT_ETH
from utils.wallet_manager import wallet_manager, WalletType, ManagedWallet
from utils.tx_builder import build_base_tx


class FundingHelper:
    """Helper class to distribute funds across managed wallets"""
    
    def __init__(self):
        self.w3 = w3
    
    async def fund_all_wallets_from_external(self, funder_private_key: str, amount_per_wallet_eth: float = DEFAULT_FUNDING_AMOUNT_ETH) -> Dict[str, Any]:
        """Fund all managed wallets from an external funder wallet
        
        Args:
            funder_private_key: Private key of wallet with funds (your 1 ETH wallet)
            amount_per_wallet_eth: Amount to send to each wallet in ETH
            
        Returns:
            Dict with funding results
        """
        funder_account = self.w3.eth.account.from_key(funder_private_key)
        funder_address = funder_account.address
        
        print(f"🚀 Starting funding operation from {funder_address}")
        print(f"💰 Amount per wallet: {amount_per_wallet_eth} ETH")
        
        # Check funder balance
        funder_balance_wei = self.w3.eth.get_balance(funder_address)
        funder_balance_eth = self.w3.from_wei(funder_balance_wei, 'ether')
        
        print(f"💳 Funder balance: {funder_balance_eth} ETH")
        
        # Calculate total needed
        total_wallets = len(wallet_manager.wallets)
        total_needed_eth = total_wallets * amount_per_wallet_eth
        estimated_gas_cost_eth = total_wallets * 0.001  # Rough estimate
        
        print(f"📊 Total wallets: {total_wallets}")
        print(f"💸 Total ETH needed: {total_needed_eth + estimated_gas_cost_eth} ETH (including gas)")
        
        if funder_balance_eth < (total_needed_eth + estimated_gas_cost_eth):
            return {
                "success": False,
                "error": f"Insufficient funds. Need {total_needed_eth + estimated_gas_cost_eth} ETH, have {funder_balance_eth} ETH"
            }
        
        # Fund each wallet
        results = []
        successful_transfers = 0
        failed_transfers = 0
        
        for wallet in wallet_manager.wallets.values():
            try:
                print(f"💸 Funding {wallet.label} ({wallet.address})...")
                
                # Build transaction
                GAS_LIMIT_ETH_TRANSFER = 21_000

                tx = await build_base_tx(funder_address)
                tx.update({
                    "to": wallet.address,
                    "value": self.w3.to_wei(amount_per_wallet_eth, 'ether'),
                    "gas": GAS_LIMIT_ETH_TRANSFER,
                })
                
                # Sign and send
                signed_tx = self.w3.eth.account.sign_transaction(tx, funder_private_key)
                tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
                
                # Wait for confirmation
                receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=60)
                
                if receipt.status == 1:
                    successful_transfers += 1
                    print(f"✅ Success: {wallet.label} funded with {amount_per_wallet_eth} ETH")
                    results.append({
                        "wallet": wallet.label,
                        "address": wallet.address,
                        "success": True,
                        "tx_hash": receipt.transactionHash.hex(),
                        "amount_eth": amount_per_wallet_eth
                    })
                else:
                    failed_transfers += 1
                    print(f"❌ Failed: {wallet.label} transaction reverted")
                    results.append({
                        "wallet": wallet.label,
                        "address": wallet.address,
                        "success": False,
                        "error": "Transaction reverted"
                    })
                
                # Small delay between transactions
                await asyncio.sleep(1)
                
            except Exception as e:
                failed_transfers += 1
                print(f"❌ Error funding {wallet.label}: {e}")
                results.append({
                    "wallet": wallet.label,
                    "address": wallet.address,
                    "success": False,
                    "error": str(e)
                })
        
        # Update all wallet balances
        wallet_manager.update_all_balances()
        
        summary = {
            "success": True,
            "total_wallets": total_wallets,
            "successful_transfers": successful_transfers,
            "failed_transfers": failed_transfers,
            "amount_per_wallet_eth": amount_per_wallet_eth,
            "total_eth_distributed": successful_transfers * amount_per_wallet_eth,
            "results": results
        }
        
        print(f"\n🎉 Funding complete!")
        print(f"✅ Successful: {successful_transfers}/{total_wallets}")
        print(f"❌ Failed: {failed_transfers}/{total_wallets}")
        print(f"💰 Total distributed: {successful_transfers * amount_per_wallet_eth} ETH")
        
        return summary
    
    def generate_funding_addresses_list(self) -> List[str]:
        """Generate a list of all wallet addresses for manual funding"""
        addresses = []
        for wallet in wallet_manager.wallets.values():
            addresses.append(wallet.address)
        return addresses
    
    def print_funding_instructions(self, amount_per_wallet_eth: float = DEFAULT_FUNDING_AMOUNT_ETH):
        """Print instructions for manual funding"""
        print("\n" + "="*80)
        print("💰 FUNDING INSTRUCTIONS")
        print("="*80)
        
        summary = wallet_manager.get_funding_summary()
        total_needed = len(wallet_manager.wallets) * amount_per_wallet_eth
        
        print(f"Total wallets to fund: {summary['total_wallets']}")
        print(f"Recommended amount per wallet: {amount_per_wallet_eth} ETH")
        print(f"Total ETH needed: {total_needed} ETH (plus gas costs)")
        
        if summary['funder_address']:
            print(f"\n🎯 MAIN FUNDER WALLET (fund this one with your 1 ETH):")
            print(f"Address: {summary['funder_address']}")
            print(f"Use this address to fund all others automatically.")
        
        print(f"\n📋 ALL WALLET ADDRESSES:")
        for wallet_type, info in summary['wallets_by_type'].items():
            print(f"\n{wallet_type.upper()} ({info['count']} wallets):")
            for addr in info['addresses']:
                print(f"  {addr}")
        
        print("\n🚀 FUNDING OPTIONS:")
        print("1. Fund the main funder wallet, then run: python -c \"from utils.funding_helper import *; funding_helper.fund_all_from_funder()\"")
        print("2. Manually send funds to each address above")
        print("3. Use a multi-send tool to distribute to all addresses at once")
        print("="*80)
    
    async def fund_all_from_funder(self, amount_per_wallet_eth: float = DEFAULT_FUNDING_AMOUNT_ETH):
        """Fund all wallets using the managed funder wallet"""
        funder_wallet = wallet_manager.get_funder_wallet()
        if not funder_wallet:
            print("❌ No funder wallet found!")
            return
        
        print(f"Using managed funder wallet: {funder_wallet.address}")
        return await self.fund_all_wallets_from_external(
            funder_wallet.private_key, 
            amount_per_wallet_eth
        )


# Global funding helper instance
funding_helper = FundingHelper() 