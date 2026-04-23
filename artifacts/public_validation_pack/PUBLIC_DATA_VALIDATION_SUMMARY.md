# Public Data Validation Pack

## Data sources
- Delft 2015 Bell dataset (4TU): `data/delft_2015/bell_open_data.txt`
- Delft 2016 Bell dataset (4TU): `data/delft_2016/*.txt`
- NIST completeblind side stream: `data/nist_completeblind_side_streams.csv`

## Key numbers
- Delft valid trials: 245
- Delft S_std: 2.422500
- Delft S_alt: 2.439807
- Delft 2016 S_combined: 2.346431
- NIST S (window=0): 2.336276
- NIST S (window=15): 2.812912

## Figures
- `fig1_s_comparison.png`
- `fig2_delft_e_points.png`
- `fig3_nist_window_robustness.png`
- `fig4_sample_volume.png`

## Interpretation notes
- Delft public data provides 4 fixed CHSH settings, not a dense angle scan.
- NIST side-stream data allows sensitivity check on pairing-window assumptions.
- This pack emphasizes reproducible visuals over narrative-only claims.
