"""
Compare two different "E" definitions on the same 3x3 set-mapping samples.

1) "Alignment E" (storytelling / non-CHSH):
   +1 if Bob in S_B and Alice in S_A, else -1.
   Under sampling always inside S_B x S_A, this is identically +1 -> useless for discrimination.

2) CHSH-style E (standard):
   E(x,y) = mean( A_x * B_y ), with A_x, B_y in {+1,-1} determined from the SAME outcome (b,a)
   using setting-dependent +/- partitions of the 3 outcomes.

This script demonstrates:
- You can write down four arbitrary numbers and get S > 2; that does not violate physics,
  it means those four numbers are not guaranteed to come from ANY local/quantum joint model
  for the *standard* CHSH observables.
- For a fully specified local classical sampler (shared (b,a) each trial), S is computed from
  the implied joint; it does not magically exceed 2 just because outcomes live in 3x3 sets.
"""

from __future__ import annotations

import math
import random


def pearson_mean(xs: list[int], ys: list[int]) -> float:
    return sum(x * y for x, y in zip(xs, ys)) / len(xs)


def main() -> None:
    rng = random.Random(0xC0FFEE)

    s_b = {1, 3, 5}
    s_a = {2, 4, 5}

    # Outcome draws: "set mapping" satisfied by construction (product on allowed pairs).
    n = 200_000
    bs: list[int] = []
    as_: list[int] = []
    for _ in range(n):
        bs.append(rng.choice((1, 3, 5)))
        as_.append(rng.choice((2, 4, 5)))

    # --- (1) Alignment score (NOT E[AB]) ---
    align = [1 if (b in s_b and a in s_a) else -1 for b, a in zip(bs, as_)]
    e_align = sum(align) / n

    # --- (2) Standard +/- encodings on the SAME (b,a), four CHSH terms ---
    # Alice: a vs a'
    def a_a(a: int) -> int:
        return +1 if a == 5 else -1

    def a_ap(a: int) -> int:
        return +1 if a in (2, 4) else -1

    # Bob: b vs b'
    def b_b(b: int) -> int:
        return +1 if b == 5 else -1

    def b_bp(b: int) -> int:
        return +1 if b in (1, 3) else -1

    aa = [a_a(a) for a in as_]
    aap = [a_ap(a) for a in as_]
    bb = [b_b(b) for b in bs]
    bbp = [b_bp(b) for b in bs]

    e_ab = pearson_mean([x * y for x, y in zip(aa, bb)])
    e_abp = pearson_mean([x * y for x, y in zip(aa, bbp)])
    e_apb = pearson_mean([x * y for x, y in zip(aap, bb)])
    e_apbp = pearson_mean([x * y for x, y in zip(aap, bbp)])

    s_chsh = e_ab - e_abp + e_apb + e_apbp

    print("set_mapping_chsh_e_compare")
    print(f"  trials = {n}")
    print(f"  S_B = {sorted(s_b)}  S_A = {sorted(s_a)}")
    print()
    print("  (A) alignment 'E' = mean(+1 if in S_B x S_A else -1)")
    print(f"      = {e_align:.6f}   (always ~1 if you only sample allowed pairs)")
    print()
    print("  (B) CHSH E(x,y)=mean(A_x*B_y) with explicit +/- partitions on labels")
    print(f"      E(a,b)   = {e_ab:+.6f}")
    print(f"      E(a,b')  = {e_abp:+.6f}")
    print(f"      E(a',b)  = {e_apb:+.6f}")
    print(f"      E(a',b') = {e_apbp:+.6f}")
    print(f"      S = E(a,b)-E(a,b')+E(a',b)+E(a',b') = {s_chsh:+.6f}")
    print()
    print("  Note: CHSH |S|<=2 is a statement about a *specific* family of observables,")
    print(" not about the alignment score in (A).")


if __name__ == "__main__":
    main()
