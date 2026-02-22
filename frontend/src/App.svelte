<script lang="ts">
  import Editor from './Editor.svelte';
  import Canvas from './Canvas.svelte';
  import { parseDsl } from './lib/parseDsl';
  import { layout } from './lib/layoutElk';
  import { onMount } from 'svelte';
  import { downloadDrawio } from './lib/exportDrawio';

  let src = `crm {
E22 "E22 Human-Made Object | Vase 123"
E42 "E42 Identifier | 123"
E55 "E55 Type | Vase"
E22 -> E42 : P1 is identified by
E22 -> E55 : P2 has type
}`;

  let graph = { nodes: [], edges: [] };
  let laidOut: any;

  // Apply（反映）
  async function update() {
    graph = parseDsl(src);
    laidOut = await layout(graph);
  }

  // --- SVG Download ---
  let canvasRef: any; // Canvas.svelte のインスタンス参照
  function downloadSVG() {
    const svg = canvasRef?.toSVGString?.();
    if (!svg) return;
    const blob = new Blob([svg], { type: 'image/svg+xml;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'diagram.svg';
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);
  }

  // --- draw.io XML Download ---
  function downloadDrawioXml() {
    if (!laidOut) return;

    const nodes = (laidOut.nodes ?? []).map((n: any, idx: number) => ({
      id: n.id ?? String(idx + 1),
      // draw.io 側では 1 行に入ってほしいので top / bottom をまとめる
      label: n.bottom ? `${n.top} | ${n.bottom}` : n.top,
      x: n.x ?? 0,
      y: n.y ?? 0,
      width: n.w ?? 220,
      height: n.h ?? 96
    }));

    const edges = (laidOut.edges ?? []).map((e: any) => ({
      from: e.from,          // layoutElk が from/to を持っている前提（違っていたらここだけ調整）
      to: e.to,
      label: e.labels?.[0]?.text ?? ''
    }));

    downloadDrawio({ nodes, edges }, 'crm-graph.drawio');
  }

  onMount(update);
</script>

<main style="display:flex; height:100vh; overflow:hidden;">
  <!-- 左ペイン：ツールバー + エディタ -->
  <section
    style="flex:0 0 38%; min-width:300px; border-right:1px solid #ddd; display:flex; flex-direction:column;"
  >
    <div style="display:flex; gap:8px; align-items:center; padding:8px;">
      <button
        on:click={update}
        style="padding:6px 10px; border:1px solid #ccc; border-radius:6px; cursor:pointer;"
      >
        Apply
      </button>

      <button
        on:click={downloadDrawioXml}
        style="padding:6px 10px; border:1px solid #ccc; border-radius:6px; cursor:pointer;"
      >
        Download draw.io XML
      </button>

      <button
        on:click={downloadSVG}
        style="padding:6px 10px; border:1px solid #ccc; border-radius:6px; cursor:pointer;"
      >
        Download SVG
      </button>
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
