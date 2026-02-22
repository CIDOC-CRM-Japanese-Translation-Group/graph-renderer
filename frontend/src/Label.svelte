<script lang="ts">
  import { onMount, tick } from 'svelte';

  export let x = 0;             // 中心座標
  export let y = 0;
  export let text = '';
  export let minW = 80;         // 背景の最小幅
  export let maxW = 240;        // 背景の最大幅
  export let padX = 8;          // 左右パディング
  export let padY = 4;          // 上下パディング
  export let fontSize = 12;

  let textEl: SVGTextElement | null = null;
  let shown = '';               // 実際に描画する文字列（省略後）
  let w = minW;                 // 背景幅（計測して更新）
  let h = fontSize + padY * 2;  // 背景高（単行）

  function measureWidth(s: string) {
    if (!textEl) return 0;
    // 一時的に文字列を差し替えて長さを測る
    textEl.textContent = s;
    const len = textEl.getComputedTextLength();
    textEl.textContent = shown || text; // 元に戻す（ちらつき防止）
    return len;
  }

  function truncateToWidth(s: string, maxTextW: number) {
    // 余裕があるならそのまま
    if (measureWidth(s) <= maxTextW) return s;
    // 末尾を二分探索的に詰めて '…' を付与
    let lo = 0, hi = s.length;
    while (lo < hi) {
      const mid = Math.floor((lo + hi) / 2);
      const candidate = s.slice(0, mid) + '…';
      if (measureWidth(candidate) <= maxTextW) lo = mid + 1;
      else hi = mid;
    }
    const finalStr = s.slice(0, Math.max(0, lo - 1)) + '…';
    return finalStr;
  }

  async function recompute() {
    await tick(); // DOM 反映後に計測
    const textW = measureWidth(text);
    const targetW = Math.min(maxW, Math.max(minW, textW + padX * 2));
    // 背景に合わせてテキストも省略
    shown = truncateToWidth(text, targetW - padX * 2);
    w = Math.min(maxW, Math.max(minW, measureWidth(shown) + padX * 2));
  }

  onMount(recompute);
  $: text, minW, maxW, padX, padY, fontSize, recompute();
</script>

<!-- 背景（中央合わせ） -->
<rect x={x - w/2} y={y - h/2} width={w} height={h} rx="3" ry="3" fill="white" opacity="0.92" />

<!-- テキスト -->
<text x={x} y={y + fontSize/3} font-size={fontSize} text-anchor="middle" fill="#333" bind:this={textEl}>
  {shown || text}
</text>
