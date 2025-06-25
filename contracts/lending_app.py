import random
import secrets

from eth_utils import to_checksum_address

from utils.metrics_logger import log_metric
from utils.tx_builder import send_eth, TxSendError
from utils.wallet_manager import wallet_manager, WalletType

BORROWER_ADDRESS = to_checksum_address("0x" + secrets.token_hex(20))


async def originate_loan():
    """Simulate loan origination (protocol sending funds to borrower)"""
    loan_amount_wei = 0  # Only pay gas

    wallet = wallet_manager.get_random_wallet_by_type(WalletType.PAYMENT_USER)
    if wallet is None:
        raise TxSendError("No available user wallet")

    try:
        tx_hash, receipt, latency = await send_eth(BORROWER_ADDRESS, loan_amount_wei, wallet=wallet)
        log_metric(
            module="lending_app",
            tx_hash=tx_hash,
            status="success" if receipt.status == 1 else "failed",
            gas_used=receipt.gasUsed,  # type: ignore[attr-defined]
            latency_sec=latency,
        )
    except TxSendError as exc:
        log_metric(
            module="lending_app",
            tx_hash="",
            status="error",
            gas_used=0,
            latency_sec=0,
            error=str(exc),
        )


async def make_repayment():
    """Simulate borrower paying back part of the loan"""
    repayment_amount_wei = 0

    wallet = wallet_manager.get_random_wallet_by_type(WalletType.PAYMENT_USER)
    if wallet is None:
        raise TxSendError("No available user wallet")

    try:
        tx_hash, receipt, latency = await send_eth(to_checksum_address("0x" + secrets.token_hex(20)), repayment_amount_wei, wallet=wallet)
        log_metric(
            module="lending_app",
            tx_hash=tx_hash,
            status="success" if receipt.status == 1 else "failed",
            gas_used=receipt.gasUsed,  # type: ignore[attr-defined]
            latency_sec=latency,
        )
    except TxSendError as exc:
        log_metric(
            module="lending_app",
            tx_hash="",
            status="error",
            gas_used=0,
            latency_sec=0,
            error=str(exc),
        ) 