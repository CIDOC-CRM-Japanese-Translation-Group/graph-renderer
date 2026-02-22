<script lang="ts">
  import Editor from './Editor.svelte';
  import Canvas from './Canvas.svelte';
  import { parseDsl } from './lib/parseDsl';
  import { layout } from './lib/layoutElk';
  import { onMount } from 'svelte';

  // FastAPI 側のベースURL（必要に応じて書き換えてください）
  const API_BASE = '/crmviz-api/api';

  let src = `crm {
E22 "E22 Human-Made Object | Vase 123"
E42 "E42 Identifier | 123"
E55 "E55 Type | Vase"
E22 -> E42 : P1 is identified by
E22 -> E55 : P2 has type
}`;

  // parseDsl の結果（id, top, bottom, edges[from/to/label]）
  let graph: any = { nodes: [], edges: [] };

  // layoutElk の結果（nodes に x, y, w, h が付いたもの + ELK edges）
  let laidOut: any;
  let isLayouting = false;

  // Canvas.svelte インスタンス（toSVGString() を呼ぶのに使う）
  let canvasRef: any;

  // DSL → Graph → ELK レイアウト
  async function update() {
    graph = parseDsl(src);
    isLayouting = true;
    try {
      laidOut = await layout(graph);
    } catch (e) {
      console.error('layout error', e);
    } finally {
      isLayouting = false;
    }
  }

  // 共通ダウンロードヘルパー
  function triggerDownload(blob: Blob, filename: string) {
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);
  }

  // 1. 画面に見えている SVG（ELK レイアウトのまま）
  function downloadScreenSVG() {
    const svg = canvasRef?.toSVGString?.();
    if (!svg) return;
    const blob = new Blob([svg], {
      type: 'image/svg+xml;charset=utf-8'
    });
    triggerDownload(blob, 'cidoc-graph-screen.svg');
  }

  // 2. Graphviz SVG（DSL → Graphviz）
  async function downloadGraphvizSvg() {
    try {
      const res = await fetch(`${API_BASE}/graphviz/svg`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ dsl: src })
      });
      if (!res.ok) {
        console.error('Graphviz SVG error', await res.text());
        return;
      }
      const blob = await res.blob();
      triggerDownload(blob, 'cidoc-graph-graphviz.svg');
    } catch (e) {
      console.error('Graphviz SVG error', e);
    }
  }

  // 3. Graphviz PNG（DSL → Graphviz）
  async function downloadGraphvizPng() {
    try {
      const res = await fetch(`${API_BASE}/graphviz/png`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ dsl: src })
      });
      if (!res.ok) {
        console.error('Graphviz PNG error', await res.text());
        return;
      }
      const blob = await res.blob();
      triggerDownload(blob, 'cidoc-graph-graphviz.png');
    } catch (e) {
      console.error('Graphviz PNG error', e);
    }
  }

  onMount(() => {
    update();
  });
</script>

<main
  style="
    display:flex;
    height:100vh;
    gap:8px;
    padding:8px;
    box-sizing:border-box;
    font-family: system-ui, -apple-system, BlinkMacSystemFont, sans-serif;
  "
>
  <!-- 左ペイン：エディタ + ボタン -->
  <section
    style="
      flex:0 0 38%;
      min-width:300px;
      border-right:1px solid #ddd;
      display:flex;
      flex-direction:column;
    "
  >
    <div
      style="
        display:flex;
        flex-wrap:wrap;
        gap:8px;
        align-items:center;
        padding:8px;
      "
    >
      <button
        on:click={update}
        disabled={isLayouting}
        style="padding:6px 10px; border:1px solid #ccc; border-radius:6px; cursor:pointer;"
      >
        {isLayouting ? 'レイアウト中…' : 'Apply'}
      </button>

      <button
        on:click={downloadScreenSVG}
        style="padding:6px 10px; border:1px solid #ccc; border-radius:6px; cursor:pointer;"
      >
        Screen SVG
      </button>

      <button
        on:click={downloadGraphvizSvg}
        style="padding:6px 10px; border:1px solid #ccc; border-radius:6px; cursor:pointer;"
      >
        Graphviz SVG
      </button>

      <button
        on:click={downloadGraphvizPng}
        style="padding:6px 10px; border:1px solid #ccc; border-radius:6px; cursor:pointer;"
      >
        Graphviz PNG
      </button>

      <span style="margin-left:auto; display:flex; gap:10px; align-items:center; font-size:0.85rem;">
        <a href="https://github.com/CIDOC-CRM-Japanese-Translation-Group/graph-renderer/blob/main/docs/dsl.md" target="_blank" rel="noopener">DSL</a>
        <a href="https://github.com/CIDOC-CRM-Japanese-Translation-Group/graph-renderer/blob/main/docs/google-sheets.md" target="_blank" rel="noopener">Google Sheets</a>
        <a href="https://github.com/CIDOC-CRM-Japanese-Translation-Group/graph-renderer" target="_blank" rel="noopener">GitHub</a>
      </span>

    </div>

    <div style="flex:1; min-height:0;">
      <Editor bind:value={src} />
    </div>
  </section>

  <!-- 右ペイン：Canvas -->
  <section style="flex:1.2; min-width:0; min-height:0;">
    {#if laidOut}
      <Canvas bind:this={canvasRef} {laidOut} />
    {/if}
  </section>
</main>
