#!/bin/bash
# Deploy pending changes to r2d2 after recovery
# Run this after recovery.sh confirms all services are up

set -e

SERVER="192.168.68.139"
USER="windsor1337"
PASS="Smurf1337!"
SSH="sshpass -p '$PASS' ssh -o StrictHostKeyChecking=no -o ConnectTimeout=10 $USER@$SERVER"
SCP="sshpass -p '$PASS' scp -o StrictHostKeyChecking=no"
WORKSPACE="/Users/jarvis/.openclaw/workspace"

echo "=== Deploy Pending Changes — $(date) ==="

# 1. Deploy Reddit module to social poster
echo -e "\n[1] Deploying Reddit cross-posting module..."
eval $SCP "$WORKSPACE/tools/social-poster/posters/reddit.py" "$USER@$SERVER:/home/windsor1337/social-poster/posters/reddit.py"
echo "  ✅ reddit.py deployed"

# Check if PRAW is installed
if ! eval $SSH "pip3 show praw 2>/dev/null | grep -q Version"; then
    echo "  Installing praw..."
    eval $SSH "pip3 install praw"
fi
echo "  ✅ PRAW dependency checked"

# 2. Restart social poster to pick up changes
echo -e "\n[2] Restarting social-poster..."
eval $SSH "sudo systemctl restart social-poster"
sleep 2
status=$(eval $SSH "systemctl is-active social-poster" || echo "failed")
echo "  Social poster: $status"

# 3. Run offsite backup
echo -e "\n[3] Running offsite backups..."
BACKUP_DIR="$WORKSPACE/backups/$(date +%Y-%m-%d)"
mkdir -p "$BACKUP_DIR"

# Ghost PT
eval $SSH "cd /var/www/ghost-portugal && ghost backup" 2>/dev/null
eval $SCP "$USER@$SERVER:/var/www/ghost-portugal/backup-*.json" "$BACKUP_DIR/" 2>/dev/null && echo "  ✅ Ghost PT backup" || echo "  ⚠️ Ghost PT backup skipped"

# Ghost Finance  
eval $SSH "cd /var/www/ghost-finance && ghost backup" 2>/dev/null
eval $SCP "$USER@$SERVER:/var/www/ghost-finance/backup-*.json" "$BACKUP_DIR/" 2>/dev/null && echo "  ✅ Ghost Finance backup" || echo "  ⚠️ Ghost Finance backup skipped"

# Project Tracker DB
eval $SCP "$USER@$SERVER:/home/windsor1337/project-tracker/db/tracker.db" "$BACKUP_DIR/tracker.db" 2>/dev/null && echo "  ✅ Project Tracker DB" || echo "  ⚠️ Tracker DB skipped"

echo -e "\n=== Deployment complete ==="
