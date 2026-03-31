"""
nist_hdf5_layout_check.py
-------------------------
判定 NIST processed HDF5 是否兼容「并列 clicks/settings 网格」管（v1 side_streams）。

用法：
  python nist_hdf5_layout_check.py --hdf5 data/completeblind.hdf5
  python nist_hdf5_layout_check.py --hdf5 data/training.hdf5 --hdf5 data/completeblind.hdf5
"""

import argparse
import json
import os
import sys


def _require_h5py():
    try:
        import h5py
    except Exception:
        print("pip install h5py")
        sys.exit(1)
    return h5py


def describe_layout(path):
    h5py = _require_h5py()
    out = {"path": os.path.abspath(path), "exists": os.path.isfile(path)}
    if not out["exists"]:
        return out
    with h5py.File(path, "r") as h5:
        need = ["alice/clicks", "alice/settings", "bob/clicks", "bob/settings"]
        for k in need:
            if k not in h5:
                out[k] = None
            else:
                out[k] = int(h5[k].shape[0])
        if all(out.get(x) is not None for x in need):
            la, sa, lb, sb = (out["alice/clicks"], out["alice/settings"], out["bob/clicks"], out["bob/settings"])
            out["grid_side_streams_compatible"] = la == sa == lb == sb
        else:
            out["grid_side_streams_compatible"] = False
        for side in ("alice", "bob"):
            cg = "config/%s" % side
            if cg + "/radius" in h5:
                out["%s_radius" % side] = int(h5["%s/radius" % cg][()])
                out["%s_bitoffset" % side] = int(h5["%s/bitoffset" % cg][()])
                out["%s_pk" % side] = int(h5["%s/pk" % cg][()])
    return out


def main():
    ap = argparse.ArgumentParser(description="Check NIST HDF5 layout for grid converter")
    ap.add_argument("--hdf5", action="append", default=[], help="HDF5 path (repeatable)")
    ap.add_argument("--json", default="", help="optional write summary JSON path")
    args = ap.parse_args()
    if not args.hdf5:
        print("pass at least one --hdf5")
        return 1
    rows = [describe_layout(p) for p in args.hdf5]
    for r in rows:
        print(json.dumps(r, indent=2, ensure_ascii=False))
    if args.json:
        with open(args.json, "w", encoding="utf-8") as f:
            json.dump(rows, f, indent=2, ensure_ascii=False)
        print("wrote", args.json)
    return 0


if __name__ == "__main__":
    sys.exit(main())
