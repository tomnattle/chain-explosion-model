# Rho–mu joint_pass feasibility

- Fixed eta=0.08, optimize bw per point.
- 1D: mu=1.5495, rho in [2.1, 2.6], n=50.

## 1D widest feasible segment (rho)
- width: **0.000000**
- center: **2.350000** (lock rho=2.35)
- lock inside segment: True
- lock offset from center: 0.0

- rho=mu^2 at lock: 2.400950

## rho=mu^2 curve (in box, 80 samples, bw optimized)
- joint_pass count: 0 / 65

## 2D grid
- joint_pass fraction: 0.0500
- lock point joint_pass: **True**
- pass centroid (mu,rho): (1.5502381578947368, 2.3500000000000005)
- lock distance to centroid: 0.0007381578947367462
- mu spread of passing cells: 0.19999999999999996
- rho spread of passing cells: 0.0

## Files
- artifacts\rho_mu_feasibility_map\RHO_MU_FEASIBILITY.json
- artifacts\rho_mu_feasibility_map\feas_rho_vs_loss.png, artifacts\rho_mu_feasibility_map\feas_rho_vs_joint_pass.png, artifacts\rho_mu_feasibility_map\feas_mu_rho_heatmap.png