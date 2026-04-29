# BELL_AUDIT_REPORT v2 (Aggressive)

- v1 is preserved unchanged.
- synthetic N per seed: 50000

## Baseline (point kernel, uniform sampling)
- S_mean=-1.999245 ± 0.018213

## Exp1 Geometry cap stress
- cap=12.0°: S=-1.987726 ± 0.013824, delta_vs_base=0.011519
- cap=25.0°: S=-1.957990 ± 0.010456, delta_vs_base=0.041255
- cap=35.0°: S=-1.904304 ± 0.012982, delta_vs_base=0.094941

## Exp2 Sampling bias stress
- bias_z=0.25: S=-1.997337 ± 0.016166, delta_vs_base=0.001908
- bias_z=0.45: S=-1.998011 ± 0.013806, delta_vs_base=0.001234

## Exp3 NIST window track
- source: D:\workspace\golang\nakama\chain-explosion-model\artifacts\bell_window_scan_v1\WINDOW_SCAN_V1.csv
- window=0.0: S=2.336276, pairs=136632
- window=1.0: S=2.564983, pairs=137498
- window=3.0: S=2.733722, pairs=139158
- window=5.0: S=2.797681, pairs=140817
- window=9.0: S=2.836638, pairs=143964
- window=11.0: S=2.848281, pairs=145572
- window=15.0: S=2.839387, pairs=148670

## Readout
- If geometry/bias deltas approach window-driven deltas, model-mismatch explanation gains strength.
- If window effect dominates by orders of magnitude, pairing remains the primary sensitivity axis.