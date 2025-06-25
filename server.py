"""Lightweight HTTP server exposing health & metrics endpoints.

This allows Railway (or any orchestrator) to perform container healthchecks
and lets evaluators view live KPI stats while the stress-test runs.
"""

import os
from flask import Flask, jsonify

from utils.iot_metrics import iot_metrics_tracker

app = Flask(__name__)


@app.route("/health", methods=["GET"])  # simple liveness probe
def health() -> tuple:
    return jsonify(status="ok"), 200


@app.route("/metrics", methods=["GET"])  # expose current KPI snapshot
def metrics() -> tuple:
    return jsonify(iot_metrics_tracker.get_current_metrics()), 200


def run():
    port = int(os.getenv("HEALTHCHECK_PORT", 8000))
    # Expose on all interfaces inside container
    app.run(host="0.0.0.0", port=port, debug=False)


if __name__ == "__main__":
    run() 