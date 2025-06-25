# Security Policy

## Supported Versions
| Version | Supported | Notes |
| ------- | --------- | ----- |
| `main`  | ✅ | Active development branch |
| `<0.1.0` tags | 🚫 | Out of scope |

---

## Threat Model Summary

| Layer | Threat | Mitigation |
|-------|--------|-----------|
| Device Auth | Fake device spamming data | Device public key whitelist (on-chain [`DeviceRegistryStylus`](https://github.com/Modern-Society-Labs/lcore-platform) from [lcore-platform](https://github.com/Modern-Society-Labs/lcore-platform) and [lcore-node](https://github.com/Modern-Society-Labs/lcore-node)) & JWT planned |
| Transport | MITM between device ↔ node | HTTPS/TLS termination in production; devnet uses localhost only |
| Encryption | Cipher downgrade / tamper | Dual‐stage AES-256-GCM ➜ ChaCha20-Poly1305 pipeline |
| Data at Rest | SQLite dump leakage | Payload is already encrypted; DB path configurable; file-system access limited inside container |
| On-Chain Commit | Replay attack | Unique `task_id` (bytes32) per submission enforced by contract |
| Secrets | Private keys leaked in repo | All sensitive material pulled from environment variables; `.env` in `.gitignore` |

---

## Responsible Disclosure

*Email:* `security@iotlcore.org`  
*PGP:* `0xBEEFDEADFEEDC0DE` (public key in `docs/pgp.pub`)

Please report vulnerabilities with:
1. Proof of concept (PoC).
2. Impact assessment.
3. Suggested fix if possible.

We respond within **48h** and coordinate advisory & patch.

---

## Development Guardrails
* `pre-commit` hooks run **ruff**, **mypy**, and secret-scan (gitleaks).  
* CI blocks merges if secrets detected.

---

## No Secrets in Repo

The project enforces a **zero-secret** policy:
* `.env` and any `*.key` files are git-ignored.
* `config/settings.py` values default to placeholders.
* CI runs `gitleaks` to prevent accidental commits.

---

© 2024 IoT-L{CORE} – MIT + Apache-2.0 dual-licensed components 