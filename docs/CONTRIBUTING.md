# Contributing to IoT-L{CORE}

Thanks for considering a contribution!  We follow a lightweight process designed for speed **and** traceability.

---

## 💡 Opening Issues
* Search existing issues first.
* Prefix your title with one of:
  * `BUG:` – unexpected behaviour / wrong output
  * `FEAT:` – new feature proposal
  * `DOC:` – documentation improvement
  * `CHORE:` – tests, tooling, CI
* Include reproduction steps, logs, and environment info.

## 🌳 Branch Workflow
We use **GitHub Flow** on the `main` branch:

1.  Fork → branch from `main`.
2.  Branch name format  ➜  `feat/<slug>`, `fix/<slug>`, `docs/<slug>`.
3.  Commit with [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/):
    * `feat:` – new user-facing capability
    * `fix:` – bug fix
    * `docs:` – docs only
    * `chore:` – infra / CI / refactor
4.  Push & open a Pull Request.  Draft is OK!

## ✅ PR Checklist
- [ ] Follows Conventional Commits
- [ ] Passes `make lint` and `make test`
- [ ] Updated docs / README if behaviour changes
- [ ] Added or updated unit tests where relevant
- [ ] `docker build .` succeeds

PRs auto-deploy to a Railway **preview environment**; link will appear on the PR.

## ⚙️  Local Development Quick-Start
```bash
# 1. Fork && clone
$ git clone git@github.com:YOUR_USER/kc-chain-stress-test.git && cd kc-chain-stress-test

# 2. Python env
$ python3 -m venv .venv && source .venv/bin/activate
$ pip install -r requirements.txt

# 3. Pre-commit hooks (black, flake8, ruff)
$ pip install pre-commit && pre-commit install

# 4. Make targets
$ make dev        # run api + simulator + hot reload
$ make lint       # ruff + mypy
$ make test       # pytest (TBD)
```

Happy hacking! 🎉 