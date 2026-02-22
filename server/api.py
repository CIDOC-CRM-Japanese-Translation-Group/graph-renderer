# api.py
from __future__ import annotations

import io
from typing import Any, Dict, List

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response, StreamingResponse
from pydantic import BaseModel

from graphviz import Source

# 既存の変換ロジックをインポート
# - graph_to_pptx.py: graph_json_to_pptx(graph: dict, output_path: str) or bytes を返す関数がある想定
# - dsl_to_graphviz_svg.py: parse_dsl(), graph_to_dot() がある想定
from graph_to_pptx import graph_json_to_pptx
from dsl_to_graphviz_svg import parse_dsl, graph_to_dot


# ===================== Pydantic モデル =====================

class GraphModel(BaseModel):
    """
    Svelte 側の laidOut をそのまま突っ込めるように
    nodes / edges を「なんでも dict」にしておく。
    """
    nodes: List[Dict[str, Any]]
    edges: List[Dict[str, Any]]


class GraphvizRequest(BaseModel):
    """
    DSL テキストをそのまま送る用のペイロード。
    """
    dsl: str


# ===================== FastAPI 本体 =====================

app = FastAPI(title="CIDOC CRM Viz API", root_path="/crmviz-api")

# CORS（Svelte のホストを origin に入れるとよい）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 必要に応じて絞ってください
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ===================== ヘルパー: pptx 変換 =====================

def make_pptx_bytes(graph: Dict[str, Any]) -> bytes:
    """
    既存の graph_json_to_pptx() を使って PPTX バイト列を返すヘルパー。

    graph_to_pptx.py 側の実装に応じて、ここだけ調整してください。
    - パターンA: graph_json_to_pptx(graph, output_path) のように「ファイルに保存」する関数なら
      一時ファイルを作ってそこに保存→読み込み→bytes 返す。
    - パターンB: graph_json_to_pptx(graph) が bytes を返す実装にしてしまうなら、
      そのまま返す。
    """
    # ---- パターンA: ファイルパスを渡す実装の場合 ----
    import tempfile
    from pathlib import Path

    with tempfile.TemporaryDirectory() as tmpdir:
        out_path = Path(tmpdir) / "graph.pptx"
        # ここはあなたの graph_to_pptx.py のシグネチャに合わせてください
        # 例: graph_json_to_pptx(graph, str(out_path))
        graph_json_to_pptx(graph, str(out_path))

        data = out_path.read_bytes()
        return data

    # ---- パターンB: bytes を返す実装なら ----
    # return graph_json_to_pptx(graph)


# ===================== ヘルパー: Graphviz SVG 変換 =====================

def dsl_to_svg_bytes(dsl: str) -> bytes:
    """
    DSL テキスト → parse_dsl() → graph_to_dot() → Graphviz SVG の bytes を返す。
    """
    graph = parse_dsl(dsl)
    dot = graph_to_dot(graph)

    src = Source(dot)
    svg_bytes: bytes = src.pipe(format="svg")
    return svg_bytes


# ===================== エンドポイント =====================

@app.post("/api/pptx")
def api_generate_pptx(graph: GraphModel):
    """
    laidOut graph JSON → PowerPoint (pptx)

    リクエスト:
      POST /api/pptx
      Content-Type: application/json

      {
        "nodes": [...],
        "edges": [...]
      }

    レスポンス:
      Content-Type: application/vnd.openxmlformats-officedocument.presentationml.presentation
      (添付ファイルとしてダウンロード)
    """
    try:
        pptx_bytes = make_pptx_bytes(graph.dict())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PPTX生成中にエラー: {e}")

    # ストリーミングレスポンスで返す
    filename = "cidoc-graph.pptx"
    return StreamingResponse(
        io.BytesIO(pptx_bytes),
        media_type=(
            "application/vnd.openxmlformats-officedocument."
            "presentationml.presentation"
        ),
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"'
        },
    )

@app.post("/api/graphviz/png")
def api_graphviz_png(req: GraphvizRequest):
    try:
        graph = parse_dsl(req.dsl)
        dot = graph_to_dot(graph)
        src = Source(dot)
        png_bytes: bytes = src.pipe(format="png")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Graphviz PNG 生成中にエラー: {e}")

    return Response(content=png_bytes, media_type="image/png")

@app.post("/api/graphviz/svg")
def api_graphviz_svg(req: GraphvizRequest):
    """
    DSL → Graphviz SVG

    リクエスト:
      POST /api/graphviz/svg
      Content-Type: application/json

      { "dsl": "crm { ... }" }

    レスポンス:
      Content-Type: image/svg+xml
      SVG のバイト列
    """
    try:
        svg_bytes = dsl_to_svg_bytes(req.dsl)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Graphviz生成中にエラー: {e}")

    return Response(content=svg_bytes, media_type="image/svg+xml")
