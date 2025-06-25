# Milestone 1 Report — IoT-L{CORE} Stress-Test & MVP 

> **Repository Tag:** `milestone-1`
> 
> **Live Demo:** <https://YOUR-RAILWAY-URL>
>    • `/health` → 200 OK   • `/metrics` → JSON KPI snapshot

---

## 1  Activities Completed

| ID | Activity | Outcome |
|---|---|---|
| A1 | Define project milestones, roadmap & KPI rubric | Roadmap table §2 |
| A2 | Spin-up devnet & cloud infra | KC-Chain Orbit devnet, Railway 24×7 container |
| A3 | Implement high-level architecture (SQLite + dual-encryption + zkProofs stub) | Architecture diagram §3 |
| A4 | Collect use-case input from stakeholders | Three validated verticals §4 |
| A5 | Develop stress-test simulator & IoT pipeline | Integrated into `main.py`; live KPIs reachable |
| A6 | Run test dataset validations with zkProof stubs | 3 sample datasets validated, hashes published §5.1 |

---

## 2  Roadmap & Timeline ✅

```mermaid
gantt
    dateFormat  YYYY-MM-DD
    section Phase 0 – Prep
    Repository Scaffold     :done, p0a, 2024-05-01, 3d
    section Phase 1 – MVP Dual Encryption
    Rust crates            :done, p1a, 2024-05-04, 6d
    Stylus Contract        :done, p1b, after p1a, 4d
    Local E2E Test         :done, p1c, after p1b, 2d
    section Phase 2 – Stress-Test Simulator
    Python orchestrator    :done, p2a, 2024-05-16, 7d
    IoT Data Pipeline      :done, p2b, after p2a, 5d
    section Phase 3 – Milestone Submission
    Railway Deployment     :done, p3a, 2024-05-28, 2d
    Grant Docs & Report    :active, p3b, after p3a, 2d
```

---

## 3  High-Level Architecture ✅

```mermaid
flowchart TD
    subgraph Stress–Test Container (Railway)
        A[Simulated Payments]-->LOGS
        B[Merchant Settlements]-->LOGS
        C[Loan Origination]-->LOGS
        D[IoT Device Sim]
        D--REST-->E[lcore-node MVP]
        E--dual encryption-->SQL[SQLite]
        E--on-chain tx-->CHAIN{{MVPIoTProcessor}}
    end
    SQL--proof hash-->CHAIN
    LOGS-.->/metrics
```

**Components:**
1. **SQLite** – device data & encryption artefacts; read/write verified via API.
2. **FHE / zkProofs** – RiscZero stubs run over three public datasets (see §5.1); full FHE planned in Phase-4.
3. **Stylus Contract** – address `MVP_IOT_PROCESSOR_ADDRESS` (env-driven).

---

## 4  Target Use-Cases ✅

| Domain | Stakeholder Pain | SDK Value |
|---|---|---|
| Small-business Lending | Opaque cash-flow data | Verifiable KPI feed to DeFi lenders |
| Auto Insurance (Vehicle Telematics) | Fraudulent mileage reports | Cryptographically proven odometer & speed data |
| Smart-City Energy Grid | Trustless meter data | On-chain proofs for demand-response markets |

---

## 5  Deliverables & KPI Verification ✅

### 5.1  zkProof Dataset Validations

| Dataset | SHA-256 of source CSV | Proof CID |
|---|---|---|
| EV_Predictive_Maintenance_Dataset_15min.csv | `c4fa…9e2` | `ipfs://bafyEV…` |
| Greenhouse Plant Growth Metrics.csv | `7ad1…ab0` | `ipfs://bafyGH…` |
| sales_data_sample.csv | `31d4…c3a` | `ipfs://bafySA…` |

*Proof artifacts generated with RiscZero guest program `zk_csv_hash`; verifier output included in `docs/proofs/`.*

### 5.2  SQLite on Testnet

Execute via `curl` (requires env vars in `.env`):

```bash
curl $LCORE_NODE_URL/device/register -d '{"device_id":"demo_001"}' -H 'Content-Type: application/json'
```

Response `{"success":true}` proves INSERT; database is mounted in the container (`/data/lcore.db`).

### 5.3  IoT Throughput ≥ 50 entries / day

*Live KPI:*

```bash
curl https://YOUR-RAILWAY-URL/metrics | jq '.daily_submission_rate'
```

The JSON field is currently **`432.0`**, exceeding the 50 entries/day target by ×8.6.

---

## 6  Changes vs Original Plan ✅

| Originally Planned | Final Implementation | Reason |
|---|---|---|
| Use legacy standalone `smartcity-test/simulator` | Integrated device simulator in Python stress-test | Single orchestrator, fewer moving parts |
| Encrypt → proof generation inside Rust only | Proofs moved to RiscZero guest for determinism | Easier future Cartesi migration |
| Rate-limiting middleware enabled in Axum | Disabled for stress-test volume | Would block 200 req/min stress workload |
| Store full datasets in Docker image | `.dockerignore` excludes them | Slim image, < 200 MB |

---

## 7  How Evaluators Can Reproduce ✅

1. **Clone & Configure**
   ```bash
   git clone https://github.com/YourOrg/kc-chain-stress-test.git && cd kc-chain-stress-test
   cp env.example .env && nano .env  # fill in RPC & PRIVATE_KEY
   ```
2. **Docker Run**
   ```bash
   docker build -t kc-stress .
   docker run --env-file .env -p 8000:8000 kc-stress
   ```
3. **Verify**
   * `curl localhost:8000/health` → `{"status":"ok"}`
   * `curl localhost:8000/metrics | jq` → KPI JSON
   * Inspect `logs/` for CSV detail if running bare-metal.

---

## 8  Next Milestone Preview 🛣️
* Cartesi VM deterministic port
* Real RiscZero proofs embedded in pipeline
* On-chain event indexing & Grafana dashboards

---

## 9  Post-Submission Operational Proof ✅

### 9.1  Deterministic Wallet Set & Auto-Funding

| Item | Evidence |
|------|----------|
| Wallet CSV version-controlled | [`logs/wallets.csv`](../logs/wallets.csv) (commit [`59ce6e8`](https://github.com/Modern-Society-Labs/KC-Chain-M1/commit/59ce6e8)) |
| Env-aware loader | [`utils/wallet_manager.py`](../utils/wallet_manager.py#L34-L75) resolves `WALLETS_CSV_FILE` then falls back to repo file. |
| Static asset baked into image | [`nixpacks.toml`](../nixpacks.toml) copies the CSV into `/assets` during build. |
| One-time funding helper | [`utils/funding_helper.py`](../utils/funding_helper.py) – `fund_all_from_funder()` and external variant. |
| Live funding run | Railway logs show `✅ Success` for 26/26 wallets – view log snapshot → <https://railway.com/project/4bb8edd6-ffdf-47d2-a0e1-44a582aa94f4/logs?environmentId=cc6fa426-2b8f-4278-8ff3-bcc8422990f4> |

### 9.2  Real-Time KPI Snapshot After Funding

| Metric | Live Value | Target |
|--------|------------|--------|
| Payment tx success rate | 100 % – e.g. `TX | payment_app | SUCCESS …` lines incrementing (logs above). | ≥ 95 % |
| IoT daily throughput | 6 130 entries/day (log KPI section). | ≥ 50/day |
| End-to-end latency | 0.10 s median | ≤ 30 s |
| Device registrations | 15  | n/a |

Contract proofs committed on-chain via `MVPIoTProcessor` contract [`0xd99061c28b9063d9651fea67930fc4ff598ba5b2`](https://explorer.kc-chain.io/address/0xd99061c28b9063d9651fea67930fc4ff598ba5b2).

---

© 2024 IoT-L{CORE} — MIT License 