# Phase 17: isolate boundary-guided evidence selection under exactly matched opportunities

## Why

Phase 16 retrieved active-evidence sessions, but selected-document counts and internal evidence location were not controlled. A matched word cap alone does not isolate the contribution of boundary placement. Frontier methods already cover event memory, hierarchical retrieval and context expansion, so this change focuses on a defensible evaluation contract.

## What changes

- Adds a locally registered fixed-anchor protocol, shared turn index and candidate windows, equal per-window lengths, and 20 count-matched random boundary controls.
- Runs 599 reused LoCoMo questions and 244 reused QMSum queries at three budgets, with complete-word evidence scoring and cluster-aware descriptive intervals.
- Adds 9 correctness tests, paired opportunity validation, deterministic numeric rerun, explicit correction audit and historical persona-level sensitivity.
- Includes a Phase 1–16 research ledger, 37-source verified literature atlas, 10 candidate directions, critical shortlist, figures and Persian RTL report.

## Findings

At 1,024 words, LoCoMo writer 443/599 versus centered 442/599. Writer-minus-random conversation-macro difference is +0.84 percentage points (descriptive 95% interval +0.07 to +1.52), below the registered 2-point practical threshold. QMSum writer-minus-random difference is −0.09 points. No claim of stable improvement, QA accuracy or semantic understanding is made.

## Validation and limits

51 tests passed; one historical Phase 14 test skipped because its pinned upstream Memora copy was absent. All 9 Phase 17 tests ran. 55,638 rows across 2,529 paired groups passed invariant checks; compressed numeric output reproduced byte-for-byte. A secondary session diagnostic was corrected after the first run; all primary metrics, windows and costs remained identical. Both datasets were previously inspected. Protocol registration was local, not an independent public timestamp. Internal episode lengths remain unmatched even though output widths are exact. A separate audit records eight LoCoMo and three QMSum history-seed pairs with a zero-word partition: turn-partition counts match, but effective nonempty interval counts are one lower.

## Publication status

Prepared locally for review. No public branch, PR, merge or release has been created for this cycle. Publication awaits the researcher's approval under the Phase 17 directive.
