import ELK from 'elkjs/lib/elk.bundled.js';
import type { Graph } from './types';
const elk = new ELK();

const _canvas = document.createElement('canvas');
const _ctx = _canvas.getContext('2d')!;

function measureText(text: string, font: string): number {
  _ctx.font = font;
  return _ctx.measureText(text).width;
}

function nodeSize(top: string, bottom?: string): { w: number; h: number } {
  const PAD = 24;
  const topW = measureText(top,     'bold 20px system-ui');
  const botW = bottom ? measureText(bottom, '18px system-ui') : 0;
  const w = Math.max(220, Math.ceil(Math.max(topW, botW)) + PAD);
  const h = bottom ? 96 : 56;
  return { w, h };
}

export async function layout(graph: Graph) {

  // まず入出次数を数える
  const outDeg = new Map<string, number>();
  const inDeg  = new Map<string, number>();
  for (const e of graph.edges) {
    outDeg.set(e.from, (outDeg.get(e.from) ?? 0) + 1);
    inDeg.set(e.to,     (inDeg.get(e.to)   ?? 0) + 1);
  }

  // 各ノードに左右ポートを必要数だけ用意（yは指定しない＝ELKが分配）
  const sizes = new Map(graph.nodes.map(n => [n.id, nodeSize(n.top, n.bottom)]));
  const children = graph.nodes.map(n => {
    const o = outDeg.get(n.id) ?? 0;
    const i = inDeg.get(n.id)  ?? 0;
    const { w, h } = sizes.get(n.id)!;
    const ports: any[] = [];
    for (let k = 0; k < o; k++) {
      ports.push({
        id: `${n.id}.E${k}`,
        properties: { 'elk.port.side': 'EAST' }   // 右側
      });
    }
    for (let k = 0; k < i; k++) {
      ports.push({
        id: `${n.id}.W${k}`,
        properties: { 'elk.port.side': 'WEST' }   // 左側
      });
    }
    return {
      id: n.id,
      width: w,
      height: h,
      ports,
      layoutOptions: {
        'elk.portConstraints': 'FIXED_SIDE'       // 側だけ固定、位置はELKに任せる
      }
    };
  });

  // 出入口の何本目かでポートを割り当て
  const outIdx = new Map<string, number>();
  const inIdx  = new Map<string, number>();
  const edges = graph.edges.map(e => {
    const oi = outIdx.get(e.from) ?? 0;
    const ii = inIdx.get(e.to)    ?? 0;
    outIdx.set(e.from, oi + 1);
    inIdx.set(e.to,    ii + 1);
    return {
      id: e.id,
      sources: [`${e.from}.E${oi}`],
      targets: [`${e.to}.W${ii}`],
      labels: e.label ? [{
        id: `${e.id}.label`,
        text: e.label,
        width: Math.max(120, Math.ceil(measureText(e.label, '14px system-ui')) + 16),
        height: 20,
      }] : []
    };
  });

  const elkGraph: any = {
    id: 'root',
    layoutOptions: {
      'elk.algorithm': 'layered',
      'elk.direction': 'RIGHT',
      'elk.spacing.nodeNode': '32',
      'elk.layered.spacing.nodeNodeBetweenLayers': '72',
      'elk.layered.edgeRouting': 'ORTHOGONAL',
      'elk.edgeSpacing.factor': '1.3',            // エッジ間隔を少し広めに
      'elk.layered.considerModelOrder': 'true'
    },
    children, edges
  };

  const result = await elk.layout(elkGraph);
  const pos = new Map((result.children ?? []).map((c: any) => [c.id, c]));
  const edgeMap = new Map((result.edges ?? []).map((e: any) => [e.id, e]));

  return {
    nodes: graph.nodes.map(n => ({
      ...n,
      x: pos.get(n.id)?.x ?? 0,
      y: pos.get(n.id)?.y ?? 0,
      w: sizes.get(n.id)!.w,
      h: sizes.get(n.id)!.h,
    })),
    edges: graph.edges.map(e => edgeMap.get(e.id)).filter(Boolean)
  };
}
