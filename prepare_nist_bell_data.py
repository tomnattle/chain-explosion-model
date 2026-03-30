"""
prepare_nist_bell_data.py
-------------------------
下载 NIST Bell Test 公开 HDF5 数据（可选）并做结构探测。

示例：
  python prepare_nist_bell_data.py --preset training
  python prepare_nist_bell_data.py --preset completeblind
  python prepare_nist_bell_data.py --url <direct_hdf5_url> --output data/foo.hdf5
"""

import argparse
import os
import sys
import urllib.request


PRESETS = {
    "training": "https://s3.amazonaws.com/nist-belltestdata/belldata/processed_compressed/hdf5/2015_09_18/03_31_CH_pockel_100kHz.run4.afterTimingfix2_training.dat.compressed.build.hdf5",
    "completeblind": "https://s3.amazonaws.com/nist-belltestdata/belldata/processed_compressed/hdf5/2015_09_18/17_04_CH_pockel_100kHz.run.completeblind.dat.compressed.build.hdf5",
}


def download(url, out_path):
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    print("downloading:", url)
    print("to:", out_path)
    with urllib.request.urlopen(url) as r, open(out_path, "wb") as f:
        total = r.headers.get("Content-Length")
        total = int(total) if total and total.isdigit() else None
        got = 0
        while True:
            chunk = r.read(1024 * 1024)
            if not chunk:
                break
            f.write(chunk)
            got += len(chunk)
            if total:
                pct = 100.0 * got / total
                print("\rprogress: %.1f%% (%d / %d MB)" % (pct, got // (1024 * 1024), total // (1024 * 1024)), end="")
            else:
                print("\rprogress: %d MB" % (got // (1024 * 1024)), end="")
    print("\nfinished.")


def inspect_hdf5(path):
    try:
        import h5py  # optional dependency
    except Exception:
        print("h5py not installed; skip HDF5 introspection.")
        print("Install with: pip install h5py")
        return 0

    print("inspecting hdf5:", path)
    with h5py.File(path, "r") as h5:
        keys = []
        def visit(name, obj):
            if hasattr(obj, "shape"):
                keys.append((name, "dataset", str(obj.shape), str(getattr(obj, "dtype", ""))))
            else:
                keys.append((name, "group", "", ""))
        h5.visititems(visit)
    print("top entries (first 120):")
    for i, row in enumerate(keys[:120], 1):
        print("%3d. %s | %s | %s | %s" % (i, row[0], row[1], row[2], row[3]))
    print("total entries:", len(keys))
    return 0


def main():
    parser = argparse.ArgumentParser(description="Download and inspect NIST Bell HDF5")
    parser.add_argument("--preset", choices=tuple(PRESETS.keys()), default="training")
    parser.add_argument("--url", default="", help="override direct URL")
    parser.add_argument("--output", default="", help="output file path")
    parser.add_argument("--inspect-only", action="store_true")
    args = parser.parse_args()

    url = args.url or PRESETS[args.preset]
    out = args.output or os.path.join("data", os.path.basename(url))

    if not args.inspect_only:
        download(url, out)
    if not os.path.isfile(out):
        print("missing file:", out)
        return 1
    return inspect_hdf5(out)


if __name__ == "__main__":
    sys.exit(main())

