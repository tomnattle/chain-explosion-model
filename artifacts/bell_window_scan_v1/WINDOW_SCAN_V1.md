# Bell Honest Window Scan v1

**Audit question:** Were the standard windows (15.0 and 10.0) cherry-picked to maximize S?

## Key Results

| Metric | Value |
|---|---|
| S at strict window (0) | 2.336276 |
| S at Round1 standard window (15) | 2.839387 |
| S at Round2 standard window (10) | 2.844568 |
| S_max across all 41 windows | 2.848281 |
| Window(s) where S is max | [11.0, 11.5] |
| Rank of Round1 window by S | #11 of 41 |
| Rank of Round2 window by S | #5 of 41 |

## Interpretation

Round1 window (w=15) ranks #11 out of 41 windows by S value. Round2 window (w=10) ranks #5 out of 41 windows by S value. S_max occurs at windows=[11.0, 11.5].

> CANNOT DETERMINE automatically. See rank above: if the chosen windows rank near the top, cherry-picking is plausible. If they rank in the middle or bottom, cherry-picking is unlikely.

## Note on S trend

If S increases monotonically with window size, then ANY large window will give high S.
In that case, choosing window=15 gives a high S not because it was cherry-picked
at the peak, but because larger windows systematically include more pairs with
higher apparent correlation. This is the coincidence loophole — and it is
exactly what the Bell paper reports as its core finding.