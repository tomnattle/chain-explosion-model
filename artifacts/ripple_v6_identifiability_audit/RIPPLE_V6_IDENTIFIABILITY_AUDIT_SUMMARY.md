# Ripple v6 Identifiability Audit

- best loss: `0.00069224`
- best x: mu=1.536751, rho=2.350000, eta=0.078226, bw=3.001880e-05
- restart std: mu=0.006731, rho=0.000002, eta=0.003205
- profile dynamic range: mu=0.192945, rho=6.100460, eta=0.180577
- permutation floor(min): 1.613912 (delta=1.613220)
- bootstrap std: mu=0.008130, rho=0.000428, eta=0.005055
- checks: {"restart_tight": true, "profile_nonflat": true, "perm_degrades": true, "bootstrap_tight": true, "overall_anchor_supported": true}

## Reading rule
- If overall_anchor_supported=false, treat (mu,rho,eta) as potentially non-unique pseudo-anchors.
