# Project Brief: IoT-L{CORE} SDK

## 1. Mission

To develop a decentralized IoT data infrastructure on Arbitrum that enables secure, private, and verifiable data processing. The project bridges real-world IoT data with on-chain applications by replacing traditional oracle-based systems with a trust-minimized, deterministic architecture using **Cartesi** for verifiable computation and **RiscZero** for zero-knowledge proofs.

The core mission is to convert an existing IoT data platform (W3bstream) into a new, open-source SDK that runs on an **Arbitrum Orbit Chain (KC-Chain)**, providing developers with the tools to build privacy-preserving, real-world applications.

## 2. Core Requirements

### Functional
- **Device Authentication**: Securely verify IoT devices using decentralized identifiers (W3C DID) and signed messages (IETF JOSE).
- **Privacy-Preserving Computation**: Process sensitive IoT data within a secure Cartesi VM environment, ensuring no raw data is exposed on-chain.
- **Verifiable Execution**: Generate RiscZero proofs to cryptographically guarantee the integrity of all computations.
- **On-Chain Settlement**: Store verifiable computation results on the Arbitrum Orbit chain for dApp consumption.

### Technical
- **Blockchain**: Arbitrum Orbit (KC-Chain - ID `1205614515668104`)
- **Compute Layer**: Cartesi Machine VM for deterministic Linux environment.
- **Proof System**: RiscZero for ZK proofs of computation.
- **Device SDK**: `lcore-device-sdk` (C/C++) for embedded device integration.
- **Node**: `lcore-node` (Rust) for processing and dual-encryption.
- **Smart Contracts**: `lcore-platform` (Solidity/TypeScript) for on-chain logic and settlement.

## 3. Strategic Approach: MVP-First

The project follows a phased implementation strategy to manage complexity and validate core concepts early.

- **Phase 1: MVP Implementation (Current)**
  - Build a standalone **dual encryption** system to prove the core privacy-preserving pattern.
  - Use a standard REST API and a local SQLite database.
  - Generate RiscZero proofs in a non-deterministic environment as a baseline.
  - This allows for rapid validation with real IoT devices using the `lcore-device-sdk`.

- **Phase 2: Full Cartesi Integration (Next)**
  - Migrate the MVP's encryption and data processing logic into the **Cartesi Machine**.
  - This transitions the system to a fully **deterministic and verifiable** architecture.
  - Replace direct database access with Cartesi rollups APIs (HTTP/GraphQL).
  - The final architecture provides fraud-proof guarantees for all IoT data processing.

## 4. Scope

### In Scope
- Adapting the `lcore-device-sdk` for the target architecture.
- Building the `lcore-node` to handle data ingestion, encryption, and Cartesi integration.
- Deploying Stylus smart contracts on the KC-Chain for results settlement.
- A timer service to trigger automated, autonomous queries.

### Out of Scope
- A graphical user interface (GUI).
- Support for ZK frameworks other than RiscZero.
- Complex multi-node clustering as seen in the original W3bstream.
- Compatibility with the original IoTeX ecosystem.

## 5. Success Metrics
- **Developer Adoption**: 2-3 external development teams integrate the SDK within 18 months.
- **Privacy & Security**: Zero raw data exposure is confirmed through audits and testing.
- **Performance**: On-chain data finalization takes less than 10 seconds.
- **Real-World Validation**: At least two pilot demonstrations are successfully deployed in a community setting. 