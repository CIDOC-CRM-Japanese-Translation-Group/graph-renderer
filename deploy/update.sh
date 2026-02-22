#!/bin/bash
# update.sh - GitHub から最新を取得してデプロイを更新する

set -e

REPO_DIR="/var/www/html/projects/cidoc/graph-renderer"

echo "=== 1. git pull ==="
cd "$REPO_DIR"
git pull origin main

echo "=== 2. Python 依存パッケージの更新 ==="
pip3 install -r "$REPO_DIR/server/requirements.txt"

echo "=== 3. フロントエンドの再ビルド ==="
cd "$REPO_DIR/frontend"
npm ci
npm run build

echo "=== 4. バックエンドの再起動 ==="
sudo systemctl restart crmviz-api
sudo systemctl status crmviz-api --no-pager

echo ""
echo "=== 更新完了 ==="
