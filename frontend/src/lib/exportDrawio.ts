// src/lib/exportDrawio.ts
export type Node = {
  id: string;
  label: string;
  x: number;
  y: number;
  width: number;
  height: number;
};

export type Edge = {
  id?: string;
  from: string;
  to: string;
  label?: string;
};

export type Graph = {
  nodes: Node[];
  edges: Edge[];
};

function escapeXml(value: string): string {
  return value
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&apos;");
}

export function graphToDrawioXml(graph: Graph): string {
  let nextId = 2; // 0,1 はルート・レイヤー用

  const nodeIdMap = new Map<string, string>();
  for (const n of graph.nodes) {
    nodeIdMap.set(n.id, String(nextId++));
  }

  const edgeIds = graph.edges.map(() => String(nextId++));

  let xml = `<?xml version="1.0" encoding="UTF-8"?>\n`;
  xml += `<mxfile host="app.diagrams.net">\n`;
  xml += `  <diagram id="diagram-1" name="Page-1">\n`;
  xml += `    <mxGraphModel>\n`;
  xml += `      <root>\n`;
  xml += `        <mxCell id="0"/>\n`;
  xml += `        <mxCell id="1" parent="0"/>\n`;

  graph.nodes.forEach((node) => {
    const mxId = nodeIdMap.get(node.id)!;
    const value = escapeXml(node.label ?? "");
    xml += `        <mxCell id="${mxId}" value="${value}" `;
    xml += `style="rounded=1;whiteSpace=wrap;html=1;" vertex="1" parent="1">\n`;
    xml += `          <mxGeometry x="${node.x}" y="${node.y}" width="${node.width}" height="${node.height}" as="geometry"/>\n`;
    xml += `        </mxCell>\n`;
  });

  graph.edges.forEach((edge, i) => {
    const edgeId = edgeIds[i];
    const srcId = nodeIdMap.get(edge.from);
    const tgtId = nodeIdMap.get(edge.to);
    if (!srcId || !tgtId) return;

    const value = escapeXml(edge.label ?? "");
    xml += `        <mxCell id="${edgeId}" value="${value}" `;
    xml += `style="endArrow=block;endFill=1;html=1;" edge="1" parent="1" `;
    xml += `source="${srcId}" target="${tgtId}">\n`;
    xml += `          <mxGeometry relative="1" as="geometry"/>\n`;
    xml += `        </mxCell>\n`;
  });

  xml += `      </root>\n`;
  xml += `    </mxGraphModel>\n`;
  xml += `  </diagram>\n`;
  xml += `</mxfile>\n`;

  return xml;
}

export function downloadDrawio(graph: Graph, filename = "graph.drawio") {
  const xml = graphToDrawioXml(graph);
  const blob = new Blob([xml], { type: "application/xml" });
  const url = URL.createObjectURL(blob);

  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  a.click();

  URL.revokeObjectURL(url);
}
