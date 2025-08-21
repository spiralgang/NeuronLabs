# Cloud Librarian Bot Engine 

This project implements an autonomous cloudspace engine that integrates OneDrive (via rclone) with an always-on librarian bot service for organizing and indexing code libraries. It provides a Flask-based API, Telegram integration, and utility scripts for managing code storage in a containerized environment using Docker and Docker Compose. 

## Features
- **Flask API**: Handles file upload, retrieval, and command processing.
- **rclone Integration**: Mounts OneDrive for cloud storage.
- **Telegram Bot**: Offers remote command control via Telegram.
- **Utility Scripts**: Automatically scans and indexes your code library.
- **Containerization**: Dockerized service for consistent and scalable deployment. 

## Directory Structure
```
cloud-librarian/
├── Dockerfile
├── docker-compose.yml
├── entrypoint.sh
├── requirements.txt
├── bot_engine.py
├── telegram_bot.py          # Optional: Telegram interface integration
├── README.md
├── docs/
│   ├── architecture.md      # Detailed architecture explanation
│   └── design_mindmap.png   # Visual mind map image file
├── config/
│   └── rclone.conf          # rclone configuration file (if not using host mount)
└── scripts/
    └── util_scan_and_index.py  # Utility script for scanning and indexing code files
``` 

## Setup Instructions
1. **rclone configuration**: Update `config/rclone.conf` with your OneDrive settings, or mount your host configuration.
2. **Build and run with Docker Compose**: `docker-compose up -d`
3. **Telegram Bot** (optional): Set your `TELEGRAM_TOKEN` environment variable and enable the Telegram integration.

## API Endpoints
- `POST /engine` - Main command processing endpoint
- `GET /health` - Health check endpoint
- `POST /organize` - Organize code snippets
- `GET /search` - Search indexed code library

## Commands
- `organize` - Organize and index new code snippets
- `search` - Search through indexed code
- `backup` - Create backups of library
- `sync` - Synchronize with OneDrive

## Environment Variables
- `TELEGRAM_TOKEN` - Telegram bot token (optional)
- `LIBRARY_MOUNT` - Path to library mount point (default: /onedrive/library)
- `RCLONE_REMOTE` - rclone remote name (default: onedrive)

## Usage
Once deployed, the bot engine runs continuously and can receive commands via:
1. HTTP API calls to `/engine` endpoint
2. Telegram bot commands (if configured)
3. Scheduled tasks and automation scripts

This bot provides "plug and play" automation for repetitive code library management tasks.