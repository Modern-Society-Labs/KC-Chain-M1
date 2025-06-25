# Continuous Integration / Deployment Pipeline

All automation lives in `.github/workflows/`.

---

## 1. `ci.yml`
Runs on every `push` + PR:
1. **Setup Python** (`3.11`) & cache `pip`.
2. `ruff --select all` lint.
3. `mypy` type-check (coming soon).
4. Build Docker image (`docker build .`).
5. Run smoke test: `python -m compileall -q .` inside the image.

> Fails the build on any linter / compile error.

## 2. `deploy-railway.yml`
Triggered on merge to `main`:
1. Re-use Docker build cache.
2. Authenticate with Railway using `RAILWAY_TOKEN` secret.
3. `railway up --service stress-test` to deploy latest image.
4. Post deployment URL as a PR comment.

---

## Secrets & Variables
| Name | Used By | Set In |
|------|---------|--------|
| `RAILWAY_TOKEN` | deploy workflow | GitHub → repo secrets |
| `RPC_HTTP_URL` etc. | Runtime | Railway env panel |

---

## Local Lint & Test
Developers can replicate CI locally:
```bash
make lint test docker-build
```

---

Future enhancements:
* **pytest** unit & integration tests.
* **gitleaks** secret scanner step.
* Push image to GitHub Container Registry for versioned tags. 