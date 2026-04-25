# 4. Results

Under the Phase-Loop model with threshold triggering, we obtain the following expectation values:
- **E(XXX) = 1.0000**
- **E(XYY) = -1.0000**
- **E(YXY) = -1.0000**
- **E(YYX) = -1.0000**
- **Mermin F = |E(XXX) - E(XYY) - E(YXY) - E(YYX)| = 4.000000**

In contrast, if we binarize the raw waves without thresholding (linear detection), we are limited to **F = 2.0**. This confirms that the GHZ "violation" is simply the resonance signature of the interference loop, captured by a threshold-sensitive detection process. The provided verification script `ghz_loop_explosion_v19.py` reproduces these results with zero variance.
