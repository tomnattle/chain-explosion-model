#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ast
import json
import re
from pathlib import Path


DICT_PATTERN = re.compile(r"\{[^{}]{10,}\}")
BIN_KEY_PATTERN = re.compile(r"^[01]+$")


def _extract_text_blocks(nb: dict) -> list[str]:
    blocks: list[str] = []
    for cell in nb.get("cells", []):
        src = cell.get("source", [])
        if isinstance(src, list):
            blocks.append("".join(src))
        elif isinstance(src, str):
            blocks.append(src)
        for out in cell.get("outputs", []):
            data = out.get("data", {})
            text_plain = data.get("text/plain")
            if isinstance(text_plain, list):
                blocks.append("\n".join(text_plain))
            elif isinstance(text_plain, str):
                blocks.append(text_plain)
            txt = out.get("text")
            if isinstance(txt, list):
                blocks.append("\n".join(txt))
            elif isinstance(txt, str):
                blocks.append(txt)
    return blocks


def _is_binary_count_dict(obj: object) -> bool:
    if not isinstance(obj, dict) or not obj:
        return False
    k0 = next(iter(obj.keys()))
    if not isinstance(k0, str):
        return False
    bitlen = len(k0)
    if bitlen <= 0:
        return False
    for k, v in obj.items():
        if not isinstance(k, str) or len(k) != bitlen or not BIN_KEY_PATTERN.match(k):
            return False
        if not isinstance(v, int):
            return False
    return True


def extract_count_candidates(notebook_path: Path) -> list[dict]:
    nb = json.loads(notebook_path.read_text(encoding="utf-8"))
    blocks = _extract_text_blocks(nb)
    candidates: list[dict] = []
    for b in blocks:
        for m in DICT_PATTERN.finditer(b):
            chunk = m.group(0)
            try:
                obj = ast.literal_eval(chunk)
            except Exception:
                continue
            if _is_binary_count_dict(obj):
                bitlen = len(next(iter(obj.keys())))
                total = int(sum(obj.values()))
                p00 = float(obj.get("0" * bitlen, 0) / total) if total else 0.0
                p11 = float(obj.get("1" * bitlen, 0) / total) if total else 0.0
                candidates.append(
                    {
                        "bitlen": bitlen,
                        "total_counts": total,
                        "p_all_zero": p00,
                        "p_all_one": p11,
                        "counts": obj,
                    }
                )
    # deduplicate by (bitlen, totals, sorted items hash)
    uniq = {}
    for c in candidates:
        key = (c["bitlen"], c["total_counts"], tuple(sorted(c["counts"].items())))
        uniq[key] = c
    out = list(uniq.values())
    out.sort(key=lambda x: (x["bitlen"], x["total_counts"]), reverse=True)
    return out


def expand_counts_to_shots(counts: dict[str, int], basis: str, project_to_3bits: bool = False) -> list[dict]:
    rows: list[dict] = []
    for bitstr, n in counts.items():
        out = bitstr[:3] if project_to_3bits else bitstr
        for _ in range(int(n)):
            rows.append({"measurement_basis": basis, "outcome": out})
    return rows


def main() -> None:
    ap = argparse.ArgumentParser(description="Extract IBM GHZ counts from notebook")
    ap.add_argument("--notebook", required=True, type=str)
    ap.add_argument("--out-dir", required=True, type=str)
    args = ap.parse_args()

    nb_path = Path(args.notebook)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    cands = extract_count_candidates(nb_path)
    (out_dir / "IBM_GHZ_COUNT_CANDIDATES.json").write_text(json.dumps(cands, indent=2), encoding="utf-8")

    three_qubit = [c for c in cands if c["bitlen"] == 3]
    selected = max(three_qubit, key=lambda x: x["total_counts"]) if three_qubit else None
    projected_source = None
    if selected is None:
        larger = [c for c in cands if c["bitlen"] > 3]
        if larger:
            projected_source = min(larger, key=lambda x: x["bitlen"])
            selected = projected_source

    summary = {
        "notebook": str(nb_path),
        "n_candidates_total": len(cands),
        "n_candidates_3qubit": len(three_qubit),
        "selected_3qubit": selected,
        "projection_used": projected_source is not None,
        "projection_note": "Used first 3 bits from smallest available >3 qubit result."
        if projected_source is not None
        else "",
        "status": "OK" if selected else "NO_3Q_OR_PROJECTABLE_DATA_FOUND",
    }
    (out_dir / "IBM_GHZ_EXTRACTION_SUMMARY.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    if selected:
        project = bool(projected_source is not None)
        strict_shots = expand_counts_to_shots(selected["counts"], basis="ZZZ", project_to_3bits=project)
        proxy_shots = expand_counts_to_shots(selected["counts"], basis="XXX", project_to_3bits=project)
        (out_dir / "IBM_GHZ_REAL_DATA_STRICT.json").write_text(
            json.dumps({"shots": strict_shots}, indent=2), encoding="utf-8"
        )
        (out_dir / "IBM_GHZ_REAL_DATA_PROXY_XXX.json").write_text(
            json.dumps({"shots": proxy_shots}, indent=2), encoding="utf-8"
        )

    print("wrote", out_dir / "IBM_GHZ_COUNT_CANDIDATES.json")
    print("wrote", out_dir / "IBM_GHZ_EXTRACTION_SUMMARY.json")
    if selected:
        print("wrote", out_dir / "IBM_GHZ_REAL_DATA_STRICT.json")
        print("wrote", out_dir / "IBM_GHZ_REAL_DATA_PROXY_XXX.json")


if __name__ == "__main__":
    main()

