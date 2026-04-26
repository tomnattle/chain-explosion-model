# 2. Methodology: Post-Selection and Selection Tax

We model the GHZ setup using a medium-wave propagation model (`medium-v10`) with three local phase-locked sources. The audit protocol sweeps the gate strength ($gate\_k$) of a soft detector to measure the sensitivity of $F$ to data retention.

- **Selection Rule**: Events are only recorded if the interference amplitude exceeds a specific "Selection Tax" threshold.
- **Random Control**: For every gated result, we generate a random subsample with the same retention ratio to distinguish between mechanism-driven gains and statistical noise.

## 3. The Real Cost Curve

The transition from $F \approx 0$ to $F \approx 4.0$ is mapped as a function of the retention ratio $R$.

![GHZ Real Cost Curve](figures/V10_4_REAL_COST_CURVE.png)
*Figure 1: The GHZ Real Cost Curve (V10.4). The blue line represents the gated F values, while the green line represents the matched-retention random baseline. High correlation is strictly coupled to low data retention.*
