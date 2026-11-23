# Physical Design Algorithms in C++

[中文版](README.zh-TW.md)

NYCU Physical Design Automation (graduate course), Fall 2026 · C++17 · single-threaded · Linux

Three programming assignments, each a standalone C++ tool that reads a design, solves a core physical-design problem and writes a result that an official verifier checks.

| Lab | Problem | Approach |
| --- | --- | --- |
| [1](#lab-1--corner-stitching) | Layout database: tile plane with point finding and neighbor queries | Corner stitching with maximal horizontal space strips |
| [2](#lab-2--heterogeneous-3d-ic-partitioning) | Assign up to 100k cells to two stacked dies, minimizing cut nets | Multilevel hypergraph partitioning with constrained FM refinement |
| [3](#lab-3--fixed-outline-floorplanning) | Place up to 200 blocks in a fixed outline, minimizing wirelength under constraints | B\*-tree simulated annealing, then legalization and local search |

---

## Lab 1 — Corner Stitching

**Problem.** Build the layout plane for up to 25,000 non-overlapping rectangular blocks inside an outline of up to 200,000 × 200,000. Answer point-finding queries during insertion, and report how many block tiles and space tiles touch each block. Space tiles must always form **maximal horizontal strips**: no two space tiles side by side, and each as wide as possible.

**Approach.**

- Each tile stores its corners and four stitches (right-top, top-right, bottom-left, left-bottom), so every operation walks the plane locally instead of scanning all tiles.
- **Point finding** walks the stitches from the last visited tile: first vertically to the right row, then horizontally, repeating until the tile contains the point.
- **Block insertion**:
  1. Split the space tiles at the block's top and bottom edges.
  2. For every space tile the block crosses, from top to bottom, split off the parts left and right of the block.
  3. Merge the middle pieces into a single block tile.
  4. Merge the leftover space tiles vertically wherever they now line up, which restores the maximal-strip invariant.
- **Neighbor enumeration** walks along each edge of a block through the stitches.

---

## Lab 2 — Heterogeneous 3D-IC Partitioning

**Problem.** Model the netlist as a hypergraph with up to 100,000 cells and 200,000 nets, and assign every cell to the top or bottom die. The two dies use different libraries, so a cell has a different area on each die.

- **Objective:** minimize the number of nets that cross the two dies.
- **Hard constraints:** each die's area capacity, and a cell-count balance window.
- **Limit:** 60 seconds per case.

**Approach: multilevel partitioning, in the spirit of hMETIS.**

1. **Coarsening.** Group strongly connected cells into clusters level by level until about 150 nodes remain. Each cluster has caps on its cell count and on its area on each die, so the coarse problem stays legal. Very large nets are ignored when scoring clusters, because they say little about locality.
2. **Community guidance.** Some trials first run Louvain community detection on a clique expansion of the hypergraph (rings replace cliques for large nets to bound memory). The coarsening then stays inside communities.
3. **Initial partition.** At the coarsest level, several randomized trials target the balance bound, since slightly unequal sides often cut fewer nets.
4. **Uncoarsening with FM refinement.** Fiduccia–Mattheyses moves use gain buckets. A move may briefly leave the legal region by at most one cell, and each pass rolls back to the best prefix, ranked first by constraint violation and then by cut size.
5. **V-cycles.** The program re-coarsens around the best solution and runs a portfolio of strategies. It keeps the best legal result within a 20-second budget, and falls back to a greedy assignment by cell type if no legal partition appears.

**Result:** scored 94.89 / 100 and ranked 6 / 82 in the class, with the best cut size in the class on 2 of the 7 hidden cases.

---

## Lab 3 — Fixed-Outline Floorplanning

A simplified version of Problem C of the ICCAD 2026 CAD Contest (*FloorSet Challenge*, Intel).

**Problem.** Place up to 200 blocks inside a given outline with no overlap. Blocks come in three kinds:

- **Soft:** only the area is given; I choose an integer shape within a 1% area tolerance and an aspect ratio of at most 3.
- **Fixed-shape:** the width and height are given.
- **Preplaced:** the position is also given.

The objective is weighted centroid-to-centroid Manhattan wirelength to other blocks and border terminals. Two scored constraints apply:

- **MIB groups:** soft blocks in a group must share one shape.
- **Boundary and corner constraints:** a block must touch a given outline edge or corner.

The limit is 120 seconds on a single thread.

**Approach.**

1. **Soft-block shapes.** For each area, list the legal integer shapes that use the least area (about 0.99 × target), then sample about 40 aspect ratios. All members of an MIB group share one shape index, so **every MIB group is satisfied by construction**.
2. **Safety net.** A constructive legalizer builds a legal floorplan first. Boundary blocks go on their edges, and the rest are placed by skyline best fit, where soft blocks can take the exact width of a gap.
3. **Simulated annealing on a B\*-tree with contour packing.**
   - The contour is a linked list, so packing costs amortized O(1) per block.
   - Preplaced blocks are tree nodes. Overlap with them is a penalty instead of a hard push, which smooths the search landscape on tight cases.
   - The cost is wirelength / threshold + outline overflow + boundary penalty.
   - Annealing runs as repeated warm cooling cycles to reach a legal fit, then switches to wirelength annealing.
   - **Early rejection:** the acceptance threshold is drawn first, and packing stops as soon as the overflow already exceeds it.
   - Near-legal packings are repaired by dropping the overflowing blocks into internal holes.
4. **Repair and refinement.**
   - Snap blocks onto their required edges when the spot is free.
   - Reduce wirelength by sliding blocks toward the weighted median of their connections, swapping equal-size blocks, and reshaping soft blocks in place.
5. **Large-neighborhood search.** Ruin and recreate in absolute coordinates, including a targeted move that clears space on a required edge. A boundary constraint is given up for wirelength only when that moves the wirelength into the scoring band.
6. **Selection and self-check.** The final candidate is chosen by the real scoring formula. Before writing the output, the program re-checks all 8 legality rules. It computes wirelength exactly with doubled integer coordinates, because centroids can fall on half-units.

**Result on the public case** (50 blocks): legal floorplan meeting all 10 boundary constraints and all 4 MIB groups, with wirelength 289,294.5, about 1.0% above the TA's reference of 286,355.5. Verifier score on the course workstation: 18.97 / 20.

---

Source code is not published: the course checks code similarity across students and reuses its assignments. It is available to interviewers on request.
