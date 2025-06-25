import random
import secrets

from eth_utils import to_checksum_address

from utils.metrics_logger import log_metric
from utils.tx_builder import send_eth, TxSendError
from utils.wallet_manager import wallet_manager, WalletType


async def simulate_transaction():
    """Simulate a local currency payment by transferring small amount of ETH."""
    # Random recipient address (not controlled)
    random_addr = to_checksum_address("0x" + secrets.token_hex(20))
    amount_wei = 0  # Only pay gas; no value transferred

    # Choose a random user wallet for this tx
    wallet = wallet_manager.get_random_wallet_by_type(WalletType.PAYMENT_USER)
    if wallet is None:
        raise TxSendError("No available user wallet")

    try:
        tx_hash, receipt, latency = await send_eth(random_addr, amount_wei, wallet=wallet)
        log_metric(
            module="payment_app",
            tx_hash=tx_hash,
            status="success" if receipt.status == 1 else "failed",
            gas_used=receipt.gasUsed,  # type: ignore[attr-defined]
            latency_sec=latency,
        )
    except TxSendError as exc:
        log_metric(
            module="payment_app",
            tx_hash="",
            status="error",
            gas_used=0,
            latency_sec=0,
            error=str(exc),
        )
    # Slight jitter can be added externally in caller. 