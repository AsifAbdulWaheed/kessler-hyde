# Kessler & Hyde — Deployment Guide

## Requirements
- Python 3.10+
- PostgreSQL database
- Linux server (Ubuntu recommended)
- Brevo account (for transactional emails)

## Step 1 — Server Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install python3 python3-pip python3-venv postgresql nginx -y
```

## Step 2 — Project Setup

```bash
# Clone your project
git clone <your-repo-url> /var/www/kessler-hyde
cd /var/www/kessler-hyde

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Step 3 — Environment Variables

Create `/var/www/kessler-hyde/.env`: