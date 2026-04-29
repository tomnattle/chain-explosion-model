# Rho vs mu^2 constraint audit (v6 joint loss)

- mu_fixed = 1.5495
- mu^2 = 2.40095025

## Test 1: rho free (optimize rho, eta, bw)
{
  "optimum": {
    "mu": 1.5495,
    "rho": 2.349999999997348,
    "eta": 0.08000043378232771,
    "bw_ghz": 3.0000007786729616e-05
  },
  "loss": 1.5940599970415956e-05,
  "joint_pass": true,
  "rho_minus_mu2": -0.050950250002652187,
  "rel_err_rho_vs_mu2": 0.021220868696738796
}

## Test 2: rho = mu^2 (optimize eta, bw)
{
  "optimum": {
    "mu": 1.5495,
    "rho": 2.40095025,
    "eta": 0.045237430147375676,
    "bw_ghz": 6.041825614427648e-05
  },
  "loss": 0.22970541624921828,
  "joint_pass": false
}

## Test 3: scan rho
- rho at min loss in scan: `2.36095025`
- distance to mu^2: `-0.040000000000000036`

## Interpretation
- Test1: optimized rho is within 5% of mu^2 under free rho — consistent with rho≈mu^2 attractor in this toy objective.
- Test3: loss minimum in scan at rho=2.36095, not mu^2=2.40095 — rho=mu^2 is not the unique minimizer on this interval.