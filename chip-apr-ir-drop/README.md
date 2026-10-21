# Chip-Level APR and IR-Drop Fix

[中文版](README.zh-TW.md)

ICLAB Lab 12, Spring 2026 · UMC 180 nm · Cadence Innovus · Rail analysis

This lab is back-end only: I took the synthesized netlist of my own **Lab 05 design**, a W4A8 diffusion-model denoiser, and turned it into a full chip with an I/O pad ring, SRAM macros, a power grid and a sign-off-clean layout. Then I ran power and rail analysis on the layout and fixed the IR drop it found.

## The design being placed

The Lab 05 accelerator denoises a 64 × 64 grayscale image for 1–7 iterations. Each iteration runs a down-sampling convolution, a transformer block (self-attention and a feed-forward network), an up-sampling convolution and an interpolation step. Weights are 4-bit and activations 8-bit, and both are stored in on-chip SRAM, so the floorplan has to accommodate several hard macros.

## Flow

1. **I/O plan:** wrote `CHIP.io` and the pad shell, with 9 core-power pad pairs (3 on the right side, 2 on each other side), 4 I/O-power pairs (one per side), corner pads, and core-power pads kept away from the corners.
2. **Floorplan:** core-to-I/O spacing above 100 µm on every side, with all SRAMs inside the core.
3. **Power plan:** core ring with 9 µm wires, wire groups and interleaving with at least 5 pairs per side, and horizontal/vertical stripes no more than 200 µm apart.
4. **Place, CTS, route** at a 14.6 ns clock, then post-route optimization to non-negative setup and hold slack with zero DRVs.
5. **Verification:** geometry (DRC) and connectivity (LVS) clean after core fillers, and a post-layout simulation with no timing violations and the same latency as gate level. The design passed the lab demo.
6. **Power and rail analysis** in Innovus to map IR drop across the core.

## The IR-drop fix

The sign-off limit was a worst-case IR drop of 50 mV. The first rail analysis showed **70 mV**, concentrated on one side of the core. Three changes brought it to **43 mV**, inside the limit:

| Change | Why it helps |
| --- | --- |
| Added core-power pad pairs on the side where the drop was worst (that side now has 3 pairs) | Shortens the current path from the supply into the hot region |
| Ensured at least two horizontal stripes run between neighboring SRAMs | Macros block the regular stripe pattern, so the cells between them were fed through long, narrow paths |
| Moved the SRAMs toward the core boundary | Puts the largest current draw next to the power ring instead of in the middle of the core |

The general lesson: SRAM macros are both large current sinks and obstacles to the power grid. Where they sit decides where the grid is weakest, so macro placement and stripe planning have to be done together.

---

Layout files, netlists and screenshots are not published because they contain foundry library data. Details are available to interviewers on request.
