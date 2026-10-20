# Formal Verification of a Round-Robin Arbiter

ICLAB Bonus Lab, Spring 2026 · SystemVerilog Assertions · JasperGold Formal

An 8-requester round-robin arbiter was given as the design under test. I wrote a checker module of SVA properties, attached it to the design with `bind`, and used JasperGold to explore and prove its behavior.

## Approach

| Property type | Role | Examples in this lab |
| --- | --- | --- |
| `assume` | Constrains the environment | A request stays high until it is granted |
| `cover` | Shows a scenario is reachable, so the assumptions are not over-constraining | Grants issued to requesters 0 → 1 → … → 7 in consecutive cycles; all requests raised between two grants to requester 0 |
| `assert` | Must hold on every reachable state | While one grant is high, all others are low; at most one grant at a time (`$countones`) |

Covers come first on purpose. If an assumption is too strict, every assertion passes vacuously; a reachable cover proves the interesting behavior still exists.

## The fairness bug

Round-robin fairness for 8 requesters means a pending request is served within 8 cycles:

```systemverilog
assert property (req[0] |-> ##[0:7] gnt[0]);
```

JasperGold returned a counterexample: a sequence of requests under which requester 0 waited longer than 8 cycles. Reading the counterexample waveform located the condition in the design that skipped requester 0, which violated the round-robin intent.

## Takeaways

- Formal explores every legal input sequence, so it reaches corner cases that directed or random simulation can miss on a small block.
- A counterexample is a minimal-length waveform, which makes the root cause much faster to find than a failing long simulation.
- Cover properties are the guard against false confidence from over-constrained assumptions.

---

The checker source is not published because the course reuses this assignment. It is available to interviewers on request.
