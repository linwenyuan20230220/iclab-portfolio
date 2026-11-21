# Low-Power Accelerator with Clock Gating and Sequential Equivalence Checking

[中文版](README.zh-TW.md)

ICLAB Lab 08, Spring 2026 · UMC 180 nm · Design Compiler · PrimeTime PX · JasperGold SEC

**Result:** passed all checks, including gate-level simulation and both JasperGold SEC runs. Clock gating cut total power by **36%**, from 4.30 mW to 2.74 mW. Score 92.77, ranked **31 / 145**.

## The design

The accelerator computes a two-stage coupling layer on 4 × 4 matrices, as in invertible neural networks. It supports two tasks:

- **Forward:** each stage runs a matrix multiplication with modulo 15 + 1 and another with modulo 256. It then applies an element-wise (Hadamard) multiplication and a bitwise XOR.
- **Backward:** runs the same stages in reverse, replacing each multiplication with an element-wise division.

All inputs arrive serially over 97 cycles and the two 4 × 4 results stream out over 32 cycles.

Constraints:

- fixed 15 ns clock
- latency of at most 200 cycles
- cell area of at most 600,000 µm²
- no memories and no DesignWare IP
- no latches other than the clock-gating latches

## Clock gating

I wrote two versions of the same RTL:

- `LAB8_DESIGN_wocg`, without clock gating
- `LAB8_DESIGN`, which gates register clocks through `GATED_OR` clock-gating cells controlled by a `cg_en` input

The two versions had to stay identical except for the gating logic. The specification required at least a 10% power reduction with gating on.

The idea is simple: a register that is not going to change does not need a clock edge. In a design like this, most registers only need to load during certain phases, such as input collection, one compute stage, or output. Gating their clocks outside those phases removes the clock and flip-flop internal power they would otherwise burn every cycle.

| | Without gating | With gating |
| --- | --- | --- |
| Total power (PTPX) | 4.30 mW | 2.74 mW (−36%) |

The lab's figure of merit was latency × power² × area, so power counted twice.

## Proving the two versions are equivalent

Simulation can show that the gated design passes the test patterns, but not that it behaves like the ungated design in every case.

So I ran **sequential equivalence checking (SEC)** in JasperGold. It formally proves that `out_valid` and `out_data` of the two RTL versions match for every input sequence.

A combinational equivalence checker (like Formality or Conformal LEC) needs registers that map one-to-one between the two designs. Clock gating changes when registers update, so a sequential proof is needed instead. Both SEC runs passed with both output assertions proven.

## What I took from it

- **Fanout of gated clocks:** clock gating needs care with how many flip-flops share one gated clock. A gating signal that drives too many flops can show up as unknown (X) values in gate-level simulation even when RTL simulation passes.
- **Equivalence checking:** it is the right tool whenever a change should not alter function, such as clock gating, retiming or an ECO.

---

RTL, specifications, test patterns and library files are not published (see the [repository README](../README.md)).
