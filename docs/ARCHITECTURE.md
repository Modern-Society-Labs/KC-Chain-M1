# System Architecture (Living Document)

> **📋 STRESS TEST DOCUMENTATION**: This architecture documents the stress testing setup across multiple IoT-L{CORE} repositories.

This file is updated as components evolve.  For the snapshot of Milestone-1, see `docs/milestone-report.md`.

---

## Top-Level Diagram (Milestone 1 - Current)

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
        ENC --> SQLITE[Local SQLite Database]¹
        API --> KC[KC-Chain Client]
    end

    KC -->|Stylus tx| CHAIN[([MVPIoTProcessor](https://github.com/Modern-Society-Labs/lcore-platform))]
```

## Future Architecture (Milestone 2 - Cartesi Integration)

```mermaid
flowchart LR
    subgraph Python Container
        MP[main.py Orchestrator]
        MP --> DP[data_pipeline]
        DP --> LC(Lcore Client)
    end

    subgraph Rust Container (lcore-node)
        API[Axum API] --> ENC(Dual Encryption)
        ENC --> CRT[[Cartesi Encryption Layer](https://github.com/Modern-Society-Labs/lcore-node)]¹
        API --> KC[KC-Chain Client]
    end

    KC -->|Stylus tx| CHAIN[([MVPIoTProcessor](https://github.com/Modern-Society-Labs/lcore-platform))]
```

¹ *Will be migrated to [Cartesi Layer](https://github.com/Modern-Society-Labs/lcore-node) in Milestone 2*

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

## Data Flow (Milestone 1 - Current)
1. `device_simulator` synthesises sensor JSON.
2. `lcore_client` POSTs to `lcore-node` (`/device/data`).
3. Rust node encrypts ➜ stores in local SQLite (`/tmp/lcore-mvp.db`) ➜ submits Stylus tx.
4. Python updates KPI counters and writes CSV logs.

## Future Data Flow (Milestone 2 - Cartesi)
1. `device_simulator` synthesises sensor JSON.
2. `lcore_client` POSTs to `lcore-node` (`/device/data`).
3. Rust node encrypts ➜ forwards payload to [Cartesi Rollups](https://github.com/Modern-Society-Labs/lcore-node) ➜ generates RiscZero proofs ➜ submits Stylus tx.
4. Python updates KPI counters and writes CSV logs.

---

## Modules & Entry Points

### Python
| Module | Entry | Key Functions |
|--------|-------|--------------|
| `main.py` | `asyncio.run(main())` | orchestrator & thread for Flask |
| `contracts/data_pipeline.py` | `submit_iot_sensor_data()` | IoT flow |
| `utils/device_simulator.py` | class `DeviceSimulator` | sensor payloads |

### Rust Crates (lcore-node) - Milestone 1
| Crate | Purpose |
|-------|---------|
| `api` | Axum routes & validation |
| `encryption` | AES-GCM + ChaCha20 libs |
| `storage` | Local SQLite database operations |
| `kc_chain` | ethers-rs client |
| `device` | domain types & manager |

### Future Rust Crates - Milestone 2
| Crate | Purpose |
|-------|---------|
| `rollups_storage` | [Cartesi Rollups](https://github.com/Modern-Society-Labs/lcore-node) off-chain data persistence |
| `cartesi_rollups` | [Off-chain input box integration](https://github.com/Modern-Society-Labs/lcore-node) |
| `risc_zero` | zkProof generation within [Cartesi VM](https://github.com/Modern-Society-Labs/lcore-node) |

---

## Migration Roadmap to Milestone 2
* Replace local SQLite with [Cartesi Rollups](https://github.com/Modern-Society-Labs/lcore-node) input box
* Move encryption + proof generation into RiscZero guest inside [Cartesi VM](https://github.com/Modern-Society-Labs/lcore-node)  
* Split payment / merchant / lending apps into separate containers for micro-benchmarking
* Implement fraud-proof dispute resolution system

 