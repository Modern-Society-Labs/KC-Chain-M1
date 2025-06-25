import time
from typing import Tuple, Optional

from web3 import Web3
from web3.exceptions import ContractLogicError, TransactionNotFound
from web3.types import TxReceipt, TxParams

from config.settings import web3_http as w3, CHAIN_ID, DEFAULT_GAS_LIMIT, FIXED_GAS_PRICE_WEI, get_account
from utils.wallet_manager import ManagedWallet  # type: ignore


class TxSendError(Exception):
    """Raised when a transaction fails to be mined or revert."""


async def build_base_tx(sender: str) -> TxParams:  # type: ignore[type-arg]
    """Generate a base transaction dict with nonce, gas limit, and gas price."""
    nonce = w3.eth.get_transaction_count(sender)
    gas_price = (
        FIXED_GAS_PRICE_WEI if FIXED_GAS_PRICE_WEI > 0 else w3.eth.gas_price  # simplistic for demo
    )
    return {
        "chainId": CHAIN_ID,
        "nonce": nonce,
        "gas": DEFAULT_GAS_LIMIT,
        "gasPrice": gas_price,
    }


async def send_eth(to_address: str, amount_wei: int, wallet: Optional[ManagedWallet] = None) -> Tuple[str, TxReceipt, float]:
    """Send native ETH transfer as simple stress tx."""
    if wallet is None:
        account = get_account()
        sender = account.address
        pk = account.key
    else:
        sender = wallet.address
        pk = wallet.private_key

    # Use the minimal gas required for a native ETH transfer (21,000) instead of the
    # global DEFAULT_GAS_LIMIT which is tuned for complex contract calls.
    ETH_TRANSFER_GAS_LIMIT = 21_000

    base_tx = await build_base_tx(sender)

    tx: TxParams = {
        **base_tx,  # type: ignore[arg-type]
        "to": Web3.to_checksum_address(to_address),
        "value": amount_wei,
        "gas": ETH_TRANSFER_GAS_LIMIT,
    }

    signed = w3.eth.account.sign_transaction(tx, pk)

    # Quick balance check to avoid obvious failures
    balance = w3.eth.get_balance(sender)
    estimated_total_cost = tx["value"] + tx["gas"] * tx["gasPrice"]
    if balance < estimated_total_cost:
        raise TxSendError(
            f"Insufficient balance: need {estimated_total_cost} wei, have {balance} wei"
        )

    try:
        tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)
    except ValueError as exc:
        # Wrap lower-level exceptions so callers handle uniformly
        raise TxSendError(f"Submission error: {exc}") from exc

    start = time.time()

    try:
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
    except (TransactionNotFound, ContractLogicError) as exc:
        raise TxSendError(f"Transaction failed: {exc}")

    latency = time.time() - start
    return receipt.transactionHash.hex(), receipt, latency  # type: ignore[attr-defined] 