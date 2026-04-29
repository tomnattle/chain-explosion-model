# Ripple v6 Identifiability Audit

- best loss: `0.00047929`
- best x: mu=1.550753, rho=2.350000, eta=0.077882, bw=3.005743e-05
- restart std: mu=0.008479, rho=0.000209, eta=0.003579
- profile dynamic range: mu=0.185126, rho=27.120311, eta=0.144335
- permutation floor(min): 1.596407 (delta=1.595927)
- bootstrap std: mu=0.017243, rho=0.000744, eta=0.004706
- checks: {"restart_tight": true, "profile_nonflat": true, "perm_degrades": true, "bootstrap_tight": true, "overall_anchor_supported": true}

## Reading rule
- If overall_anchor_supported=false, treat (mu,rho,eta) as potentially non-unique pseudo-anchors.
