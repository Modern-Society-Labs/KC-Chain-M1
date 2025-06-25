# KC-Chain Enhanced Stress Test Simulator with IoT Data Pipeline

This repository contains an enhanced load-testing framework for KC-Chain (Arbitrum Orbit) devnet that integrates real IoT data simulation through the validated lcore-node MVP architecture. It dispatches realistic, randomly-generated transactions across both traditional blockchain operations and real IoT data pipeline workflows.

## 🚀 Enhanced Features

### Traditional Blockchain Stress Testing
1. `payment_app` – user payments in local currency (simulated as ETH transfers)
2. `merchant_app` – business settlements
3. `lending_app` – loan origination / repayments

### **NEW: Real IoT Data Pipeline Integration**
4. `data_pipeline` – **Real IoT device simulation with dual-encryption pipeline**
   - **Device Registration**: Simulates IoT devices registering through lcore-node MVP
   - **Real Data Submission**: Uses actual CSV data samples (EV, greenhouse, sales)
   - **Dual Encryption**: AES-256-GCM + ChaCha20-Poly1305 pipeline
   - **On-Chain Commitment**: Direct integration with deployed Stylus contract

### Deployment Targets
This project is designed to run **24/7** on [Railway](https://railway.app/) while still being effortless to clone and run locally.

* **Live Demo** – the public Railway URL exposes:
  * `/health` → simple 200 OK liveness probe
  * `/metrics` → JSON snapshot of KPIs (volume, latency, success-rate)
* **Self-host** – clone, `cp env.example .env`, then either:
  * `docker build -t kc-stress . && docker run --env-file .env kc-stress`
  * or `python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt && python main.py`

---

## 🎯 Milestone 1 — Objectives & KPIs

| Objective | Requirement | Where to Observe |
|-----------|-------------|------------------|
| zkProof validation | Validate ≥ **3** test datasets using zkProofs | `smartcity-test/docs/mvp-testing.md` + `/metrics` (commit counts) |
| SQLite R/W on testnet | Functional read **and** write via `lcore-node` | `/metrics` → `on_chain_commitments` counter |
| IoT data throughput | ≥ **50** data entries / day | `/metrics` → `daily_submission_rate` |

The `/metrics` endpoint returns real-time booleans `meets_success_target`, `meets_latency_target`, `meets_volume_target` so evaluators know instantly if targets are hit.

---

## 🔧 Quick Start (Local)

```bash
# clone & config
git clone https://github.com/<your-org>/kc-chain-stress-test.git
cd kc-chain-stress-test
cp env.example .env  # fill in real RPC + keys

# run with Docker
docker build -t kc-stress .
docker run --env-file .env -p 8000:8000 kc-stress

# OR run with Python
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

Visit `http://localhost:8000/metrics` to verify KPIs.

---

## 🚀 Deploy on Railway

1. Create a new Railway project and **link this GitHub repo**.
2. Add the environment variables from `env.example` in the Railway dashboard.
3. Railway will auto-detect the `Dockerfile` and build the image.
4. After deploy finishes, open the generated URL → `/metrics` should show live stats.

> **Tip:** Set Railway Health Check to `GET /health`.

---

## 🔒 Security & Privacy

* **No secrets in repo** – `.env` is ignored; all keys are placeholders.
* **Logs excluded** – runtime CSVs are ignored via `.gitignore`.
* **Binary DBs removed** – large `*.db` artefacts are no longer tracked.

## 🏗️ Architecture Integration

### Data Flow Pipeline
```
CSV Data Samples → Data Parsers → Device Simulators → lcore-node API → Dual Encryption → Stylus Contract (0xd99061c28b9063d9651fea67930fc4ff598ba5b2)
```

### Performance Targets
- **Volume**: 500 IoT entries per day simulation
- **Success Rate**: >95% for data submissions  
- **Latency**: <30 seconds end-to-end pipeline
- **Concurrency**: Operates alongside traditional stress test modules

## Prerequisites

* Python ≥ 3.10
* **lcore-node MVP running** (for IoT pipeline integration)
* An RPC endpoint and funded account on KC-Chain

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Configuration

Create an `.env` file at the project root:

```env
# Blockchain Configuration
PRIVATE_KEY=0x...
RPC_HTTP_URL=https://rpc.devnet.alchemy.com/7eade438-d743-4dc5-ac64-3480de391200
CHAIN_ID=1205614515668104

# lcore-node MVP Integration
LCORE_NODE_URL=http://127.0.0.1:3000
MVP_IOT_PROCESSOR_ADDRESS=0xd99061c28b9063d9651fea67930fc4ff598ba5b2

# IoT Simulation Parameters
IOT_DEVICE_COUNT=15
IOT_REGISTRATION_RATE=0.1
IOT_DATA_SUBMISSION_RATE=0.2
TARGET_DAILY_ENTRIES=500
TARGET_SUCCESS_RATE=0.95
TARGET_MAX_LATENCY_SEC=30.0
```

## Running the Enhanced Simulator

### Option 1: Full Integration (Recommended)
Ensure lcore-node MVP is running, then:

```bash
source .venv/bin/activate
python main.py
```

This runs:
- Traditional blockchain stress testing (payments, merchant, lending)
- **Real IoT device registration and data submission**
- Performance monitoring and metrics tracking

### Option 2: Blockchain-Only Mode
If lcore-node is not available, the simulator gracefully degrades to traditional stress testing only.

## 📊 Monitoring & Metrics

### Enhanced Logging
- `logs/tx_metrics.csv` - Traditional blockchain transaction metrics
- `logs/iot_metrics.csv` - **NEW: IoT pipeline-specific metrics**
- `logs/device_stats.csv` - **NEW: Device fleet statistics**

### Real-Time Monitoring
The simulator provides real-time performance metrics:

```
============================================================
IoT PIPELINE PERFORMANCE METRICS
============================================================
Runtime: 0.25 hours
Total Operations: 45
Success Rate: 97.8% (Target: 95.0%) ✅
Avg Latency: 2.34s (Target: <30s) ✅
Daily Rate: 432.0 entries/day (Target: 500) ❌
Device Registrations: 12
Data Submissions: 33
On-Chain Commitments: 31
============================================================
```

## 🧪 Data Sources

The enhanced simulator uses real data samples:

1. **EV Predictive Maintenance**: Time-series sensor data from electric vehicles
2. **Greenhouse Agricultural Data**: Plant growth metrics and environmental sensors  
3. **Sales Transaction Data**: Commercial transaction records

Data is parsed from CSV files in `smartcity-test/data/` with realistic variance applied.

## 🔧 Component Architecture

### Enhanced Components
- `utils/data_parsers.py` - Parse CSV samples into realistic IoT data
- `utils/device_simulator.py` - Manage fleet of simulated IoT devices
- `utils/lcore_client.py` - HTTP client for lcore-node MVP API
- `utils/iot_metrics.py`

## 🔖 Documentation Index

* [Milestone-1 Report](docs/milestone-report.md)

## 🌐 Live Deployment & Explorer Links

KC-Chain devnet explorer: <https://explorer-1205614515668104.devnet.alchemy.com/>

| Purpose | Address / URL |
|---------|---------------|
| Stylus contract `MVPIoTProcessor` | [`0xd99061c28b9063d9651fea67930fc4ff598ba5b2`](https://explorer-1205614515668104.devnet.alchemy.com/address/0xd99061c28b9063d9651fea67930fc4ff598ba5b2) |
| Stress-test metrics endpoint | `https://<your-railway-url>/metrics` |


## 🪪 Simulated Wallets

The simulator uses pre-funded devnet wallets. Private keys are **never** published; only public addresses are listed here.

| Label | Address | Role in simulator |
|-------|---------|-------------------|
| main_funder | 0xEd14eDC72F6DA4f2a68b339d6B3526534c9C5c59 | Provides ETH to all other wallets at start-up |
| user_alice | 0xE26E30d3dd83627e4ADf96C87c5Fc1A290f03bed | Sends payment txs in `payment_app` |
| user_bob | 0x6A590348500A4d423bd2660b44C94458447e4D92 | Sends payment txs |
| user_charlie | 0x4C403a9e4BA771816022D2D44FAb3D39EEe71d6E | Sends payment txs |
| merchant_store_a | 0xf0e75a1Ef0B79DFc3d33A7062646E72D92d70e48 | Receives settlements in `merchant_app` |
| merchant_store_b | 0x6263DBE3D26a28fE0C11Fb88761Fc5Ac33Bf1d58 | Receives settlements |
| lending_protocol | 0x864BBd89AB4814912A63167a91DA633BCe356729 | Originates loans in `lending_app` |
| borrower_alice | 0x0Bb6ec0ed8ABebdce4D5383Be8Bfa0a06D6Ef341 | Makes loan repayments |
| iot_device_pool | 0x8a03c782E3c7F58955BC42c3C8FfdBF0a8dB3008 | Default on-chain identity for device submissions |
| iot_operator_a | 0xe2adB5B52043576f2C1d382020bcda2899686F72 | Registers devices & monitors pipeline |
| iot_operator_b | 0x4a303984Bf3a0829261391bb4c9a243F1Dfd7087 | Registers devices |
| auto_user_4 | 0xB813b503600C97952E10fd6f238f3b53B1B23E8F | Payment user |
| auto_user_5 | 0x56729034cDdeed42FC7FdE953d737735753e6E1e | Payment user |
| auto_user_6 | 0x54BaBa905DBfA2e3Acd4dd4e47799FA4f9fB89DB | Payment user |
| auto_user_7 | 0x68E7C4CB5E7d6Ee250Ad1b7812d0D56186861863 | Payment user |
| auto_user_8 | 0xEB985bf239baC1658E119f5E41bF704dcE35da94 | Payment user |
| auto_user_9 | 0x084E38a97430edACFA4CBd9305a1a13924A6665c | Payment user |
| auto_user_10 | 0xAEee257cbF616a620C839665298eb09F62E77f9B | Payment user |
| auto_user_11 | 0x0606e69Ea93515a05d0BB65Dc6208b4E8095A014 | Payment user |
| auto_user_12 | 0x8505714BdAAdd02b22746f9772aa0CE8DD9922DD | Payment user |
| auto_user_13 | 0xee3Aad90dDF580649b7938e8aCcE93Eb7414FB5A | Payment user |
| auto_user_14 | 0x5BABD6232D1E44eF60d602bde384232241e612E6 | Payment user |
| auto_user_15 | 0xd81509af6F29B1A2CE7C2367807E89DB823eA3Cc | Payment user |
| auto_user_16 | 0xA675af321014d6DC51C6f52A487D11ff1F83bDbA | Payment user |
| auto_user_17 | 0xD7504A63795F7d193BcF0Db31201cDaAb240adDd | Payment user |
| auto_user_18 | 0x6ef74Fc1dbfd351096E2A080e1d1619258C98953 | Payment user |