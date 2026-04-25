# METHODOLOGY: Normalization as the Secret Engine

To sit the case (坐实) for local realism, we compare two distinct data processing pipelines on the same local wave source.

### The Source Model
Our source emits a random phase $\lambda \in [0, 2\pi)$. 
Alice measures: $A(\lambda, a) = \cos(\lambda - a)$
Bob measures:   $B(\lambda, b) = -\cos(\lambda - b)$

### Pipeline A: The Binarized "Bell" Protocol
In this pipeline, results are truncated:
$Outcome_A = \text{sign}(A)$
$Outcome_B = \text{sign}(B)$
Correlation is computed as: $E = \text{mean}(Outcome_A \cdot Outcome_B)$
**Result**: $E$ is linear with respect to angle, and $S_{max} = 2.0$.

### Pipeline B: The Normalized "Audit" Protocol (NCC)
In this pipeline, the full wave amplitude is preserved and normalized:
$E = \frac{\langle A \cdot B \rangle}{\sqrt{\langle A^2 \rangle \langle B^2 \rangle}}$
**Result**: $E = \cos(a - b)$
**Result**: $S_{max} = 2\sqrt{2} \approx 2.828$.

### The Audit Conclusion
The "Tsirelson Bound" of 2.828 is not a quantum ceiling; it is the **Geometric Floor** for normalized harmonic oscillators. The reason quantum experiments "violate" Bell is that they use a physical mechanism (wave interference) that naturally follows the NCC logic, but they analyze it using an inequality designed for Pipeline A. This is a category error.
