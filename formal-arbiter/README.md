# Formal Verification of a Round-Robin Arbiter

[中文版](README.zh-TW.md)

ICLAB Bonus Lab, Spring 2026 · SystemVerilog Assertions · JasperGold Formal

An 8-requester round-robin arbiter with a hidden bug was given as the design under test, together with a checker template bound to it and the input assumption. I completed the missing cover and assert properties, ran JasperGold, and used a failing assertion to find the bug.

## Approach

| Property type | Role | Examples in this lab |
| --- | --- | --- |
| `assume` (provided) | Constrains the environment | A request stays high until it is granted |
| `cover` | Shows a scenario is reachable, so the assumptions are not over-constraining | Grants issued to requesters 0 → 1 → … → 7 in consecutive cycles (covered at bound 8); requester 0 can wait 6 cycles after requester 1 is granted, but not 7 (proven unreachable) |
| `assert` | Must hold on every reachable state | While one grant is high, all others are low; at most one grant at a time (`$countones`) |

Covers come first on purpose. If an assumption is too strict, every assertion passes vacuously; a reachable cover proves the interesting behavior still exists.

## The fairness bug

Round-robin fairness for 8 requesters means a pending request is served within 8 cycles:

```systemverilog
assert property (req[0] |-> ##[0:7] gnt[0]);
```

JasperGold returned a counterexample: when requester 0 was the last client served and is the only one requesting, it is never granted again. The priority loop scanned offsets 1 to N−1 (`j < N`) and so never revisited the last-served client; with no grant, the last-served pointer never moved, and the arbiter deadlocked. The fix is `j <= N`, which checks the last-served client at the lowest priority.

## Takeaways

- Formal explores every legal input sequence, so it reaches corner cases that directed or random simulation can miss on a small block.
- A counterexample is a minimal-length waveform, which makes the root cause much faster to find than a failing long simulation.
- Cover properties are the guard against false confidence from over-constrained assumptions.

---

The checker source is not published because the course reuses this assignment. It is available to interviewers on request.
