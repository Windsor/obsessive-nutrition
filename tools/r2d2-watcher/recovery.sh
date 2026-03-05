#!/bin/bash
# r2d2 Recovery Script — run after server comes back online
# Verifies all services, restarts any that are down, runs health check

set -e

SERVER="192.168.68.139"
USER="windsor1337"
PASS="Smurf1337!"
SSH="sshpass -p '$PASS' ssh -o StrictHostKeyChecking=no -o ConnectTimeout=10 $USER@$SERVER"

echo "=== r2d2 Recovery Check — $(date) ==="

# Step 1: Verify SSH connectivity
echo -e "\n[1/6] Testing SSH..."
if ! eval $SSH "echo 'SSH OK'" 2>/dev/null; then
    echo "❌ SSH still unreachable. Server not recovered."
    exit 1
fi
echo "✅ SSH connected"

# Step 2: System info
echo -e "\n[2/6] System status..."
eval $SSH "uptime; echo '---'; free -h | head -2; echo '---'; df -h / | tail -1"

# Step 3: Check and restart systemd services
echo -e "\n[3/6] Checking systemd services..."
SERVICES="project-tracker quiz-generator social-poster"
for svc in $SERVICES; do
    status=$(eval $SSH "systemctl is-active $svc 2>/dev/null" || echo "inactive")
    if [ "$status" = "active" ]; then
        echo "  ✅ $svc: active"
    else
        echo "  ⚠️ $svc: $status — restarting..."
        eval $SSH "sudo systemctl restart $svc"
        sleep 2
        new_status=$(eval $SSH "systemctl is-active $svc 2>/dev/null" || echo "failed")
        echo "  → $svc: $new_status"
    fi
done

# Step 4: Check Ghost services
echo -e "\n[4/6] Checking Ghost services..."
GHOST_DIRS="/var/www/ghost-portugal /var/www/ghost-finance"
for dir in $GHOST_DIRS; do
    name=$(basename $dir)
    status=$(eval $SSH "cd $dir && ghost status 2>/dev/null | grep -o 'running\|stopped'" || echo "unknown")
    if [ "$status" = "running" ]; then
        echo "  ✅ $name: running"
    else
        echo "  ⚠️ $name: $status — starting..."
        eval $SSH "cd $dir && ghost start"
        sleep 3
        echo "  → $name started"
    fi
done

# Step 5: HTTP health checks
echo -e "\n[5/6] HTTP health checks..."
ENDPOINTS=(
    "Ghost PT|http://$SERVER:2368"
    "Ghost Finance|http://$SERVER:2370"
    "Project Tracker|http://$SERVER:3001"
    "Quiz Generator|http://$SERVER:5000"
    "Social Poster|http://$SERVER:5555"
)
for entry in "${ENDPOINTS[@]}"; do
    name="${entry%%|*}"
    url="${entry##*|}"
    code=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 "$url" 2>/dev/null || echo "000")
    if [ "$code" -ge 200 ] && [ "$code" -lt 400 ]; then
        echo "  ✅ $name: HTTP $code"
    else
        echo "  ❌ $name: HTTP $code"
    fi
done

# Step 6: Check Docker containers
echo -e "\n[6/6] Docker containers..."
eval $SSH "docker ps --format 'table {{.Names}}\t{{.Status}}' 2>/dev/null | head -15"

echo -e "\n=== Recovery check complete ==="
