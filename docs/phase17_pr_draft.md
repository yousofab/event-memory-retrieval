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

The researcher approved publication and GitHub closeout on 21 October 2026. The reviewed scientific package is commit `0e2483a972e05fcbf02430037e69e87226ef37cb`; subsequent closeout changes add publication documentation, a Phase 18 planning handoff, and CI without changing the protocol, experiment, results, figures, or approved PDF/DOCX. The report remains the pre-publication review snapshot; the publication record supersedes its historical hold wording.

GitHub Actions runs the full existing test suite and the committed-result validator with read-only repository permissions. It does not download source conversations or run a new experiment. Merge with a merge commit to preserve the local protocol/implementation/correction chronology. Tag the merged checkpoint `phase17-fixed-anchor-evidence`; Phase 18 has not started and requires a separate protocol before scoring.

The terminal lacked a GitHub push credential, so the authenticated connector published the five local trees in their original order with new commit metadata. Every tree SHA matches exactly. `docs/phase17_local_git_history.json` maps the local and public SHAs and stores the original commit objects for exact reconstruction. The public equivalent of reviewed local commit `0e2483a` is `a36ba4cfc80e26d5d0c1652e35b1925d04cec1be`. These public timestamps represent publication, not independent preregistration.

The merge commit's explicit `[publish-phase17]` marker enables a separate release job only on a push to `main`, after validation succeeds. That job checks approved SHA-256 values, creates the checkpoint tag/release and uploads PDF, DOCX, numeric rows and checksums. Write permission is limited to this publication job; pull-request validation remains read-only. An existing release targeting a different commit is never overwritten.
