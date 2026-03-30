"""
convert_nist_hdf5_to_events_csv.py
----------------------------------
Convert Bell-test HDF5 data into locked-protocol CSV:
  side,t,setting,outcome

Supports 3 strategies:
1) direct_fields
   HDF5 already contains arrays for side/time/setting/outcome.
2) timetag_channels
   Reconstruct events from per-side timetag streams (channel + time).
3) nist_hdf5_grid
   NIST processed HDF5: parallel alice/bob clicks (uint16 one-hot slot) + settings (uint8).
   Use emit_mode=side_streams so A/B times differ and coincidence window changes pairing.

Usage examples:
  python convert_nist_hdf5_to_events_csv.py --hdf5 data/run.hdf5 --config nist_convert_config.json --inspect
  python convert_nist_hdf5_to_events_csv.py --hdf5 data/run.hdf5 --config nist_convert_config.json --output data/events.csv
"""

import argparse
import csv
import json
import os
import sys


def _require_h5py():
    try:
        import h5py
    except Exception:
        print("h5py not installed. Install with: pip install h5py")
        raise
    return h5py


def _read_dataset(h5, path):
    if path not in h5:
        raise KeyError("missing dataset path: %s" % path)
    return h5[path][()]


def inspect_hdf5(h5, head=140):
    entries = []

    def visit(name, obj):
        kind = "dataset" if hasattr(obj, "shape") else "group"
        shape = str(getattr(obj, "shape", ""))
        dtype = str(getattr(obj, "dtype", ""))
        entries.append((name, kind, shape, dtype))

    h5.visititems(visit)
    print("HDF5 entries (first %d):" % head)
    for i, e in enumerate(entries[:head], 1):
        print("%3d. %s | %s | %s | %s" % (i, e[0], e[1], e[2], e[3]))
    print("total entries:", len(entries))


def convert_direct_fields(h5, cfg):
    f = cfg["direct_fields"]
    side = _read_dataset(h5, f["side"]).astype(str)
    t = _read_dataset(h5, f["time"])
    setting = _read_dataset(h5, f["setting"])
    outcome = _read_dataset(h5, f["outcome"])

    n = min(len(side), len(t), len(setting), len(outcome))
    events = []
    for i in range(n):
        sd = str(side[i]).strip().upper()
        if sd not in ("A", "B"):
            continue
        s = int(setting[i])
        if s not in (0, 1):
            continue
        o = 1 if int(outcome[i]) >= 0 else -1
        events.append((sd, float(t[i]), s, o))
    return events


def _reconstruct_side_events(arr, mapping, col_channel, col_time, max_setting_age):
    """
    Build side events from timetag rows:
      detector channels -> outcomes
      setting marker channels -> active setting state
    """
    # Ensure 2D
    if len(arr.shape) != 2:
        raise ValueError("timetag dataset must be 2D, got shape=%s" % (arr.shape,))
    if arr.shape[1] <= max(col_channel, col_time):
        raise ValueError("dataset columns too small for configured indices")

    det_plus = set(mapping["detector_plus_channels"])
    det_minus = set(mapping["detector_minus_channels"])
    set0 = set(mapping["setting0_channels"])
    set1 = set(mapping["setting1_channels"])

    # sort by time
    idx = arr[:, col_time].argsort(kind="mergesort")
    rows = arr[idx]

    current_setting = None
    setting_time = None
    out = []

    for r in rows:
        ch = int(r[col_channel])
        tt = float(r[col_time])

        if ch in set0:
            current_setting = 0
            setting_time = tt
            continue
        if ch in set1:
            current_setting = 1
            setting_time = tt
            continue

        if ch in det_plus or ch in det_minus:
            # detector click can only become event if we have a recent setting marker
            if current_setting is None or setting_time is None:
                continue
            if max_setting_age > 0 and (tt - setting_time) > max_setting_age:
                continue
            outcome = 1 if ch in det_plus else -1
            out.append((tt, current_setting, outcome))

    return out


def _nist_slot_outcome(click_val, plus_slots, minus_slots):
    v = int(click_val)
    if v <= 0:
        return None
    k = v.bit_length() - 1
    if (1 << k) != v:
        return None
    if k in plus_slots:
        return 1
    if k in minus_slots:
        return -1
    return None


def convert_nist_hdf5_grid(h5, cfg, out_path, chunk=None):
    """
    Stream NIST bell-test HDF5 to CSV (low memory).

    emit_mode:
      side_streams: one row per detector click; t = grid index (float).
                    Enables strict vs wide coincidence in explore_chsh_experiment_alignment.
      joint_same_t: only indices with both alice and bob click; emit A and B with identical t.
                    (pairing then identical across windows — use only for sanity checks.)
    """
    import numpy as np

    def _outcome_lut(plus_slots, minus_slots):
        lut = np.full(65536, -999, dtype=np.int16)
        for p in plus_slots:
            if 0 <= p < 16:
                lut[1 << p] = 1
        for p in minus_slots:
            if 0 <= p < 16:
                lut[1 << p] = -1
        return lut

    m = cfg["nist_hdf5_grid"]
    apath = m["alice_clicks"]
    bpath = m["bob_clicks"]
    aset_p = m["alice_settings"]
    bset_p = m["bob_settings"]
    emit_mode = str(m.get("emit_mode", "side_streams")).strip()
    if chunk is None:
        chunk = int(m.get("chunk", 8000000))
    plus = set(int(x) for x in m.get("outcome_plus_slots", list(range(8))))
    minus = set(int(x) for x in m.get("outcome_minus_slots", list(range(8, 16))))
    lut = _outcome_lut(plus, minus)

    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    n_grid = int(h5[apath].shape[0])
    n_written = 0

    with open(out_path, "w", encoding="utf-8", newline="") as fout:
        w = csv.writer(fout)
        w.writerow(["side", "t", "setting", "outcome"])

        for start in range(0, n_grid, chunk):
            end = min(start + chunk, n_grid)
            ca = h5[apath][start:end]
            cb = h5[bpath][start:end]
            sa = h5[aset_p][start:end]
            sb = h5[bset_p][start:end]

            if emit_mode == "joint_same_t":
                msk = (ca[:] > 0) & (cb[:] > 0)
                idx = np.nonzero(msk)[0]
                for j in idx:
                    i = start + int(j)
                    oa = _nist_slot_outcome(int(ca[j]), plus, minus)
                    ob = _nist_slot_outcome(int(cb[j]), plus, minus)
                    if oa is None or ob is None:
                        continue
                    ssa, ssb = int(sa[j]), int(sb[j])
                    if ssa not in (1, 2) or ssb not in (1, 2):
                        continue
                    tt = float(i)
                    w.writerow(["A", tt, ssa - 1, oa])
                    w.writerow(["B", tt, ssb - 1, ob])
                    n_written += 2
            elif emit_mode == "side_streams":
                oa = lut[ca]
                ob = lut[cb]
                ok_a = (ca > 0) & (oa != -999) & ((sa == 1) | (sa == 2))
                ok_b = (cb > 0) & (ob != -999) & ((sb == 1) | (sb == 2))
                ja = np.nonzero(ok_a)[0]
                jb = np.nonzero(ok_b)[0]
                for j in ja:
                    jj = int(j)
                    w.writerow(["A", float(start + jj), int(sa[jj]) - 1, int(oa[jj])])
                    n_written += 1
                for j in jb:
                    jj = int(j)
                    w.writerow(["B", float(start + jj), int(sb[jj]) - 1, int(ob[jj])])
                    n_written += 1

            if emit_mode not in ("joint_same_t", "side_streams"):
                raise ValueError("unknown emit_mode: %s" % emit_mode)

            print("grid %d/%d rows, events written %d" % (end, n_grid, n_written))

    return n_written


def convert_timetag_channels(h5, cfg):
    m = cfg["timetag_channels"]
    col_channel = int(m.get("col_channel", 0))
    col_time = int(m.get("col_time", 1))
    max_setting_age = float(m.get("max_setting_age", 0.0))

    Aarr = _read_dataset(h5, m["alice_dataset"])
    Barr = _read_dataset(h5, m["bob_dataset"])

    Aevents = _reconstruct_side_events(
        Aarr, m["alice_mapping"], col_channel, col_time, max_setting_age
    )
    Bevents = _reconstruct_side_events(
        Barr, m["bob_mapping"], col_channel, col_time, max_setting_age
    )

    out = []
    for t, s, o in Aevents:
        out.append(("A", float(t), int(s), int(o)))
    for t, s, o in Bevents:
        out.append(("B", float(t), int(s), int(o)))
    return out


def write_csv(events, out_path):
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    # stable order by time
    events = sorted(events, key=lambda x: x[1])
    with open(out_path, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["side", "t", "setting", "outcome"])
        for row in events:
            w.writerow(row)


def main():
    parser = argparse.ArgumentParser(description="Convert NIST HDF5 to events CSV")
    parser.add_argument("--hdf5", required=True, help="input HDF5 path")
    parser.add_argument("--config", required=True, help="JSON conversion config")
    parser.add_argument("--output", default="data/events_from_hdf5.csv", help="output CSV path")
    parser.add_argument("--inspect", action="store_true", help="print HDF5 structure and exit")
    parser.add_argument(
        "--out-csv",
        default="",
        help="alias for --output (overrides if set)",
    )
    args = parser.parse_args()
    if args.out_csv:
        args.output = args.out_csv

    if not os.path.isfile(args.hdf5):
        print("missing hdf5:", args.hdf5)
        return 1
    if not os.path.isfile(args.config):
        print("missing config:", args.config)
        return 1

    h5py = _require_h5py()
    cfg = json.loads(open(args.config, "r", encoding="utf-8").read())
    strategy = cfg.get("strategy", "").strip()
    if strategy not in ("direct_fields", "timetag_channels", "nist_hdf5_grid"):
        print("invalid strategy:", strategy)
        return 1

    with h5py.File(args.hdf5, "r") as h5:
        if args.inspect:
            inspect_hdf5(h5)
            return 0
        if strategy == "nist_hdf5_grid":
            nw = convert_nist_hdf5_grid(h5, cfg, args.output)
            print("conversion complete.")
            print("strategy:", strategy)
            print("rows written:", nw)
            print("saved:", args.output)
            return 0 if nw > 0 else 2
        if strategy == "direct_fields":
            events = convert_direct_fields(h5, cfg)
        else:
            events = convert_timetag_channels(h5, cfg)

    if not events:
        print("no events reconstructed; check mapping config")
        return 2

    write_csv(events, args.output)
    print("conversion complete.")
    print("strategy:", strategy)
    print("events:", len(events))
    print("saved:", args.output)
    return 0


if __name__ == "__main__":
    sys.exit(main())

