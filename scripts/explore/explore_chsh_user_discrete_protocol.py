"""
User-specified discrete protocol (verbatim structure):

- Bob outcome space {1,3,5}, Alice outcome space {2,4,5} for the *draw*.
- CHSH "angles" are labels:
 a1=1, a2=2 for Alice settings
    b1=3, b2=5 for Bob settings

User's deterministic readout rule in their worked example:
- The *observed Alice value* equals the Alice setting label (a1 -> 1, a2 -> 2).
- The *observed Bob value* equals the Bob setting label (b1 -> 3, b2 -> 5).

Match score for CHSH product (mapped to +/-1 outcome):
  X = +1 if Alice observed in {2,4,5}, else -1
  Y is not used in their E; they define E as essentially X (or treat Y implicitly as +1).

Under their four cells, this yields S = 2 exactly (algebraically).

This file also includes a sanity check: standard CHSH uses  E(x,y) = E[ A_x * B_y ]
with BOTH parties binary. If you fold Bob into the conditioning only, you are not using the same object as textbook CHSH (even if the symbol "S" is reused).
"""

from __future__ import annotations


def match_alice(a_obs: int) -> int:
    return +1 if a_obs in (2, 4, 5) else -1


def main() -> None:
    # Deterministic mapping from settings to observed outcomes (as in user's derivation)
    cells = [
        ("E(a1,b1)", 1, 3, match_alice(1)),
        ("E(a1,b2)", 1, 5, match_alice(1)),
        ("E(a2,b1)", 2, 3, match_alice(2)),
        ("E(a2,b2)", 2, 5, match_alice(2)),
    ]

    # NOTE: user's E1..E4 are exactly the third column here (they did not introduce a separate Bob +/-1)
    e11 = cells[0][3]
    e12 = cells[1][3]
    e21 = cells[2][3]
    e22 = cells[3][3]

    s = e11 - e12 + e21 + e22

    print("user_discrete_protocol")
    for name, _a_set, _b_set, e in cells:
        print(f"  {name}: Alice_obs from setting, match -> {e:+d}")
    print()
    print(f"  E(a1,b1)={e11:+d}  E(a1,b2)={e12:+d}  E(a2,b1)={e21:+d}  E(a2,b2)={e22:+d}")
    print(f"  S = {e11} - ({e12}) + {e21} + {e22} = {s}")


if __name__ == "__main__":
    main()
