<script lang="ts">
  export let value = '';

  // Google Sheets 関連
  let useSheet = false;
  let sheetUrl = '';
  let loading = false;
  let error: string | null = null;

  function onInput(e: Event) {
    const target = e.target as HTMLTextAreaElement;
    value = target.value;
  }

  async function maybeLoadFromSheet() {
    if (!useSheet || !sheetUrl) return;
    loading = true;
    error = null;
    try {
      const res = await fetch(sheetUrl);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const tsv = await res.text();
      value = tsvToDsl(tsv);   // ここで自動生成して src を上書き
    } catch (err: any) {
      error = err?.message ?? String(err);
    } finally {
      loading = false;
    }
  }

  function tsvToDsl(tsv: string): string {
    const lines = tsv.split(/\r?\n/).filter(l => l.trim());
    if (lines.length <= 1) return 'crm {\n}\n';

    const dataLines = lines.slice(1);

    type NodeInfo = { id: string; label: string };
    const nodes = new Map<string, NodeInfo>();
    const classCounters: Record<string, number> = {};
    const edges: { from: string; to: string; label: string }[] = [];

    function getNodeId(cls: string, lbl: string): string {
      const key = `${cls}||${lbl}`;
      const existing = nodes.get(key);
      if (existing) return existing.id;

      const classCode = cls.split(' ')[0] || 'N';
      const current = (classCounters[classCode] ?? 0) + 1;
      classCounters[classCode] = current;
      const id = `${classCode}_${current}`;
      const label = `${cls} | ${lbl}`;
      nodes.set(key, { id, label });
      return id;
    }

    for (const line of dataLines) {
      const cols = line.split('\t');
      if (cols.length < 6) continue;
      const [sClassRaw, sLabelRaw, propRaw, _type, oClassRaw, oLabelRaw] = cols;
      const sClass = sClassRaw.trim();
      const sLabel = sLabelRaw.trim();
      const prop = propRaw.trim();
      const oClass = oClassRaw.trim();
      const oLabel = oLabelRaw.trim();

      if (!sClass || !sLabel || !prop || !oClass || !oLabel) continue;

      const from = getNodeId(sClass, sLabel);
      const to = getNodeId(oClass, oLabel);
      const propShort = prop.replace(/\s*\(.*\)\s*$/, '');
      edges.push({ from, to, label: propShort });
    }

    let out = 'crm {\n';
    const nodeList = Array.from(nodes.values()).sort((a, b) => a.id.localeCompare(b.id));
    for (const n of nodeList) {
      out += `${n.id} "${n.label}"\n`;
    }
    for (const e of edges) {
      out += `${e.from} -> ${e.to} : ${e.label}\n`;
    }
    out += '}';
    return out;
  }
</script>

<div style="display:flex; flex-direction:column; gap:0.5rem; height:100%;">
  <div style="display:flex; align-items:center; gap:0.5rem;">
    <label style="display:flex; align-items:center; gap:0.25rem;">
      <input type="checkbox"
             bind:checked={useSheet}
             on:change={maybeLoadFromSheet} />
      Google Sheets から生成
    </label>
    <input
      type="text"
      placeholder="https://docs.google.com/.../pub?output=tsv"
      bind:value={sheetUrl}
      on:change={maybeLoadFromSheet}
      style="flex:1; font-size:0.9rem;"
    />
    {#if loading}
      <span>読み込み中...</span>
    {/if}
  </div>

  {#if error}
    <div style="color:red; font-size:0.8rem;">{error}</div>
  {/if}

  <textarea
    bind:value={value}
    rows="30"
    style="width:100%; height:100%; font-family:monospace;"
    on:input={onInput}
    disabled={useSheet}
  ></textarea>
</div>
