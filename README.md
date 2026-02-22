# graph-renderer

CIDOC-CRM グラフを DSL で記述し、ブラウザ上でレイアウト・表示するツールです。

- **frontend/** — Svelte + Vite 製の SPA。ELK によるグラフレイアウト、SVG / draw.io XML のエクスポート
- **server/** — FastAPI 製のバックエンド。Graphviz による SVG/PNG 出力、PPTX 生成

---

## 動作環境

| 項目 | バージョン |
|---|---|
| Node.js | 18 以上 |
| npm | 9 以上 |
| Python | 3.10 以上 |
| nginx | 任意（静的配信 + リバースプロキシ） |

---

## セットアップ（初回）

### 1. リポジトリの取得

```bash
cd /var/www/html/projects/cidoc
git clone https://github.com/CIDOC-CRM-Japanese-Translation-Group/graph-renderer.git
cd graph-renderer
```

### 2. deploy.sh の実行

```bash
bash deploy/deploy.sh
```

以下が自動で行われます：

- Python 依存パッケージのインストール（`server/requirements.txt`）
- フロントエンドのビルド（`frontend/dist/` が生成されます）
- systemd サービス `crmviz-api` の登録・起動

### 3. nginx の設定

既存の `server` ブロックに以下を追記します。

```nginx
location /graph-renderer/ {
    alias /var/www/html/projects/cidoc/graph-renderer/frontend/dist/;
    index index.html;
    try_files $uri $uri/ =404;
}
```

設定ファイルのテストと反映：

```bash
sudo nginx -t && sudo systemctl reload nginx
```

> `/crmviz-api/` のプロキシ設定（ポート 8001）は既に nginx に設定済みであれば不要です。
> 未設定の場合は `deploy/nginx-graph-renderer.conf` のコメントを参照してください。

---

## アクセス

| 項目 | URL |
|---|---|
| フロントエンド | `https://<hostname>/graph-renderer/` |
| バックエンド API | `https://<hostname>/crmviz-api/` |

---

## 更新（2回目以降）

サーバにログインして `update.sh` を実行します。

```bash
ssh <server>
cd /var/www/html/projects/cidoc/graph-renderer
bash deploy/update.sh
```

以下が順に実行されます：

1. `git pull origin main`
2. Python パッケージの更新
3. フロントエンドの再ビルド
4. `crmviz-api` サービスの再起動

---

## ローカル開発

### フロントエンド

```bash
cd frontend
npm install
npm run dev
```

`http://localhost:5173` で開発サーバが起動します。

### バックエンド

```bash
cd server
pip install -r requirements.txt
uvicorn api:app --reload --port 8001
```

`http://localhost:8001` で FastAPI が起動します。フロントエンドの `API_BASE` がローカルを向いていない場合は `frontend/src/App.svelte` の `API_BASE` を書き換えてください。

---

## FAQ

### Graphviz 出力で日本語が文字化けする

サーバに日本語フォントが入っていない場合に発生します。以下でインストールしてください。

```bash
sudo apt-get install -y fonts-noto-cjk
fc-cache -fv
sudo systemctl restart crmviz-api
```

---

## ファイル構成

```
graph-renderer/
├── frontend/          # Svelte フロントエンド
│   ├── src/
│   │   ├── App.svelte
│   │   ├── Canvas.svelte
│   │   ├── Editor.svelte
│   │   ├── Label.svelte
│   │   └── lib/
│   │       ├── exportDrawio.ts
│   │       ├── layoutElk.ts
│   │       ├── parseDsl.ts
│   │       └── types.ts
│   ├── package.json
│   └── vite.config.ts
├── server/            # FastAPI バックエンド
│   ├── api.py
│   ├── dsl_to_graphviz_svg.py
│   └── requirements.txt
└── deploy/            # デプロイ用スクリプト・設定
    ├── deploy.sh
    ├── update.sh
    ├── crmviz-api.service
    └── nginx-graph-renderer.conf
```
