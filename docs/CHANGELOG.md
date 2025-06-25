# Changelog

All notable changes to this project will be documented here following [Keep a Changelog](https://keepachangelog.com/) and [SemVer](https://semver.org/).

## [0.1.1] – 2025-06-25
### Added
* `utils.wallet_manager` now respects the `WALLETS_CSV_FILE` environment variable so a fixed wallet set can be provided in container images (e.g. `/assets/wallets.csv` on Railway).

### Changed
* When no explicit path or environment variable is provided WalletManager still falls back to `logs/wallets.csv`.

### Fixed
* Avoided permission errors by not attempting to create parent directories for absolute wallet paths (e.g. `/assets`).

## [0.1.0] – 2024-05-29
### Added
* Milestone-1 stress-test simulator with IoT pipeline.
* lcore-node MVP Rust service; Stylus contract source.
* `/health` & `/metrics` endpoints.
* Railway deployment support via Dockerfile.
* Documentation: README overhaul, milestone report, CONTRIBUTING, DEPLOYMENT, API_REFERENCE, SECURITY, ARCHITECTURE, OPERATIONS, DATASETS, CI_PIPELINE.

### Removed
* Legacy `smartcity-test/simulator/` script.
* Internal planning docs now superseded by milestone report.

### Changed
* `config/settings.py` now uses placeholder secrets only.
* Switched from standalone device sim to integrated async version.

---

© 2024 IoT-L{CORE} 