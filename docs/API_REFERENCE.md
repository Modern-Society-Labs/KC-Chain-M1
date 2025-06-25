# lcore-node MVP API Reference

This reference covers the REST endpoints consumed by the stress-test simulator.  The node listens on the base URL defined by `$LCORE_NODE_URL` (default `http://127.0.0.1:3000`).

---

## OpenAPI / Swagger

Download the live **OpenAPI 3.0** JSON:
```bash
curl $LCORE_NODE_URL/openapi.json > api.json
```
Visualise with [ReDoc](https://redocly.github.io/redoc/) locally:
```bash
npx redoc-cli serve api.json
```
(If `/openapi.json` is not enabled, use the manual specs below.)

---

## 1. `POST /device/register`
Register a device so it can submit data.

### Request Body
```json
{
  "device_id": "EV_1234",
  "public_key": "abcd…"   // optional, hex-encoded
}
```

### Response `200 OK`
```json
{
  "success": true,
  "device_id": "EV_1234"
}
```

### Curl
```bash
curl -X POST $LCORE_NODE_URL/device/register \
  -H 'Content-Type: application/json' \
  -d '{ "device_id": "demo_001" }'
```

---

## 2. `POST /device/data`
Submit encrypted sensor payload.

### Request Body
```json
{
  "device_id": "EV_1234",
  "data": "{...JSON payload...}",
  "timestamp": 1717098458
}
```

### Response `200 OK`
```json
{
  "success": true,
  "tx": "0x1abc…def"
}
```

### Curl
```bash
curl -X POST $LCORE_NODE_URL/device/data \
  -H 'Content-Type: application/json' \
  -d '{ "device_id": "demo_001", "data": "{\"speed\":42}", "timestamp": 1717098458 }'
```

---

## 3. `GET /status`
Health + version info.

### Response
```json
{
  "status": "ok",
  "version": "0.1.0",
  "chain_id": "1205614515668104"
}
```

---

## 4. Stress-Test Container Endpoints (Python)

| Method | Path | Purpose |
|---|---|---|
| GET | `/health` | Liveness probe, returns `{ "status": "ok" }` |
| GET | `/metrics` | JSON snapshot of KPI counters |

These are served by `server.py` inside the stress-test container (Flask). 