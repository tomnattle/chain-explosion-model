"""
Monte Carlo: set-to-set outcome mapping (|S_B|=|S_A|=3), no Bell/CHSH framing.

We use label space {1..6}, S_B={1,3,5}, S_A={2,4,5} as in the user's example.

Sampling rule "overlap_aware" (set mapping, not 1:1 pointwise):
  - b ~ Uniform(S_B)
  - If b is in the label overlap S_B ∩ S_A = {5}: bias toward matching that label.
  - Else: a ~ Uniform(S_A)  (any of Alice's three labels is allowed)

This produces nontrivial dependence between b and a while respecting that Bob in S_B does not fix a unique Alice label.
"""

from __future__ import annotations

import math
import random


def pearson(xs: list[float], ys: list[float]) -> float:
    n = len(xs)
    if n < 2:
        return float("nan")
    mx = sum(xs) / n
    my = sum(ys) / n
    vx = sum((x - mx) ** 2 for x in xs)
    vy = sum((y - my) ** 2 for y in ys)
    if vx <= 0.0 or vy <= 0.0:
        return float("nan")
    cov = sum((xs[i] - mx) * (ys[i] - my) for i in range(n))
    return cov / math.sqrt(vx * vy)


def sample_alice_given_bob(b: int, s_a: set[int], overlap: set[int], p_match_if_overlap: float) -> int:
    """Non-1:1: when b not in overlap, Alice is uniform on S_A; when in overlap, stochastically match."""
    if b in overlap:
        if random.random() < p_match_if_overlap:
            return b
        pool = list(s_a - {b})
        return random.choice(pool)
    return random.choice(list(s_a))


def main() -> None:
    rng = random.Random(0xC0FFEE)
    random.seed(0xC0FFEE)

    s_b = {1, 3, 5}
    s_a = {2, 4, 5}
    assert len(s_b) == len(s_a) == 3

    overlap = s_b & s_a
    p_match = 0.85  # strong but not deterministic tie on shared label 5

    n = 10_000
    bs: list[int] = []
    aas: list[int] = []

    hits = 0  # a in S_A while b in S_B (should be 100% by construction)
    match_shared = 0  # a == b and b in overlap

    for _ in range(n):
        b = rng.choice(list(s_b))
        a = sample_alice_given_bob(b, s_a, overlap, p_match)
        bs.append(b)
        aas.append(a)
        hits += int(a in s_a)
        if b in overlap and a == b:
            match_shared += 1

    rho = pearson([float(x) for x in bs], [float(y) for y in aas])

    # Also report a bounded "agreement score" in [-1,1] tailored to this label space:
    # +1 if (b,a) is in allowed Cartesian shadow; we always sample a in S_A so this is 1.
    # More informative: fraction of time Alice picks the overlap label when Bob is in overlap.
    bob_in_overlap = sum(1 for b in bs if b in overlap)
    alice_eq_b_when_overlap = sum(1 for b, a in zip(bs, aas) if b in overlap and a == b)

    print("set_mapping_sim")
    print(f"  trials          = {n}")
    print(f"  |S_B|, |S_A|     = {len(s_b)}, {len(s_a)}")
    print(f"  S_B             = {sorted(s_b)}")
    print(f"  S_A             = {sorted(s_a)}")
    print(f"  overlap         = {sorted(overlap)}")
    print(f"  p(match|overlap)= {p_match}")
    print()
    print(f"  P(a in S_A) = {hits / n:.6f}  (by construction ~1)")
    print(f"  Pearson(b, a)   = {rho:+.6f}")
    print()
    print("  overlap branch diagnostics:")
    print(f"    count(b in overlap)     = {bob_in_overlap}")
    print(f"    count(a==b | b overlap) = {alice_eq_b_when_overlap}")
    print(f"    empirical P(a=b | b in overlap) = {alice_eq_b_when_overlap / max(bob_in_overlap, 1):.6f}")

    # Spearman-like monotonic tie: rank correlation not computed (keep deps at stdlib only).


if __name__ == "__main__":
    main()
