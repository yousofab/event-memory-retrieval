# Phase 19 formal contract

## Practical retrieval

Let P be the first M=64 nonempty turns in the unchanged BM25 ranking, k=8,
and g(t) the native session of turn t. For R_r, traverse P and reserve the first
representative of each distinct g until r representatives or exhaustion. Fill
the remaining positions from P in its original ranking, without duplicates.
Finally sort the selected indices by their original BM25 ranks. R_4 is the
primary treatment, R_8 a secondary dose comparison, and R_0 the original top8.

The sham R_4 preserves the complete label-frequency histogram in P but assigns
labels to different turns via a seeded permutation. It selects using those labels
and builds windows in actual native sessions. Its seed depends only on a frozen
seed, history identifier and question identifier, never references or answers.
This is a structural perturbation control, not a claim of exchangeable true and
shuffled sessions or a randomization test.

## Reservation guarantee

If S distinct groups occur in P, R_r represents at least min(r,S) groups; it
retains the first-ranked turn, returns k distinct turns, and replaces at most
r-1 members of the original top-k. The reserved representatives witness the
first claim; the earliest representative is rank1, and adding remaining ranked
turns cannot reduce group coverage. At most r-1 reserved representatives lie
outside top-k, so filling from top-k causes at most that many replacements.
Here r<=k<=M. Renaming group IDs bijectively leaves selections unchanged.

This guarantee concerns source groups, not gold groups, answer correctness or
semantic diversity. It can discard a necessary turn from a concentrated session.
Increasing r therefore has no monotonic guarantee for evidence coverage.
If the pool has a single session, every registered policy returns the original
top8; this is an executable negative control. R_8 maximizes the number of groups
represented by k anchors in this pool, but not their relevance or their evidence.

## Window opportunities and exact cost

After anchor selection use the original Phase17 midpoint cells, native session
coordinates, round-robin allocation in original BM25 order and legal contiguous
windows containing their anchors. Each of the two selectors has the same cells,
widths and paid words inside one policy. Across policies these objects change;
they are not described as paired opportunities. For each condition actual cost
is min(B,sum of its cell capacities). Unequal costs across policies are counted.
The common budget is a maximum of returned source-text regex words, not a model
token bill, index-storage cap or paid retrieval-computation budget. Rank depth64,
index and number of anchors are shared; retrieval wall time and RSS are reported.

## Recomputed exact feasibility

For each policy and each cell i, let c_i be capacity and r_i the shortest in-cell
interval containing its anchor and every part of a nonempty reference message
intersecting that cell. When a reference session has no anchor, complete coverage
is impossible in this policy. Otherwise complete coverage is possible exactly
when all allocated widths w_i >= r_i. Windows and minimum budget are computed
using the already tested Phase18 theorem, separately for each new anchor set.

The exact round-robin minimum budget is

```text
B_min = max_i [sum_j min(c_j, r_i - 1) + count(j <= i with c_j >= r_i)].
```

The audit stores constructive successful windows and checks threshold B_min and
B_min-1. Necessary evidence may cross a cell boundary; all intersected pieces
must be covered. A source word is never counted twice. Reference labels enter
this offline audit only, after every practical selection is complete.

For each question, policy and budget, executable invariants are

```text
realized_complete <= exact_feasible <= all_gold_sessions_in_windows
                  <= all_gold_sessions_in_top64_pool.
```

These upper bounds apply to complete annotated-message coverage. The all-or-none
ceiling is not an upper bound on mean partial message recall, and broad supplied
references are not necessarily minimal semantic evidence. The bound of468 from
Phase18 is never carried over to changed anchors.

## Estimation and attribution

Use question means inside histories followed by equal-history averaging. The
primary policy contrast is R_4 writer minus top8 writer at1024 words, with source-
specific registered outcomes. Five sham seeds are averaged inside the question.
The secondary two-by-two interaction is

```text
(R4_writer - R4_centered) - (top8_writer - top8_centered).
```

It measures dependence of two algorithmic choices under this protocol, not a
general causal effect of human semantic boundaries. Report paired transitions
for session access, exact complete feasibility and realized complete coverage.
Descriptive history bootstrap intervals and leave-one-history-out ranges expose
instability; neither queries nor sham seeds are treated as independent samples.

## Attribution and scope

Diversification and complementarity are established prior art (MMR, BFR, and
related memory retrieval). The contribution is the particular controlled audit,
source adapter, transfer experiment, falsifiable stopping rule and reusable
certificates. No global novelty of diversification, semantic understanding,
neural mechanism, benchmark leaderboard victory or answer-accuracy gain is claimed.

We thank Amir Noori Volandeh for university supervision and support of new ideas,
and Dr Arash Fekri, founder of FARDIAT, for cognitive neuroscience education and
review and approval of the original proposal.
