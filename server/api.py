# api.py
from __future__ import annotations

from typing import Any, Dict, List

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel

from graphviz import Source

# 既存の変換ロジックをインポート
# - graph_to_pptx.py: graph_json_to_pptx(graph: dict, output_path: str) or bytes を返す関数がある想定
# - dsl_to_graphviz_svg.py: parse_dsl(), graph_to_dot() がある想定
from dsl_to_graphviz_svg import parse_dsl, graph_to_dot


# ===================== Pydantic モデル =====================

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
