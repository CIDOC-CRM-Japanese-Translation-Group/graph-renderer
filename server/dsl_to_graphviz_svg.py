#!/usr/bin/env python
"""
dsl_to_graphviz_svg.py

CIDOC風 DSL を Graphviz で可視化する:
- 入力: DSL テキスト
- 出力: SVG（デフォルト）または DOT

例: input.dsl

crm {
E22 "E22 Human-Made Object | Vase 123"
E42 "E42 Identifier | 123"
E55 "E55 Type | Vase"
E22 -> E42 : P1 is identified by
E22 -> E55 : P2 has type
}
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import List, Dict, Any

try:
    from graphviz import Source
except ImportError:
    Source = None


# ===== DSL パーサ =====

node_re = re.compile(r'^\s*([A-Za-z0-9_:-]+)\s+"([^"]*)"\s*$')
edge_re = re.compile(r'^\s*([A-Za-z0-9_:-]+)\s*->\s*([A-Za-z0-9_:-]+)\s*:\s*(.+)\s*$')


def parse_dsl(src: str) -> Dict[str, Any]:
    """
    - ノード行: ID "ラベル | 値"
    - エッジ行: A -> B : ラベル
    それ以外（crm {, } など）は無視。
    """
    nodes: List[Dict[str, str]] = []
    edges: List[Dict[str, str]] = []

    for line in src.splitlines():
        m_node = node_re.match(line)
        if m_node:
            node_id, txt = m_node.groups()
            top, sep, bottom = txt.partition("|")
            top = top.strip()
            bottom = bottom.strip() if sep else ""
            nodes.append({"id": node_id, "top": top, "bottom": bottom})
            continue

        m_edge = edge_re.match(line)
        if m_edge:
            from_id, to_id, label = m_edge.groups()
            label = label.strip()
            edges.append(
                {
                    "id": f"{from_id}-{to_id}-{label}",
                    "from": from_id,
                    "to": to_id,
                    "label": label,
                }
            )
            continue

    return {"nodes": nodes, "edges": edges}


# ===== DOT 生成 =====

def html_escape(s: str) -> str:
    """HTML ラベル用の簡易エスケープ。"""
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )

def graph_to_dot(graph: Dict[str, Any]) -> str:
    """
    {nodes, edges} から Graphviz DOT を生成。

    ノード:
      - node[shape=plaintext] で「ラベル = HTML TABLE そのもの」
      - TABLE は BORDER=0, CELLBORDER=1
      - 上段: クラス名（少し小さめ）
      - 下段: インスタンス名（少し大きめ）
      - SIDES で外枠＋中央線を 1 本ずつにする
    エッジ:
      - A -> B で、矢印は TABLE の外接矩形（箱）にくっつく
    """
    jp_font = "Noto Sans CJK JP"
    lines: List[str] = []
    lines.append("digraph G {")
    lines.append(f'  graph [rankdir=LR, charset="UTF-8", fontname="{jp_font}"];')
    lines.append(f'  node [shape=plaintext, margin="0,0", fontname="{jp_font}"];')

    for n in graph["nodes"]:
        node_id = n["id"]
        top_raw = n["top"]
        bottom_raw = n["bottom"]

        top_text = html_escape(top_raw)
        bottom_text = html_escape(bottom_raw)

        if bottom_raw:
            # クラス＋インスタンス（中央の1本線）
            html_label = f"""
  <
    <TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0">
      <TR>
        <!-- 四辺全部: 外枠 + 中央線の上側 -->
        <TD CELLPADDING="3" SIDES="TLRB">
          <FONT FACE="{jp_font}" POINT-SIZE="11">{top_text}</FONT>
        </TD>
      </TR>
      <TR>
        <!-- 下＋左右: 外枠の下＋側面。中央線は上段セルの B 側が担当 -->
        <TD CELLPADDING="3" SIDES="BLR">
          <FONT FACE="{jp_font}" POINT-SIZE="13">{bottom_text}</FONT>
        </TD>
      </TR>
    </TABLE>
  >
            """.strip()
        else:
            # クラスだけ（1セルの枠）
            html_label = f"""
  <
    <TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0">
      <TR>
        <TD CELLPADDING="4">
          <FONT FACE="{jp_font}" POINT-SIZE="12">{top_text}</FONT>
        </TD>
      </TR>
    </TABLE>
  >
            """.strip()

        lines.append(f"  {node_id} [label={html_label}];")

    # エッジ
    for e in graph["edges"]:
        src = e["from"]
        tgt = e["to"]
        label = e.get("label") or ""
        if label:
            lines.append(f'  {src} -> {tgt} [label="{html_escape(label)}"];')
        else:
            lines.append(f"  {src} -> {tgt};")

    lines.append("}")
    return "\n".join(lines)

# ===== メイン =====

def main():
    parser = argparse.ArgumentParser(
        description="CIDOC DSL → Graphviz (SVG/DOT) 変換ツール"
    )
    parser.add_argument("input", help="入力 DSL ファイルパス（例: sample.dsl）")
    parser.add_argument(
        "-o",
        "--output",
        help="出力ファイルパス（.svg 推奨。未指定なら標準出力）",
    )
    parser.add_argument(
        "--dot",
        action="store_true",
        help="SVG ではなく DOT テキストを出力（graphviz Python ラッパ不要）",
    )
    args = parser.parse_args()

    src = Path(args.input).read_text(encoding="utf-8")
    graph = parse_dsl(src)
    dot = graph_to_dot(graph)

    # DOT だけ欲しい場合 / graphviz ラッパ未インストール時
    if args.dot or Source is None:
        if args.output:
            Path(args.output).write_text(dot, encoding="utf-8")
        else:
            print(dot)
        return

    # Graphviz (Python ラッパ) で SVG 生成
    src_obj = Source(dot)
    svg_bytes: bytes = src_obj.pipe(format="svg")

    if args.output:
        Path(args.output).write_bytes(svg_bytes)
    else:
        import sys

        sys.stdout.buffer.write(svg_bytes)

if __name__ == "__main__":
    main()
