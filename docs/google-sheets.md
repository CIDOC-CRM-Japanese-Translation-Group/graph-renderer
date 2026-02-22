# Google Sheets フォーマット

エディタ上部の「Google Sheets から生成」チェックボックスを使うと、スプレッドシートの TSV を読み込んで DSL を自動生成できます。

## スプレッドシートの列構成

| 列 | ヘッダー | 内容 | 例 |
|---|---|---|---|
| A | Subject Class | 主語のクラス名 | `E22 Human-Made Object` |
| B | Subject Label | 主語のインスタンス名 | `Vase v123` |
| C | Property | プロパティ名（括弧付き逆名も可） | `P1 is identified by (identifies)` |
| D | .1 Type | P…1 修飾用（省略可） | |
| E | Object Class | 目的語のクラス名 | `E42 Identifier` |
| F | Object Label | 目的語のインスタンス名 | `v123` |

1行目はヘッダーとして扱われ、スキップされます。A・B・C・E・F のいずれかが空の行もスキップされます。

## URL の取得方法

Google スプレッドシートを「ウェブに公開」し、フォーマットを **TSV** に指定して URL を取得します。

1. スプレッドシートを開く
2. ファイル → 共有 → ウェブに公開
3. 「タブ区切り値 (.tsv)」を選択して「公開」
4. 表示された URL をエディタの入力欄に貼り付ける

URL の末尾は `?output=tsv` になります。

## 変換ルール

- 各行が1つのトリプル（主語 → プロパティ → 目的語）に対応します
- **ノード ID** は `クラスコード_連番` で自動採番されます（例: `E22_1`、`E42_1`）
- 同じ（クラス名、インスタンス名）の組み合わせは1つのノードに集約されます
- プロパティ名末尾の `(逆名)` 部分は除去されます（例: `P1 is identified by (identifies)` → `P1 is identified by`）

## 生成される DSL の例

入力スプレッドシート：

| Subject Class | Subject Label | Property | .1 Type | Object Class | Object Label |
|---|---|---|---|---|---|
| E22 Human-Made Object | Vase v123 | P1 is identified by (identifies) | | E42 Identifier | v123 |
| E22 Human-Made Object | Vase v123 | P2 has type (is type of) | | E55 Type | Vase |

生成される DSL：

```
crm {
E22_1 "E22 Human-Made Object | Vase v123"
E42_1 "E42 Identifier | v123"
E55_1 "E55 Type | Vase"
E22_1 -> E42_1 : P1 is identified by
E22_1 -> E55_1 : P2 has type
}
```
