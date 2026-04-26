#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MD_PATH = ROOT / "01_Ripple_Joint_Audit_ZH.md"
SUBMISSION_MD_PATH = ROOT / "02_Submission_Abstract_Intro_Table_CoverLetter.md"
FIG_DIR = ROOT / "figures"
HTML_PATH = ROOT / "03_Ripple_Joint_Audit_ZH.html"


def read_markdown(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def md_to_simple_html(md: str) -> str:
    lines = md.splitlines()
    html = []
    in_ul = False
    in_code = False
    in_math_block = False
    math_lines: list[str] = []
    h2_count = 0
    for ln in lines:
        if ln.strip().startswith("```"):
            if in_code:
                html.append("</code></pre>")
            else:
                html.append("<pre><code>")
            in_code = not in_code
            continue
        if in_code:
            html.append(
                ln.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            )
            continue

        s = ln.strip()
        if s == r"\[":
            if in_ul:
                html.append("</ul>")
                in_ul = False
            in_math_block = True
            math_lines = []
            continue
        if in_math_block:
            if s == r"\]":
                math_expr = "\n".join(math_lines)
                html.append(f"<div class=\"math-block\">\\[\n{math_expr}\n\\]</div>")
                in_math_block = False
                math_lines = []
            else:
                math_lines.append(ln)
            continue

        if not s:
            if in_ul:
                html.append("</ul>")
                in_ul = False
            html.append("<p></p>")
            continue
        if s.startswith("# "):
            if in_ul:
                html.append("</ul>")
                in_ul = False
            html.append(f"<h1 id=\"sec-top\">{s[2:]}</h1>")
        elif s.startswith("## "):
            if in_ul:
                html.append("</ul>")
                in_ul = False
            h2_count += 1
            sec_id = f"sec-{h2_count}"
            html.append(f"<h2 id=\"{sec_id}\" class=\"section-break\">{s[3:]}</h2>")
        elif s.startswith("### "):
            if in_ul:
                html.append("</ul>")
                in_ul = False
            html.append(f"<h3>{s[4:]}</h3>")
        elif s.startswith("- "):
            if not in_ul:
                html.append("<ul>")
                in_ul = True
            html.append(f"<li>{s[2:]}</li>")
        elif re.match(r"^\d+\.\s", s):
            if in_ul:
                html.append("</ul>")
                in_ul = False
            html.append(f"<p>{s}</p>")
        else:
            if in_ul:
                html.append("</ul>")
                in_ul = False
            html.append(f"<p>{s}</p>")
    if in_ul:
        html.append("</ul>")
    if in_math_block and math_lines:
        math_expr = "\n".join(math_lines)
        html.append(f"<div class=\"math-block\">\\[\n{math_expr}\n\\]</div>")
    return "\n".join(html)


def build_html(md: str) -> str:
    body = md_to_simple_html(md)
    toc = build_toc(md)
    figs = [
        "fig_joint_2x2_default.png",
        "fig_branch_metrics.png",
        "fig_stress_2d_demo.png",
        "fig_v6_pipeline_schematic.png",
    ]
    fig_html = []
    for f in figs:
        p = FIG_DIR / f
        if p.exists():
            fig_html.append(
                f'<div class="fig"><img src="figures/{f}" alt="{f}"><div class="cap">{f}</div></div>'
            )
    timestamp = dt.datetime.now().strftime("%Y-%m-%d %H:%M")
    return f"""<!doctype html>
<html lang="zh">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Ripple Joint Audit v6</title>
  <style>
    body {{ font-family: Arial, 'Microsoft YaHei', sans-serif; margin: 2rem auto; max-width: 980px; line-height: 1.6; color: #1f2937; }}
    h1,h2,h3 {{ color: #0f172a; }}
    .cover {{ border: 1px solid #e5e7eb; border-radius: 10px; padding: 1rem 1.2rem; background: #f9fafb; margin-bottom: 1.2rem; }}
    .cover-title {{ margin: 0 0 0.5rem; font-size: 1.4rem; font-weight: 700; }}
    .cover-meta {{ margin: 0; color: #6b7280; font-size: 0.95rem; }}
    .toc {{ border-left: 4px solid #dbeafe; background: #f8fbff; padding: 0.6rem 0.9rem; margin: 1rem 0 1.4rem; }}
    .toc h2 {{ margin: 0.1rem 0 0.5rem; font-size: 1.05rem; }}
    .toc ul {{ margin: 0.2rem 0 0.1rem 1.2rem; padding: 0; }}
    .toc a {{ text-decoration: none; color: #1d4ed8; }}
    .toc a:hover {{ text-decoration: underline; }}
    pre {{ background: #f3f4f6; padding: 0.8rem; border-radius: 6px; overflow: auto; }}
    .math-block {{ margin: 0.8rem 0; overflow-x: auto; }}
    .meta {{ color: #6b7280; font-size: 0.9rem; margin-bottom: 1rem; }}
    .figgrid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin: 1rem 0 1.5rem; }}
    .fig img {{ width: 100%; border: 1px solid #e5e7eb; border-radius: 6px; }}
    .cap {{ font-size: 0.85rem; color: #6b7280; margin-top: 0.35rem; }}
    @media (max-width: 900px) {{ .figgrid {{ grid-template-columns: 1fr; }} }}
    @media print {{
      body {{ max-width: none; margin: 0; color: #111827; }}
      .meta {{ margin-bottom: 0.5rem; }}
      .fig {{ break-inside: avoid; page-break-inside: avoid; }}
      .math-block {{ break-inside: avoid; page-break-inside: avoid; }}
      pre {{ white-space: pre-wrap; }}
      .cover {{ border: none; background: none; padding: 0; margin-bottom: 0.4rem; }}
      .toc {{ border: none; background: none; padding: 0; margin: 0.3rem 0 0.8rem; }}
      .section-break {{ break-before: page; page-break-before: always; }}
      h1, h2, h3 {{ break-after: avoid; page-break-after: avoid; }}
      @page {{ size: A4; margin: 15mm 12mm; }}
    }}
  </style>
</head>
<body>
  <div class="cover">
    <p class="cover-title">Ripple Joint Audit v6（可打印 HTML）</p>
    <p class="cover-meta">版本：v6-joint draft（审稿友好格式）</p>
    <p class="cover-meta">Generated at {timestamp}</p>
  </div>
  <div class="toc">
    {toc}
  </div>
  {body}
  <h2>主图（论文友好）</h2>
  <div class="figgrid">
    {''.join(fig_html)}
  </div>
</body>
<script>
  window.MathJax = {{
    tex: {{
      inlineMath: [['\\\\(', '\\\\)']],
      displayMath: [['\\\\[', '\\\\]']]
    }},
    options: {{
      skipHtmlTags: ['script', 'noscript', 'style', 'textarea', 'pre', 'code']
    }}
  }};
</script>
<script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
</html>
"""


def build_toc(md: str) -> str:
    sec = []
    h2_count = 0
    for ln in md.splitlines():
        s = ln.strip()
        if s.startswith("## "):
            h2_count += 1
            title = s[3:].strip()
            sec.append((f"sec-{h2_count}", title))
    if not sec:
        return "<h2>目录</h2><p>（无二级章节）</p>"
    items = "".join([f'<li><a href="#{sid}">{title}</a></li>' for sid, title in sec])
    return f"<h2>目录</h2><ul>{items}</ul>"


def compose_markdown(main_md: str, append_md: str | None) -> str:
    if not append_md:
        return main_md
    sep = "\n\n---\n\n## 附录 B：投稿文本包\n\n"
    return main_md.rstrip() + sep + append_md.lstrip()


def main() -> int:
    ap = argparse.ArgumentParser(description="Generate HTML publishable for ripple journal draft")
    ap.add_argument("--md", type=str, default=str(MD_PATH))
    ap.add_argument(
        "--append-submission-md",
        type=str,
        default=str(SUBMISSION_MD_PATH),
        help="Optional markdown file appended into final HTML. Use empty string to disable.",
    )
    ap.add_argument("--html", type=str, default=str(HTML_PATH))
    args = ap.parse_args()

    md_path = Path(args.md)
    append_path_raw = (args.append_submission_md or "").strip()
    append_path = Path(append_path_raw) if append_path_raw else None
    html_path = Path(args.html)

    md = read_markdown(md_path)
    append_md = None
    if append_path and append_path.exists():
        append_md = read_markdown(append_path)
    final_md = compose_markdown(md, append_md)
    html_path.write_text(build_html(final_md), encoding="utf-8")
    print("wrote", html_path)
    if append_path and not append_path.exists():
        print("skip append: file not found:", append_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

