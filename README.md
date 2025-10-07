[![Run Main Script](https://github.com/UltimateBoi/AhAveragesPy/actions/workflows/run_main.yml/badge.svg)](https://github.com/UltimateBoi/AhAveragesPy/actions/workflows/run_main.yml)

Bad implemtation / conversion of my 2020 auction averages (which was made into a sniper). Averaging system is extremely (4 years) outdated so dont trust. Purely for example / testing currently as of 03/25

### Currently the database includes over 7200 minutes (120 hours) of finished auctions (7200 api refreshes). Currently limited to about 1 request every 5 minutes due to githubs limit on how github actions chron scheduler work (1 request every 5 minutes)

### 90 unique BIN auctions that contain a buyer as of 13:59 07/10/2025 UTC since *roughly* beginning of March 2025

## 🔐 Environment Variables & API Key Protection

This repository now uses **environment variables** to securely manage API keys and configuration. API keys and sensitive data are **never committed** to the repository.

### Quick Start for Local Development

1. Copy the environment template:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` with your configuration (the file is already in `.gitignore`)

3. Run the application:
   ```bash
   python __main__.py
   ```

### GitHub Actions (Production)

For automated runs via GitHub Actions, environment variables are securely injected using **GitHub Secrets**:

1. Go to repository **Settings** → **Secrets and variables** → **Actions**
2. Add required secrets (see `ENVIRONMENT_SETUP.md` for details)

**📖 Full Documentation:** See [ENVIRONMENT_SETUP.md](ENVIRONMENT_SETUP.md) for complete setup instructions, security best practices, and Firebase integration guide.

## Database Storage Change (Snapshots)
Raw `*.db` files are no longer committed (they grew near / over GitHub's 100 MB limit). Instead compressed SQL dumps (`database.sql.gz`, `database2.sql.gz`) are stored. CI rebuilds the actual `.db` files for GitHub Pages deployment.

Rebuild locally:
```
gzip -dc database2.sql.gz | sqlite3 database2.db
```
This yields a faithful snapshot of the state at that commit.

[Database Viewer](https://ultimateboi.github.io/AhAveragesPy/)

# Repo Views
![Views](https://count.getloli.com/get/@UltimateBoi.AhAveragesPy?theme=3d-num)
