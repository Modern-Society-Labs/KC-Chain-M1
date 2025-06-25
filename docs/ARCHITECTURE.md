# System Architecture (Living Document)

This file is updated as components evolve.  For the snapshot of Milestone-1, see `docs/milestone-report.md`.

---

## Top-Level Diagram

```mermaid
flowchart LR
    subgraph Python Container
        MP[main.py Orchestrator]
        MP --> P1(payment_app)
        MP --> M1(merchant_app)
        MP --> L1(lending_app)
        MP --> DP[data_pipeline]
        DP --> LC(Lcore Client)
        MP --> S[Flask /metrics]
    end

    subgraph Rust Container (lcore-node)
        API[Axum API] --> ENC(Dual Encryption)
        ENC --> DB[(SQLite)]
        API --> KC[KC-Chain Client]
    end

    KC -->|Stylus tx| CHAIN[(MVPIoTProcessor)]
```

---

## Repository Map

| Path | Language | Purpose |
|------|----------|---------|
| `contracts/` | Python | Stress-test transaction modules |
| `utils/` | Python | Shared helpers (wallets, metrics, parsers) |
| `server.py` | Python | Exposes `/health` & `/metrics` |
| `smartcity-test/lcore-node/` | Rust | MVP node (REST, encryption, on-chain) |
| `smartcity-test/stylus_contracts/` | Rust (WASM) | Stylus contract source |

---

## Data Flow
1. `device_simulator` synthesises sensor JSON.
2. `lcore_client` POSTs to `lcore-node` (`/device/data`).
3. Rust node encrypts ➜ stores ➜ submits Stylus tx.
4. Python updates KPI counters and writes CSV logs.

---

## Modules & Entry Points

### Python
| Module | Entry | Key Functions |
|--------|-------|--------------|
| `main.py` | `asyncio.run(main())` | orchestrator & thread for Flask |
| `contracts/data_pipeline.py` | `submit_iot_sensor_data()` | IoT flow |
| `utils/device_simulator.py` | class `DeviceSimulator` | sensor payloads |

### Rust Crates (lcore-node)
| Crate | Purpose |
|-------|---------|
| `api` | Axum routes & validation |
| `encryption` | AES-GCM + ChaCha20 libs |
| `storage` | Diesel ORM / SQLite |
| `kc_chain` | ethers-rs client |
| `device` | domain types & manager |

---

## Future Evolution
* Replace SQLite with Cartesi Rollups input box.  
* Move encryption + proof into RiscZero guest inside Cartesi VM.  
* Split payment / merchant / lending apps into separate containers for micro-benchmarking. 