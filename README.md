# Digital IC Design Portfolio — Wen-Yuan Lin

[中文版](README.zh-TW.md)

M.S. student in Electronics Engineering (Digital Systems Group), National Yang Ming Chiao Tung University.
This repository documents selected projects from **NYCU IC Design Laboratory (ICLAB), Spring 2026**: what each design does, the architecture decisions behind it, and the results it reached.

| Project | Focus | Highlights |
| --- | --- | --- |
| [Dual-Core 16-bit RISC CPU](dual-core-cpu/) | RTL → GDSII, memory system, low power | 3 AXI4 masters, write-through D-cache, cross-core memory ordering, 3 → 1 SRAM for peak power, Innovus APR with clean DRC/LVS |
| [Triple-Clock-Domain Accelerator](cdc-accelerator/) | Clock domain crossing | Handshake synchronizer + 3 async FIFOs with Gray-coded pointers, SDRAM command controller, JasperGold CDC sign-off |
| [Round-Robin Arbiter Formal Verification](formal-arbiter/) | Assertion-based formal | SVA assume / cover / assert, fairness bug found from a counterexample |

**Tool flow:** VCS (RTL, gate-level, post-layout simulation) → Design Compiler (`compile_ultra`) → PrimeTime PX (power) → Cadence Innovus (APR) → JasperGold (formal, CDC). Technology: UMC 180 nm standard cells.

## What is and is not in this repository

This repository contains my own documentation and my own helper scripts only.

It intentionally does **not** include:

- **RTL source code.** ICLAB reuses its assignments across semesters, so I do not publish full solutions. The code is available to interviewers on request.
- **Course materials** such as specifications, testbenches and encrypted patterns, which belong to the course staff.
- **Process and memory-compiler files** such as standard-cell libraries, SRAM models, netlists, SDF and layout, which are covered by a foundry NDA.

## Contact

nycumonkyking.ee11@nycu.edu.tw
