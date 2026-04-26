#!/usr/bin/env python3
"""
Build merged v7+v8 manuscript HTML with the same visual system as v7.html
(paper-container, grid/cards, MathJax).
"""

from __future__ import annotations

import argparse
from pathlib import Path

import markdown

# Mirrors papers_final/.../v7.html stylesheet for consistent "professional" look.
PAPER_CSS = r"""
:root {
  --bg: #f5f7fb;
  --card: #ffffff;
  --text: #1f2937;
  --muted: #6b7280;
  --line: #e5e7eb;
  --accent: #2563eb;
}
* { box-sizing: border-box; }
body {
  margin: 0;
  font-family: 'Inter', 'Noto Sans SC', system-ui, sans-serif;
  color: var(--text);
  background: #1a202c;
  max-width: 1000px;
  margin: 40px auto;
  padding: 0 20px;
  line-height: 1.6;
}
.paper-container {
  background: var(--card);
  padding: 56px 48px;
  border-radius: 12px;
  box-shadow: 0 20px 25px -5px rgba(0,0,0,0.1);
  border-top: 10px solid #4a5568;
}
.main-title-block {
  text-align: center;
  margin: 0 0 28px 0;
  padding-bottom: 16px;
  border-bottom: 3px solid #4a5568;
}
.main-title-block h1 {
  color: #1a202c;
  font-size: 2.1em;
  text-align: center;
  margin: 0 auto;
  line-height: 1.25;
}
.main-title-block h1 + h1 {
  margin-top: 0.4em;
  font-size: 1.8em;
  font-weight: 600;
}
.sub {
  color: var(--muted);
  font-size: 0.95rem;
  margin: 8px 0 0 0;
  text-align: center;
}
.metadata {
  background: #f7fafc;
  padding: 24px 20px;
  border-radius: 8px;
  margin: 32px 0;
  border: 1px solid #e2e8f0;
  text-align: center;
  overflow-wrap: anywhere;
  font-size: 0.95rem;
  color: #4a5568;
}
.metadata .meta {
  margin-top: 8px;
  font-size: 0.86rem;
  color: #6b7280;
}
.metadata a {
  color: #1d4ed8;
  text-decoration: none;
  font-weight: 600;
  word-break: break-word;
}
.metadata a:hover { text-decoration: underline; }
.md-content h2 {
  margin: 18px 0 10px 0;
  font-size: 1.15rem;
  color: #2d3748;
  border-left: 8px solid #4a5568;
  padding-left: 16px;
}
.md-content h3 {
  margin: 14px 0 8px 0;
  font-size: 1.02rem;
  color: #374151;
}
.md-content p, .md-content li { font-size: 0.94rem; color: #374151; }
.md-content code {
  background: #f4f4f5;
  padding: 0.1rem 0.28rem;
  border-radius: 4px;
  font-size: 0.86rem;
}
.md-content hr {
  border: none;
  border-top: 1px solid #e5e5e5;
  margin: 1.6rem 0;
}
.md-content table {
  border-collapse: collapse;
  width: 100%;
  margin: 12px 0;
  font-size: 0.9rem;
}
.md-content th, .md-content td {
  border: 1px solid var(--line);
  padding: 8px 10px;
  text-align: left;
}
.md-content tr:nth-child(even) { background: #f9fafb; }
.md-content img {
  max-width: 100%;
  height: auto;
  border-radius: 10px;
  border: 1px solid var(--line);
  background: #fff;
}
.grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
}
.card {
  background: var(--card);
  border: 1px solid var(--line);
  border-radius: 10px;
  overflow: hidden;
}
.card img {
  width: 100%;
  display: block;
  background: #fff;
}
.cap {
  padding: 10px 12px;
  border-top: 1px solid var(--line);
  font-size: 0.9rem;
  color: #374151;
}
.cap code { color: var(--muted); font-size: 0.82rem; }
.note {
  margin-top: 16px;
  padding: 10px 12px;
  background: #eef2ff;
  border: 1px solid #c7d2fe;
  border-radius: 10px;
  color: #374151;
  font-size: 0.9rem;
}
.footer-repro {
  margin-top: 1.25rem;
  padding: 1rem 0 1.25rem 0;
  border-top: 1px solid #e2e8f0;
  text-align: left;
  color: #4a5568;
  font-size: 0.92rem;
  line-height: 1.55;
  overflow-wrap: anywhere;
}
.footer-strip {
  margin-top: 0.5rem;
  padding: 1rem 1.15rem;
  background: #f7fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  color: #718096;
  font-size: 0.88rem;
  line-height: 1.5;
  text-align: left;
  overflow-wrap: anywhere;
}
.footer-strip a { color: #2d3748; font-weight: 600; word-break: break-word; }
@media (max-width: 900px) {
  .grid { grid-template-columns: 1fr; }
}
@media (max-width: 640px) {
  body { padding: 0 12px; margin: 16px auto; }
  .paper-container { padding: 24px 16px; border-top-width: 6px; }
}
"""


def _strip_leading_h1_pair(text: str) -> str:
    """Remove the first two top-level markdown titles (already shown in HTML header)."""
    lines = text.splitlines()
    i = 0
    removed = 0
    while i < len(lines) and removed < 2:
        if lines[i].strip() == "":
            i += 1
            continue
        if lines[i].startswith("# ") and not lines[i].startswith("## "):
            removed += 1
            i += 1
            continue
        break
    while i < len(lines) and lines[i].strip() == "":
        i += 1
    return "\n".join(lines[i:]).lstrip()


def main() -> None:
    parser = argparse.ArgumentParser(description="Build merged v7+v8 manuscript HTML.")
    parser.add_argument(
        "--input",
        default="papers_final/04_Ripple_Rigidity_Audit/version_01/【0】_Ripple_Rigidity_Audit/files/07_Manuscript_Merged_v7_v8_Bilingual.md",
    )
    parser.add_argument(
        "--output",
        default="papers_final/04_Ripple_Rigidity_Audit/version_01/【0】_Ripple_Rigidity_Audit/files/08_Manuscript_Merged_v7_v8_Bilingual.html",
    )
    parser.add_argument(
        "--github",
        default="https://github.com/tomnattle/chain-explosion-model",
        help="Repository URL shown in metadata.",
    )
    args = parser.parse_args()

    in_path = Path(args.input)
    out_path = Path(args.output)
    text = in_path.read_text(encoding="utf-8")
    text = _strip_leading_h1_pair(text)
    text = text.replace("\\[", "$$").replace("\\]", "$$")

    body = markdown.markdown(text, extensions=["extra", "tables", "toc"])

    html = f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Ripple Reality — Merged v7+v8 Manuscript</title>
  <style>{PAPER_CSS}</style>
  <script>
    window.MathJax = {{
      tex: {{ inlineMath: [['$', '$'], ['\\\\(', '\\\\)']], displayMath: [['$$', '$$'], ['\\\\[', '\\\\]']] }},
      svg: {{ fontCache: 'global' }}
    }};
  </script>
  <script defer src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-svg.js"></script>
</head>
<body>
  <div class="paper-container">
    <header class="main-title-block">
      <h1>Ripple Reality: Merged Audit Manuscript (v6+v7+v8)</h1>
      <h1>Ripple Reality：合并审计稿（v6+v7+v8）</h1>
      <p class="sub">Includes v6 baseline, v7 rigidity metrics, the same audit-chain figure grid as <code>v7.html</code>, and the v8 deep-quantum figure panel. / 含 v6 基线、v7 刚性指标、与 <code>v7.html</code> 同源的审计链图阵、以及 v8 深水图像面板。</p>
    </header>
    <div class="metadata">
      <strong>Source markdown / 源稿：</strong> <code>{in_path.as_posix()}</code><br>
      <strong>Companion figure manuscript / 图文姊妹篇：</strong> <code>v7.html</code>（同目录）<br>
      <span class="meta">
        <strong>GitHub / 仓库：</strong>
        <a href="{args.github}" rel="noopener noreferrer" target="_blank">{args.github}</a><br>
        Run figure and audit scripts from repository root. / 请在仓库根目录运行作图与审计脚本。
      </span>
    </div>
    <div class="md-content">
      {body}
    </div>
    <div class="footer-repro">
      <strong>Rebuild / 重建 HTML：</strong>
      <code>python scripts/explore/ripple_quantum_tests/build_merged_v7_v8_html.py</code>
    </div>
    <div class="footer-strip">
      <strong>Manuscript folder / 论文目录：</strong> <code>papers_final/04_Ripple_Rigidity_Audit</code><br>
      <strong>v7 artifacts / v7 产物：</strong> <code>artifacts/ripple_quantum_tests_v7_three/</code><br>
      <strong>v8 artifacts / v8 产物：</strong> <code>artifacts/ripple_quantum_tests_v8_unify/</code>
    </div>
  </div>
</body>
</html>
"""
    out_path.write_text(html, encoding="utf-8")
    print(f"Wrote HTML: {out_path.as_posix()}")


if __name__ == "__main__":
    main()

