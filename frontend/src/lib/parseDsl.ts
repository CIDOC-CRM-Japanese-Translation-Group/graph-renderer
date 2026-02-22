import type { Graph } from './types';
export function parseDsl(src: string): Graph {
  const nodes = [];
  const edges = [];
  const nodeRe = /^\s*([A-Za-z0-9_:-]+)\s+"([^"]*)"\s*$/;
  const edgeRe = /^\s*([A-Za-z0-9_:-]+)\s*->\s*([A-Za-z0-9_:-]+)\s*:\s*(.+)\s*$/;

  for (const line of src.split('\n')) {
    if (nodeRe.test(line)) {
      const [, id, txt] = line.match(nodeRe)!;
      const [top, bottom=''] = txt.split('|',2).map(s=>s.trim());
      nodes.push({ id, top, bottom });
    } else if (edgeRe.test(line)) {
      const [, from, to, label] = line.match(edgeRe)!;
      edges.push({ id:`${from}-${to}-${label}`, from, to, label });
    }
  }
  return { nodes, edges };
}
