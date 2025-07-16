# Secrets Directory

This directory contains sensitive configuration files for production deployment.

## Required Files:

- `telegram_bot_token.txt` - Telegram Bot Token from @BotFather
- `updates_channel_id.txt` - Channel ID for updates (e.g., -1001234567890)
- `full_channel_id.txt` - Channel ID for full reports (e.g., -1001234567891)

## Security:

- All `.txt` files in this directory are ignored by git
- Files should have 600 permissions (owner read/write only)
- Created automatically by deployment scripts

## Usage:

These files are created automatically when running:
- `./deploy-vps.sh`
- `./deploy-prod.sh`

The deployment scripts will prompt for the required values and create these files with proper permissions.
