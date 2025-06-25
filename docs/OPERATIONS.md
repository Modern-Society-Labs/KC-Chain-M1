# Operations & Runtime Handbook

---

## 1. Log Management
* Runtime metrics available via `/metrics` endpoint with JSON KPI data.
* In Railway, stdout is forwarded to the web UI; CSV files are ephemeral.
* Rotate local logs with `logrotate` or run:
  ```bash
  find logs -type f -size +50M -delete
  ```

## 2. Disk Space (SQLite)
* lcore-node stores encrypted blobs in `/data/lcore.db` (Docker volume).
* Average row size: 2 KB → 50 entries/day ≈ 100 KB.
* A 1 GB volume sustains ~10 years of data; schedule weekly backups:
  ```bash
  docker exec lcore-node sqlite3 /data/lcore.db .backup /backup/$(date +%F).db
  ```

## 3. KPI & Alerting
* `/metrics` JSON includes `success_rate`, `avg_latency_sec`, and boolean target flags.
* Example Railway alert (pseudo):
  ```yaml
  if .success_rate < 0.9 for 5m then notify_slack()
  ```

## 4. Tailing Logs in Railway
```
railway logs -s stress-test | jq '.message'
```

## 5. Backup / Restore
* **Backup:** copy `/data/lcore.db` to object storage.
* **Restore:** mount file back into container at same path, restart node.

## 6. Scaling
* CPU-bound: increase Railway plan; Python orchestration is async; Rust node is multi-threaded.
* For horizontal scaling, deploy multiple stress-test containers with unique `CONTAINER_ID` env var.

## 7. Common Issues
| Symptom | Cause | Fix |
|---------|-------|-----|
| `HTTP 502` from /device/data | lcore-node overloaded | increase `CPU` or add rate limit |
| `gas required exceeds allowance` | stylus tx too big | raise `DEFAULT_GAS_LIMIT` env |

---

© 2024 IoT-L{CORE} 