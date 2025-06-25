# `lcore-node-mvp`

This repository contains the backend service for the IoT-L{CORE} MVP. It's a Rust application built with Axum that serves as the central hub for IoT device data.

Its primary responsibilities are:
1.  **Receiving** data from IoT devices.
2.  **Encrypting** the data using a dual-encryption scheme.
3.  **Storing** the encrypted data locally in a SQLite database.
4.  **Committing** a record of the data submission to the KC-Chain (an Arbitrum Orbit devnet) via a Stylus smart contract.

This service is the core component that bridges off-chain device data with on-chain verifiable commitments.

## Architecture

The MVP architecture is streamlined to validate the core pipeline:

```mermaid
graph TD
    subgraph "Device Layer"
        CURL[CLI / Simulated Device]
    end

    subgraph "lcore-node-mvp (This Service)"
        API[Axum REST API<br/>/device/register<br/>/device/data]
        ENC[Dual Encryption Service<br/>AES-256-GCM + ChaCha20-Poly1305]
        DB[SQLite Database<br/>(storage.db)]
        KCC[KC-Chain Client<br/>(ethers-rs)]
    end

    subgraph "On-Chain Layer (KC-Chain)"
        CONTRACT[MVPIoTProcessor<br/>Stylus Contract]
    end

    CURL -->|1. POST /device/data| API
    API -->|2. Encrypts Payload| ENC
    API -->|3. Stores Encrypted Data| DB
    API -->|4. Submits Tx| KCC
    KCC -->|5. `submit_result()`| CONTRACT
```

## Features

-   **`/device/register`**: Registers a new device, storing its ID in the local database.
-   **`/device/data`**: The main endpoint for data submission. It takes device data, performs dual encryption, stores it, and sends a transaction to the `MVPIoTProcessor` contract.
-   **`/status`**: A simple health-check endpoint.
-   **Dual Encryption**: A two-stage encryption process ensures data is protected both at rest and during processing.
-   **Local Storage**: Uses SQLite for a lightweight, persistent local data store.
-   **KC-Chain Integration**: Communicates with an Arbitrum Orbit chain to create an immutable, on-chain record of data submission.

## Getting Started

### Prerequisites
- Rust and Cargo (`rustup.rs`)
- A funded wallet on the KC-Chain devnet.

### Configuration

1.  **Copy the config template**:
    ```bash
    cp config.template.toml config.toml
    ```
2.  **Edit `config.toml`**:
    -   `rpc_url`: Your KC-Chain RPC endpoint (e.g., from Alchemy).
    -   `private_key`: The private key of the wallet you will use to send transactions. **(Ensure this wallet is funded with ETH on the KC-Chain devnet)**.
    -   `mvp_processor`: The address of the deployed `MVPIoTProcessor` contract (`0xd99061c28b9063d9651fea67930fc4ff598ba5b2`).

### Build & Run

From the `lcore-node-mvp` directory:

```bash
# Install dependencies, build, and run the server
cargo run --release
```
The server will start and listen on `127.0.0.1:3000`.

## Testing the MVP

Once the server is running, you can test the end-to-end flow.

### Step 1: Register a Device

```bash
curl -X POST http://127.0.0.1:3000/device/register \
     -H 'Content-Type: application/json' \
     -d '{"device_id":"device_001"}'
```
Expected response: `{"success":true,"message":"Device registered"}`

### Step 2: Submit Device Data

```bash
curl -X POST http://127.0.0.1:3000/device/data \
     -H 'Content-Type: application/json' \
     -d '{"device_id":"device_001","data":"{\"temperature\":25.5,\"humidity\":60.1}","timestamp":1718576400}'
```
Expected response: `{"success":true,"message":"Data submitted; tx 0x..."}`
This confirms the data was encrypted, stored locally, and the transaction was successfully mined on KC-Chain.

### Step 3: Verify On-Chain Data

You can verify the result on-chain using `foundry cast`. The `task_id` is derived from the submitted data. For the command above, the `task_id` is `0x03c8deb30d8d0d830ba20cb607786f2b31310eff52408aca9a7a5adb08f791cd`.

```bash
# Replace <CONTRACT_ADDRESS> with your deployed address if different
cast call 0xd99061c28b9063d9651fea67930fc4ff598ba5b2 \
  "get_result(bytes32)" \
  0x03c8deb30d8d0d830ba20cb607786f2b31310eff52408aca9a7a5adb08f791cd \
  --rpc-url <YOUR_KC_CHAIN_RPC_URL>
```
This will return the tuple `(bytes encryptedResult, bytes32 proofHash, uint256 ts, address submitter)` stored in the contract.

## Future Upgrades

- **Add Rate Limiting**: Implement middleware to prevent abuse of the API endpoints.
- **Enhanced Encryption**: Integrate the dual-encryption process with a deterministic execution environment like the Cartesi VM.
- **Real Proof Hashes**: Replace the placeholder proof hash with actual proofs from a system like RiscZero.
- **Full Device SDK Integration**: Replace `curl` simulations with actual data streams from devices running the `lcore-device-sdk`. 