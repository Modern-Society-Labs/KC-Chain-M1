# Deployment Guide

This document covers production & local deployment paths.

---

## 1. Railway (one-click)

1. **Fork** this repo and push to your GitHub org.
2. Sign in to [Railway](https://railway.app/) → **New Project → Deploy from GitHub** → select repo.
3. When prompted, set env vars (copy from `env.example`).
4. Railway auto-detects the `Dockerfile`; the default start command is `python main.py`.
5. Health check: configure `GET /health`, port `8000`.
6. Wait for build logs → **Deploy Successful**.  Open URL → `/metrics` should return JSON KPIs.

### CLI Alternative
```bash
railway init  # inside repo root
railway env add <VAR> <VALUE>
railway up
```

---

## 2. Docker Compose (Local)

```yaml
version: "3.8"
services:
  lcore-node:
    image: rust:1.76
    build:
      context: ./smartcity-test/lcore-node
    env_file: .env
    command: cargo run --release --bin lcore-node
    ports:
      - "3000:3000"
  stress-test:
    build: .
    env_file: .env
    depends_on:
      - lcore-node
    ports:
      - "8000:8000"
```

Run with:
```bash
docker compose up --build
```

---

## 3. Kubernetes / Helm (preview)

A Helm chart lives in `deploy/helm/iot-lcore` (placeholder).  Quick install:
```bash
helm repo add lcore https://YOUR_CHART_REPO
helm install stress-test lcore/iot-lcore \ 
   --set image.tag=<git-sha> --set envSecretsRef=mysecret
```

---

## 4. Environment Variable Matrix

| Variable | Description | Example |
|---|---|---|
| `RPC_HTTP_URL` | KC-Chain RPC | `https://rpc.devnet.alchemy.com/...` |
| `LCORE_NODE_URL` | URL where Rust node listens | `http://lcore-node:3000` |
| `PRIVATE_KEY` | Funded devnet key | `0x...` |
| `MVP_IOT_PROCESSOR_ADDRESS` | Stylus contract | `0xabc…` |
| ... | ... | ... |

See full list in `env.example`. 