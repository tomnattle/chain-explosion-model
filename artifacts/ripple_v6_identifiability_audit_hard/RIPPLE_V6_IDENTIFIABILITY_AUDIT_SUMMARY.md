# Ripple v6 Identifiability Audit

- best loss: `0.00001341`
- best x: mu=1.550113, rho=2.350000, eta=0.080125, bw=3.000015e-05
- restart std: mu=0.003820, rho=0.000232, eta=0.000494
- profile dynamic range: mu=0.210868, rho=27.120311, eta=0.192467
- permutation floor(min): 1.596407 (delta=1.596393)
- bootstrap std: mu=0.004750, rho=0.000366, eta=0.002230
- checks: {"restart_tight": true, "profile_nonflat": true, "perm_degrades": true, "bootstrap_tight": true, "overall_anchor_supported": true}

## Reading rule
- If overall_anchor_supported=false, treat (mu,rho,eta) as potentially non-unique pseudo-anchors.
