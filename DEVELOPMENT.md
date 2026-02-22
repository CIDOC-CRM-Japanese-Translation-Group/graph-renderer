# 開発メモ

## 設計判断の記録

### PPTX エクスポートの削除（2026-02-22）

PowerPoint (.pptx) への出力機能を削除した。

**理由**:
ELK によるグラフレイアウト結果（ノードの座標・サイズ）を python-pptx でスライドに配置する実装を試みたが、
フォントサイズ・余白・コネクタの経路など細部のレイアウト調整が困難で、
実用的な品質に仕上げるコストが高すぎると判断した。

**削除したもの**:
- `frontend/src/App.svelte` — `downloadPptx()` 関数と PPTX ボタン
- `server/api.py` — `/api/pptx` エンドポイントと関連ヘルパー
- `server/graph_to_pptx.py` — 変換ロジック本体
- `server/sample.json` — テスト用サンプルデータ

コードは git 履歴から復元可能。
