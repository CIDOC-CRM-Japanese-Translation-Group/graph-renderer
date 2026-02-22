<script lang="ts">
  export let laidOut;

  // ===== Zoom / Pan（初期表示やや大きめ） =====
  let svgEl: SVGSVGElement | null = null;
  let scale = 1.4;
  let tx = 80, ty = 80;
  let panning = false;
  let lastX = 0, lastY = 0;

  function svgPoint(clientX: number, clientY: number) {
    const pt = (svgEl as any).createSVGPoint();
    pt.x = clientX; pt.y = clientY;
    const m = svgEl!.getScreenCTM();
    if (!m) return { x: 0, y: 0 };
    const inv = m.inverse();
    const sp = pt.matrixTransform(inv);
    return { x: (sp.x - tx) / scale, y: (sp.y - ty) / scale };
  }
  function onWheel(e: WheelEvent) {
    e.preventDefault();
    const factor = e.deltaY < 0 ? 1.1 : 0.9;
    const before = svgPoint(e.clientX, e.clientY);
    scale *= factor;
    const after = svgPoint(e.clientX, e.clientY);
    tx += (after.x - before.x) * scale;
    ty += (after.y - before.y) * scale;
  }
  function onDown(e: MouseEvent){ panning = true; lastX = e.clientX; lastY = e.clientY; }
  function onMove(e: MouseEvent){
    if (!panning) return;
    const dx = e.clientX - lastX, dy = e.clientY - lastY;
    lastX = e.clientX; lastY = e.clientY; tx += dx; ty += dy;
  }
  function onUp(){ panning = false; }

  // ===== Edge label（交互オフセット） =====
  let labelIdx = 0;
  const nextDy = () => (labelIdx++ % 2 === 0 ? -8 : 14);
  $: if (laidOut) labelIdx = 0;

  // ===== Export: SVG をそのまま文字列化 =====
  export function toSVGString(): string {
    if (!svgEl) return '';
    const clone = svgEl.cloneNode(true) as SVGSVGElement;

    // 余計なイベント属性を掃除
    ['onload','onmousedown','onmousemove','onmouseup','onwheel'].forEach(attr => {
      clone.querySelectorAll(`[${attr}]`).forEach(n => (n as Element).removeAttribute(attr));
    });

    // 必要な名前空間と version
    clone.setAttribute('xmlns', 'http://www.w3.org/2000/svg');
    clone.setAttribute('xmlns:xlink', 'http://www.w3.org/1999/xlink');
    clone.setAttribute('version', '1.1');

    // 幅・高さが無い場合は viewBox から設定
    const vb = clone.getAttribute('viewBox');
    if (vb && !clone.getAttribute('width') && !clone.getAttribute('height')) {
      const [, , w, h] = vb.split(/\s+/).map(Number);
      clone.setAttribute('width', String(w));
      clone.setAttribute('height', String(h));
    }

    // 最低限のフォント等のスタイルを埋め込む
    const style = document.createElementNS('http://www.w3.org/2000/svg', 'style');
    style.textContent = `
      text { font-family: system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, "Apple Color Emoji", "Segoe UI Emoji"; }
      rect, line, path, polygon { shape-rendering: geometricPrecision; }
    `;
    clone.insertBefore(style, clone.firstChild);

    return new XMLSerializer().serializeToString(clone);
  }
</script>

<svg
  bind:this={svgEl}
  viewBox="-200 -200 3000 2000"
  style="width:100%;height:100%;background:#f7f7f7; touch-action:none;"
  on:wheel|passive={onWheel}
  on:mousedown={onDown}
  on:mousemove={onMove}
  on:mouseup={onUp}
  on:mouseleave={onUp}
>
  <g transform={`translate(${tx},${ty}) scale(${scale})`}>
    {#if laidOut?.nodes?.length}
      {#each laidOut.nodes as n}
        <g transform={`translate(${n.x ?? 0},${n.y ?? 0})`}>
          <rect rx="12" ry="12" width="{n.w ?? 220}" height="{n.h ?? 96}" fill="white" stroke="#333"/>
          <line x1="0" y1="{(n.h ?? 96)/2}" x2="{(n.w ?? 220)}" y2="{(n.h ?? 96)/2}" stroke="#333"/>

          <!-- 上段：タイトル -->
          <text x="10" y="26" font-size="20" font-weight="700">{n.top}</text>
          <!-- 下段：本文（あれば） -->
          {#if n.bottom}
            <text x="10" y="{(n.h ?? 96)/2 + 22}" font-size="18">{n.bottom}</text>
          {/if}
        </g>
      {/each}
    {/if}

    {#if laidOut?.edges?.length}
      {#each laidOut.edges as e (e.id)}
        {#if e?.sections?.length}
          {#each e.sections as s, i (i)}
            {#if s?.startPoint && s?.endPoint}
              <!-- 線 -->
              <path
                d={`M ${s.startPoint.x} ${s.startPoint.y} ${
                  s.bendPoints ? s.bendPoints.map(b => `L ${b.x} ${b.y}`).join(' ') + ' ' : ''
                }L ${s.endPoint.x} ${s.endPoint.y}`}
                fill="none" stroke="#333"
              />
              <!-- 矢印 -->
              <g transform={`translate(${s.endPoint.x},${s.endPoint.y})`}>
                <polygon points="0,0 -8,-4 -8,4" fill="#333"/>
              </g>

              <!-- ラベル：直線の中点 + 交互オフセット -->
              {#if e.labels && e.labels.length}
                {@const mx = (s.startPoint.x + s.endPoint.x) / 2}
                {@const my = (s.startPoint.y + s.endPoint.y) / 2}
                {@const dy = nextDy()}
                <rect x={mx - 60} y={my - 16 + dy} width="120" height="20" rx="3" ry="3" fill="white" opacity="0.92"/>
                <text x={mx} y={my - 2 + dy} font-size="14" text-anchor="middle" fill="#333">
                  {e.labels[0].text}
                </text>
              {/if}
            {/if}
          {/each}
        {/if}
      {/each}
    {/if}
  </g>
</svg>
