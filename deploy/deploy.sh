#!/bin/bash
# deploy.sh - graph-renderer 初回セットアップ
# サーバ上で sudo 権限のあるユーザとして実行すること

set -e

REPO_DIR="/var/www/html/projects/cidoc/graph-renderer"
DEPLOY_DIR="$REPO_DIR/deploy"

echo "=== 1. Python 依存パッケージのインストール ==="
pip3 install -r "$REPO_DIR/server/requirements.txt"

echo "=== 2. フロントエンドのビルド ==="
cd "$REPO_DIR/frontend"
npm ci
npm run build

echo "=== 3. systemd サービスの登録 ==="
sudo cp "$DEPLOY_DIR/crmviz-api.service" /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable crmviz-api
sudo systemctl start crmviz-api
sudo systemctl status crmviz-api

echo "=== 4. nginx の設定 ==="
sudo cp "$DEPLOY_DIR/nginx-graph-renderer.conf" /etc/nginx/snippets/graph-renderer.conf
echo "snippet を配置しました: /etc/nginx/snippets/graph-renderer.conf"
echo ""
echo "既存の server ブロック（sites-enabled/default）に以下を追記してください:"
echo "  include /etc/nginx/snippets/graph-renderer.conf;"
echo ""
echo "追記後:"
echo "  sudo nginx -t && sudo systemctl reload nginx"

echo ""
echo "=== 完了 ==="
echo "フロントエンド: https://ik1-313-16672.vs.sakura.ne.jp/graph-renderer/"
echo "バックエンド:   https://ik1-313-16672.vs.sakura.ne.jp/crmviz-api/"
