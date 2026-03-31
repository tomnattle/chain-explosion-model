# Model Intuition

This document records the author's intuitive picture of the model. It is not a proof, not a final physical verdict, and not a replacement for the code or the archival results. Its purpose is narrower: to show what the model is trying to picture when it talks about propagation, measurement, and correlation.

## What Is Being Imagined

The underlying picture is not "a tiny particle flies through empty space along a fixed path." It is closer to "an excitation keeps triggering nearby medium-like states, and the visible propagation is the history of those triggers."

In that picture:

- what moves is not primarily a billiard-ball particle, but a chain of local triggering events
- each newly triggered point can in turn act like a fresh local source
- propagation is therefore closer to a branching, fan-like, or shell-like spread than to a single sharp trajectory
- different directions do not have to carry equal strength, so the spread can be anisotropic rather than perfectly circular

This is the visual and conceptual background behind the repository name "chain explosion."

## Propagation as Repeated Local Re-Emission

The author's intuition is that propagation should be thought of as repeated local re-emission or re-triggering.

One useful analogy is a stone skipping across water, but with an important twist: each contact point is not only a mark left behind, it is also a new place from which disturbance spreads outward again. In the model picture, the medium is not passive. Every arrival can become a new local launch point.

This does not imply that the code has already captured every part of that intuition with physical completeness. It only means that the code is trying to work in that direction: local updates, repeated neighborhood transfer, geometry-dependent spread, and loss during propagation.

## Why Measurement Matters So Much

Within this intuition, measurement is not a neutral readout. It is an intervention into an already propagating structure.

The author's picture is that measurement can do at least one or more of the following:

- absorb part of the propagating structure
- cut off further branching from a local region
- disturb phase-like relations that would otherwise support interference
- convert a still-spreading pattern into an irreversible recorded event

For that reason, the repository often treats measurement-like operations as local absorbers, masks, thresholds, or event-retention rules instead of as a purely abstract observation layer.

## How Correlation Is Viewed

The intuitive goal of the model is to explore whether some strong correlations can be pictured as consequences of shared origin plus propagation history, rather than as immediate evidence of a mysterious super-distance action.

That does not automatically prove such a picture is correct. It simply defines the direction of exploration:

- start from a common source structure
- let propagation remain local and explicit
- let measurement be a real intervention rather than a passive glance
- then inspect what kinds of patterns and correlations survive

## Boundary of This Document

This file should be read as an intuition note, not as a result note.

- For code and mechanisms, read the implementation files and the technical monograph.
- For archived CHSH / NIST work, read `battle_results/`.
- For formal claims and limits, prefer the project README and the closure documents over this note.

The role of this document is only to preserve the author's internal picture in a transparent and non-overstated way.
