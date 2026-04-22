"""
Generate static experiment animation pages for docs/site.

Outputs:
  - docs/site/experiments/index.json
  - docs/site/experiments/index.js
  - docs/site/experiments/pages/<group>__<name>.html

Each page includes:
  - Three.js animation canvas
  - Source path
  - Principle/docstring summary
  - Extracted uppercase parameters (best-effort)
"""

from __future__ import annotations

import ast
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_DIR = ROOT / "scripts"
SITE_EXP_DIR = ROOT / "docs" / "site" / "experiments"
PAGES_DIR = SITE_EXP_DIR / "pages"


@dataclass
class ExperimentMeta:
    id: str
    title: str
    group: str
    source_path: str
    page_path: str
    principle: str
    parameters: list[dict[str, Any]]
    animation_mode: str
    run_command: str


def _safe_literal(node: ast.AST) -> str:
    try:
        v = ast.literal_eval(node)
        if isinstance(v, (int, float, str, bool)):
            return str(v)
        return repr(v)
    except Exception:
        return "<expr>"


def extract_meta(py_path: Path) -> tuple[str, list[dict[str, str]]]:
    src = py_path.read_text(encoding="utf-8", errors="ignore")
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return ("(parse failed)", [])

    principle = (ast.get_docstring(tree) or "").strip()
    if principle:
        principle = principle.splitlines()[0][:180]
    else:
        principle = "No module docstring. See source for details."

    params: list[dict[str, str]] = []
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Name) and t.id.isupper():
                    params.append({"name": t.id, "value": _safe_literal(node.value)})
        if len(params) >= 18:
            break
    return (principle, params)


def mode_for_group(group: str) -> str:
    return {
        "ce": "wave",
        "explore": "network",
        "verify": "pulse",
        "discover": "spiral",
        "misc": "tree",
    }.get(group, "tree")


def page_html(meta: ExperimentMeta) -> str:
    rows = "\n".join(
        f"<tr><td>{p['name']}</td><td>{p['value']}</td></tr>" for p in meta.parameters
    ) or "<tr><td colspan='2'>(no extracted uppercase constants)</td></tr>"
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{meta.title}</title>
  <style>
    body {{ margin:0; font-family:Segoe UI,Arial,sans-serif; background:#0d1117; color:#e6edf3; }}
    .wrap {{ max-width:1100px; margin:0 auto; padding:16px; }}
    .card {{ border:1px solid #30363d; border-radius:10px; padding:12px; background:#111827; margin-bottom:12px; }}
    .meta {{ color:#8b949e; font-size:13px; }}
    #c {{ width:100%; height:calc(100vh - 260px); min-height:420px; border:1px solid #30363d; border-radius:8px; display:block; }}
    table {{ width:100%; border-collapse:collapse; }}
    th,td {{ border:1px solid #30363d; padding:6px 8px; text-align:left; font-size:13px; }}
    th {{ background:#0f1f35; }}
    code {{ color:#58a6ff; }}
  </style>
</head>
<body>
  <div class="wrap">
    <div class="card">
      <h2 style="margin:0 0 8px">{meta.title}</h2>
      <div class="meta">Group: {meta.group} | Source: <code>{meta.source_path}</code></div>
    </div>
    <div class="card">
      <h3 style="margin:0 0 8px">动画</h3>
      <canvas id="c"></canvas>
    </div>
    <div class="card">
      <h3 style="margin:0 0 8px">运行命令</h3>
      <div class="meta">在仓库根目录执行</div>
      <pre style="white-space:pre-wrap;color:#58a6ff">{meta.run_command}</pre>
    </div>
    <div class="card">
      <h3 style="margin:0 0 8px">原理说明</h3>
      <div>{meta.principle}</div>
    </div>
    <div class="card">
      <h3 style="margin:0 0 8px">参数（自动提取）</h3>
      <table>
        <thead><tr><th>参数名</th><th>值/表达式</th></tr></thead>
        <tbody>{rows}</tbody>
      </table>
    </div>
  </div>
  <script src="https://unpkg.com/three@0.161.0/build/three.min.js"></script>
  <script>
    const mode = {json.dumps(meta.animation_mode)};
    const canvas = document.getElementById('c');
    const renderer = new THREE.WebGLRenderer({{canvas, antialias:true, alpha:true}});
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(50, 2, 0.1, 100);
    camera.position.set(0,0.2,6);
    const g = new THREE.Group(); scene.add(g);
    const nodes = [];
    const nodeGeo = new THREE.SphereGeometry(0.045, 10, 10);
    const nodeMat = new THREE.MeshBasicMaterial({{color:0x58a6ff}});
    for(let i=0;i<180;i++) {{
      const m = new THREE.Mesh(nodeGeo, nodeMat);
      m.position.set((Math.random()-0.5)*4, (Math.random()-0.5)*2.6, (Math.random()-0.5)*2.4);
      g.add(m); nodes.push(m);
    }}
    const lineMat = new THREE.LineBasicMaterial({{color:0x8b949e}});
    for(let i=1;i<nodes.length;i++) {{
      const a = nodes[(i*7)%nodes.length].position;
      const b = nodes[i].position;
      const geo = new THREE.BufferGeometry().setFromPoints([a,b]);
      g.add(new THREE.Line(geo, lineMat));
    }}
    function resize() {{
      const w = canvas.clientWidth, h = canvas.clientHeight;
      renderer.setSize(w,h,false); camera.aspect = w/h; camera.updateProjectionMatrix();
    }}
    window.addEventListener('resize', resize); resize();
    function tick(t) {{
      const x = t*0.001;
      g.rotation.y = x*0.15;
      if(mode==='wave') g.rotation.x = Math.sin(x*1.2)*0.15;
      if(mode==='network') g.rotation.z = Math.cos(x*0.7)*0.1;
      if(mode==='pulse') nodes.forEach((n,i)=> n.scale.setScalar(0.8+0.4*Math.abs(Math.sin(x*2+i*0.09))));
      if(mode==='spiral') nodes.forEach((n,i)=>{{ const a=x*0.2+i*0.1; n.position.x=Math.cos(a)*(1.2+i*0.004); n.position.z=Math.sin(a)*(1.2+i*0.004); }});
      if(mode==='tree') nodes.forEach((n,i)=>{{ n.position.y += Math.sin(x+i*0.1)*0.0008; }});
      renderer.render(scene,camera); requestAnimationFrame(tick);
    }}
    requestAnimationFrame(tick);
  </script>
</body>
</html>
"""


def main() -> None:
    PAGES_DIR.mkdir(parents=True, exist_ok=True)
    metas: list[ExperimentMeta] = []

    for py in sorted(SCRIPTS_DIR.rglob("*.py")):
        rel = py.relative_to(ROOT).as_posix()
        if "__pycache__" in rel:
            continue
        # keep experiment-like scripts only
        if not rel.startswith("scripts/"):
            continue
        group = py.parent.name
        principle, params = extract_meta(py)
        base = py.stem
        page_name = f"{group}__{base}.html"
        page_rel = f"docs/site/experiments/pages/{page_name}"
        exp_id = f"{group}-{base}"
        title = base.replace("_", " ")
        meta = ExperimentMeta(
            id=exp_id,
            title=title,
            group=group,
            source_path=rel,
            page_path=page_rel,
            principle=principle,
            parameters=params,
            animation_mode=mode_for_group(group),
            run_command=f'./activate_conda.ps1; python "{rel}"',
        )
        (PAGES_DIR / page_name).write_text(page_html(meta), encoding="utf-8")
        metas.append(meta)

    index = {
        "generated_at": str(Path(__file__).name),
        "count": len(metas),
        "experiments": [asdict(m) for m in metas],
    }
    json_text = json.dumps(index, ensure_ascii=False, indent=2)
    (SITE_EXP_DIR / "index.json").write_text(json_text, encoding="utf-8")
    (SITE_EXP_DIR / "index.js").write_text(
        "window.EXPERIMENT_INDEX = " + json.dumps(index, ensure_ascii=False) + ";\n",
        encoding="utf-8",
    )
    print(f"generated {len(metas)} experiment pages")


if __name__ == "__main__":
    main()

