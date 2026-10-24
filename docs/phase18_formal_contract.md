# Exact evidence feasibility in the frozen window space

This is a label-assisted offline audit. Every statement below refers to coverage
of the supplied nonempty annotated word spans, not semantic answer sufficiency.

## Fixed objects

For a question, Phase 17 determines eight anchors and disjoint cells. Cell i has
session s_i, half-open interval [l_i,u_i), integer anchor a_i inside it, and capacity
c_i = u_i − l_i. In each selected session the cells partition the session's word
coordinates. The list of cells retains retrieval-rank order, which controls the
round-robin allocation. At budget B the unchanged allocator produces widths w_i(B).
All production budgets are at least eight, so every cell has a nonempty window.

A legal window is [x_i,x_i+w_i), with

\[
\max(l_i,a_i-w_i+1)\leq x_i\leq\min(a_i,u_i-w_i).
\]

Let G be the union of word positions from the original nonempty annotated turns.
Any zero-word turn contributes no position and follows the original exclusion
policy. The audit requires at least one nonempty annotated turn.

## Exact feasibility theorem

If an annotated session has no anchor, complete coverage is impossible at every
budget under this fixed anchor set. Otherwise define

\[
L_i=\min(\{a_i\}\cup(G\cap[l_i,u_i))),\qquad
U_i=1+\max(\{a_i\}\cup(G\cap[l_i,u_i))),\qquad r_i=U_i-L_i.
\]

The intersection is restricted to the same session as the cell. If it is empty,
the singleton anchor gives r_i=1. A legal collection covers every annotated word
if and only if w_i(B) ≥ r_i for every cell.

Necessity: a window in cell i must contain the anchor and all annotated positions
in that cell. Since it is contiguous, it must contain [L_i,U_i), requiring width
at least r_i. No other cell can cover a missing interior word in cell i because
the cells are disjoint. A gold turn crossing a cell boundary requires both parts.

Sufficiency: a length-w_i interval inside [l_i,u_i) that contains [L_i,U_i) exists
when r_i ≤ w_i ≤ c_i. Its allowable starts have nonempty intersection

\[
[\max(l_i,a_i-w_i+1,U_i-w_i),\ \min(a_i,u_i-w_i,L_i)].
\]

Choose a start in that intersection independently for each cell. The resulting
windows cover G, contain the original anchors and have exactly the prescribed
individual widths and total word cost. These windows are constructive witnesses.
When a width is too small, that cell and its required interval certify failure.

This is an exact maximum of the binary all-annotated-evidence score, over the
legal window product space. It is not a maximum of partial turn recall or answer
accuracy, and it is not a method that can choose its windows without labels.

## Minimum total budget theorem

The old allocator emits one word per active cell, in list order, on each pass;
cells stop receiving words at their capacities. The r-th word of cell i appears
at total allocation position

\[
T_i(r)=\sum_j\min(c_j,r-1)+\sum_{j\leq i}\mathbf{1}[c_j\geq r].
\]

Before pass r, all cells have received min(c_j,r−1) words. Within pass r, exactly
the cells at or before i with capacity at least r receive their next word before
or at cell i. Therefore the displayed position is exact. Widths are nondecreasing
with budget, hence the first budget meeting every requirement is

\[
B_{\min}=\max_i T_i(r_i).
\]

When an annotated session is missing, B_min is undefined (stored as JSON null),
not a finite number estimated by extrapolation. When finite, it is at most the
total cell capacity. At B_min a witness succeeds; at B_min−1 at least one required
allocation event has not occurred, so complete coverage is impossible.

The expression is computed in O(k²) time and O(k) space for k cells after the
required intervals are constructed; k=8 here. It is the minimum budget for this
specific allocation rule and these anchors. It is not the shortest semantic
answer evidence, the optimum under arbitrary budget allocation, or a claim about
a different retrieval architecture.

## Measurement and inference

The primary estimate is the equal-conversation mean of F_q−Y_q for LoCoMo at
1,024 words, where F is the exact feasibility indicator and Y is the frozen
writer's recorded complete-evidence indicator. The finite-data bound is exact
inside the defined space; the bootstrap interval describes sensitivity to the
seven conversation clusters and is not a confirmatory significance claim.

At each method and budget, failures are assigned exclusively to missing session,
infeasible window geometry or a feasible selection miss. These names identify
constraints in the audited pipeline. They do not establish a causal cognitive
mechanism, distinguish all possible engineering remedies, or imply that source
annotations are exhaustive or minimal. The weak touch criterion requires at
least one covered word in every annotated turn and is not semantic evidence.

The QMSum complete-span audit is secondary; its original Phase 17 primary metric
was mean complete-turn recall, which is a different outcome. Historical random
partition degeneracies do not change the common legal window space or this
method-independent feasibility theorem.
