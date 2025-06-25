import csv
import os
import time
import logging
from pathlib import Path
from typing import Dict, DefaultDict

LOG_DIR = Path(os.getenv("LOG_DIR", "logs"))
LOG_DIR.mkdir(parents=True, exist_ok=True)

CSV_FILE = LOG_DIR / "tx_metrics.csv"

# Ensure header
if not CSV_FILE.exists():
    with open(CSV_FILE, "w", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "timestamp",
                "module",
                "tx_hash",
                "status",
                "gas_used",
                "latency_sec",
                "error",
            ],
        )
        writer.writeheader()

# Configure local logger (inherits global level)
logger = logging.getLogger(__name__)

_agg: DefaultDict[str, int] = DefaultDict(int)  # module -> success count

# ---------------------------------------------------------------------------
# Public helpers
# ---------------------------------------------------------------------------

def get_aggregate_counts() -> Dict[str, int]:
    """Return a shallow copy of the per-module success counters."""
    return dict(_agg)


def print_dapp_summary() -> None:
    """Log a one-shot summary of total successful regular dApp transactions."""
    if not _agg:
        logger.info("No successful dApp transactions yet")
        return

    total = sum(_agg.values())
    logger.info("================= dApp Transactions Summary =================")
    logger.info(f"Total successful dApp transactions: {total}")
    for module, cnt in _agg.items():
        logger.info(f"{module}: {cnt} successes")
    logger.info("=============================================================")

def log_metric(module: str, tx_hash: str, status: str, gas_used: int, latency_sec: float, error: str = ""):  # noqa: E501
    """Append a transaction metric row to CSV file."""
    with open(CSV_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                int(time.time()),
                module,
                tx_hash,
                status,
                gas_used,
                f"{latency_sec:.4f}",
                error,
            ]
        )

    # Update aggregate and print to stdout for visibility inside container
    if status == "success":
        _agg[module] += 1

    logger.info(
        f"TX | {module} | {status.upper()} | latency {latency_sec:.2f}s | gas {gas_used} | total successes { _agg[module] }"
    ) 