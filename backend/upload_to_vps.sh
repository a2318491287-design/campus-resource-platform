#!/bin/bash
# ============================================================
# Upload backend + frontend + resources to VPS
# Run from your laptop (in /Users/yuxianglian/Downloads/SAD_Project/)
# ============================================================
set -euo pipefail

VPS="${VPS:-root@178.157.59.239}"
REMOTE_DIR="${REMOTE_DIR:-/opt/campus_resource_platform}"

cd "$(dirname "$0")/.."   # SAD_Project root

echo "==> Creating remote directory on $VPS"
ssh "$VPS" "mkdir -p $REMOTE_DIR/backend $REMOTE_DIR/web $REMOTE_DIR/backend/storage"

echo "==> Uploading backend code..."
rsync -avz --progress \
  --exclude='__pycache__' \
  --exclude='*.pyc' \
  --exclude='.env' \
  --exclude='local.db' \
  backend/ "$VPS:$REMOTE_DIR/backend/"

echo "==> Uploading 9 course resources to backend storage..."
rsync -avz --progress \
  resources/ "$VPS:$REMOTE_DIR/backend/storage/"

echo "==> Uploading frontend HTML..."
rsync -avz --progress \
  Prototype.html "$VPS:$REMOTE_DIR/web/"

echo ""
echo "✅ Upload complete."
echo ""
echo "Next steps on the VPS:"
echo "  ssh $VPS"
echo "  cd $REMOTE_DIR/backend"
echo "  bash deploy.sh"
echo ""
echo "After deploy, configure nginx:"
echo "  cp nginx_campus.conf /etc/nginx/sites-available/campus_resource_platform"
echo "  ln -sf /etc/nginx/sites-available/campus_resource_platform /etc/nginx/sites-enabled/"
echo "  nginx -t && systemctl reload nginx"
