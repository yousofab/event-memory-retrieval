# Event Memory Retrieval — BSc software project

## Phase 18 local review package

**Phase 18 is implemented and evaluated locally; this cycle awaits final publication approval.** The new annotation-assisted auditor proves exact complete-evidence feasibility inside the frozen Phase 17 window space and computes the minimum total budget under its original round-robin allocation. It is an offline diagnostic with access to reference labels, not a new deployable retriever.

At 1,024 words, the writer's 156 LoCoMo failures decompose into **106 missing-session cases, 25 geometry-infeasible cases and 25 feasible selection misses**. Exact feasible coverage is **468/599**, versus recorded writer coverage of 443/599. The equal-conversation headroom is **4.19 percentage points** (descriptive cluster interval 2.96–5.13). For QMSum, complete coverage of all annotated relevant spans is possible for 29/244 queries; this is a secondary outcome distinct from the Phase 17 primary partial-turn-recall metric.

- [Persian research report](docs/phase18.md), [locally registered plan](docs/phase18_plan.md), [formal definitions and proofs](docs/phase18_formal_contract.md), [17-source literature atlas](docs/phase18_literature_atlas.md), [novelty critique](docs/phase18_novelty_audit.md), [reproduction guide](docs/phase18_reproduce.md).
- [PDF](deliverables/phase18_research_report_fa.pdf) and [Word](deliverables/phase18_research_report_fa.docx): Persian RTL B Nazanin report with figures, numeric examples, references and advisor/FARDIAT acknowledgements.
- `scripts/run_phase18_feasibility.py`, `scripts/validate_phase18.py`, `scripts/analyze_phase18.py`; seven new correctness tests including independent enumeration of every candidate-window combination on 240 seeded toy geometries across their budgets.
- 843 reused questions, 2,529 query–budget groups and 55,638 historical conditions checked; two numeric files reproduced byte-for-byte. The full suite ran 59 tests: 58 passed and one historical Phase 14 test skipped for absent local upstream data. The toy examples are correctness tests, not a new conversation benchmark.

```bash
python scripts/fetch_data.py
python scripts/fetch_phase10_data.py --download
python -m unittest discover -s tests -p 'test_phase18*' -v
python scripts/run_phase18_feasibility.py --output-dir /tmp/phase18-reproduction
python scripts/validate_phase18.py --directory /tmp/phase18-reproduction
```

The bound is exact only for the fixed legal windows and supplied annotations. It does not bound answer accuracy, semantic sufficiency or a different retrieval architecture. A 17-source focused review includes the 22 October 2026 Raw-RAG preprint and distinguishes two different MemTrace papers; no claim of worldwide priority is made. Historical results and the Phase 17 release remain unchanged.

**Status: Phase 17 fixed-anchor, exactly matched-opportunity evidence study completed and approved for publication. At 1,024 words, LoCoMo full-evidence coverage was 443/599 for the frozen writer versus 442/599 for centered context; the conversation-macro difference versus 20 random controls was +0.84 percentage points, below the predeclared 2-point practical threshold. QMSum did not show a stable transfer benefit. This is a controlled exploratory retrieval study on reused data, not answer accuracy or a claim of human-like understanding.**

[Phase 17 publication record](docs/phase17_publication.md) · [Phase 18 handoff — planning only](docs/phase18_handoff.md) · [PDF report](deliverables/phase17_research_report_fa.pdf) · [Word report](deliverables/phase17_research_report_fa.docx)

## Phase 17: boundary guidance with fixed evidence opportunities

The turn BM25 index, eight anchors, all feasible context windows, per-window widths, selected window count, accessible sessions and **actual unique-word cost** are identical across centered, frozen-writer and 20 count-matched random conditions. Only boundary-guided window selection changes. Underlying episode lengths are not matched. Turn-partition counts are matched; a post-result audit found eight LoCoMo and three QMSum history-seed pairs with a zero-word part, leaving one fewer effective nonempty interval. Output opportunities remain exact. The local protocol commit `2932298` predates scoring; it is not externally timestamped public preregistration.

- [Persian research report](docs/phase17.md), [Phase 1–16 state ledger](docs/phase17_state_ledger.md), [37-source literature atlas](docs/phase17_literature_atlas.md), [frontier and novelty audit](docs/phase17_frontier_synthesis.md), [10 candidates and critical shortlist](docs/phase17_candidates.md).
- [Protocol](docs/phase17_plan.md), [machine-readable plan](configs/phase17_plan.json), [reproduction guide](docs/phase17_reproduce.md), [implementation corrections](docs/phase17_implementation_corrections.md), [PR draft](docs/phase17_pr_draft.md).
- `scripts/run_phase17_fixed_anchors.py`, `scripts/validate_phase17.py`, `scripts/analyze_phase17.py`, `tests/test_phase17_fixed_anchors.py`.
- `results/phase17_rows.json.gz`: 55,638 numeric rows, 843 questions, 3 budgets, 22 conditions; these are repeated conditions, not 55,638 independent samples. Corrected numerical output was reproduced byte-for-byte. `phase17_summary.json`, `phase17_diagnostics.json`, `phase17_validation.json` and `phase17_historical_persona_audit.json` contain aggregates and audit evidence.
- `deliverables/phase17_research_report_fa.docx` and `.pdf`: A4 Persian RTL B Nazanin report with verified references, figures and advisor/FARDIAT acknowledgements. Fonts and upstream transcripts are excluded.
- GitHub Actions runs the existing test suite and validates the committed numeric results on pull requests and pushes to `main`. This check uses no raw datasets or paid API; it is not a fresh end-to-end experiment. The approved report files remain the original review snapshot; their historical publication-hold wording is superseded by the publication record above.

At 512 words, the writer trails centered windows by 14 LoCoMo complete-evidence cases; at 2,048 all methods reach 472/599. QMSum uses broad relevant-turn spans, not minimal answer evidence. Confidence intervals are descriptive cluster bootstraps over 7 LoCoMo conversations or 10 QMSum source families. A post-hoc historical Phase 16 reanalysis clusters by 10 personas; its equal-selected sensitivity interval includes zero. Historical results remain unchanged.

```bash
python scripts/fetch_data.py
python scripts/fetch_phase10_data.py --download
python -m unittest discover -s tests -v
python scripts/run_phase17_fixed_anchors.py --output-dir /tmp/phase17-review-run
python scripts/validate_phase17.py --directory /tmp/phase17-review-run
```


## Phase 16: paired online boundaries and count-matched random partitions

The [primary plan](docs/phase16_plan.md) was registered [before Phase 16 scoring](https://github.com/yousofab/event-memory-retrieval/commit/d609e32fc4d90743eceac9a777d7f9ebe4eb1b85). The [equal-selected-document sensitivity](docs/phase16_post_result_amendment.md) was separately registered [after inspecting the primary result, before its own computation](https://github.com/yousofab/event-memory-retrieval/commit/75e65685cc5ca92bb7c919de2c237f3226edf60e). Both use pinned Memora revision `a6493188efc836d6511ed5e4163fe3ba87da30ff`. All 30 groups and 600 questions are ranked; the primary metric includes the 398 with direct active-evidence session IDs. Source roles, original tokens and total retrieved word cap are common to all methods. Random controls are matched by **built segments per session**, but selected segment count and lengths can still differ.

- [Persian Phase 16 report](docs/phase16.md), [machine-readable plan](configs/phase16_boundary_plan.json), `scripts/run_phase16_boundaries.py`, `scripts/run_phase16_equal_selected.py`, `scripts/validate_phase16.py` and `tests/test_phase16_boundaries.py`.
- `results/phase16_summary.json`, `results/phase16_rows.json.gz`, `results/phase16_equal_selected.json.gz`: aggregates and numeric question-keyed rows, no raw conversation, question or answer text.
- `deliverables/گزارش-پژوهشی-مرحله-۱۶-مرزهای-همتعداد.docx` and `.pdf`: Persian RTL B Nazanin progress report with FARDIAT and advisor acknowledgements.

```bash
git clone https://github.com/geniesinc/Memora.git ../memora-upstream
git -C ../memora-upstream checkout a6493188efc836d6511ed5e4163fe3ba87da30ff
python scripts/run_phase16_boundaries.py --upstream ../memora-upstream --summary /tmp/phase16_summary.json --rows /tmp/phase16_rows.json.gz
python scripts/run_phase16_equal_selected.py --upstream ../memora-upstream --output /tmp/phase16_equal_selected.json.gz
python scripts/validate_phase16.py
python -m unittest tests/test_phase16_boundaries.py -v
```

## Phase 15: role fidelity, horizon, evidence state and word cost

The [primary protocol](docs/phase15_plan.md) was registered in [commit f13a583](https://github.com/yousofab/event-memory-retrieval/commit/f13a58370024bde842e3211e652d92b8c1787a33) before ranking. The [word-budget sensitivity](docs/phase15_post_result_amendment.md) and [separate content-history sensitivity](docs/phase15_history_sensitivity.md) were each registered **after** their motivating observations and **before** their own calculations. The study uses all 30 persona-period histories and all 600 question strings from pinned official Memora. Explicit `session_id` active evidence exists for 398 questions; 156 content-history questions with a different label schema are reported separately. No API or answer model was run.

- [Persian Phase 15 report](docs/phase15.md), `configs/phase15_plan.json`, `scripts/run_phase15_role_retrieval.py`, `scripts/run_phase15_budget.py`, `scripts/run_phase15_history.py`, `scripts/validate_phase15.py` and `tests/test_phase15_role_retrieval.py`.
- `results/phase15_summary.json`, `results/phase15_rows.json.gz`, `results/phase15_budget.json.gz`, `results/phase15_history.json.gz`: numeric aggregates and question-keyed rows, no raw dialogue or answer text.
- `deliverables/گزارش-پژوهشی-مرحله-۱۵-نقش-و-هزینه-Memora.docx` and `.pdf`: Persian RTL B Nazanin progress report, FARDIAT logo and acknowledgements. Supplied font and source textbooks are not redistributed.

```bash
git clone https://github.com/geniesinc/Memora.git ../memora-upstream
git -C ../memora-upstream checkout a6493188efc836d6511ed5e4163fe3ba87da30ff
python scripts/run_phase15_role_retrieval.py --upstream ../memora-upstream
python scripts/run_phase15_budget.py --upstream ../memora-upstream
python scripts/run_phase15_history.py --upstream ../memora-upstream
python scripts/validate_phase15.py
python -m unittest tests/test_phase15_role_retrieval.py -v
```

## Phase 14: Memora direct-model prompt-fidelity audit

The [Phase 14 plan](docs/phase14_plan.md) was [registered after discovery but before the supplementary measurements](https://github.com/yousofab/event-memory-retrieval/commit/119f46a9fb47fed486873c019fb484e8d7545f06). This is a reproducibility audit, not a blind or independent model evaluation. The official Memora source is pinned to `a6493188efc836d6511ed5e4163fe3ba87da30ff` with a SHA-256 check on the evaluator; source data are not committed here.

- [Persian Phase 14 report](docs/phase14.md), [registered plan](configs/phase14_plan.json), and [aggregate results](results/phase14_summary.json).
- `scripts/audit_phase14_memora.py` AST-extracts the official formatter for isolated no-API execution, checks synthetic and real samples, and counts all 30 persona-period histories. `scripts/validate_phase14.py` and `tests/test_phase14_memora.py` check invariants.
- `deliverables/گزارش-پژوهشی-مرحله-۱۴-ممیزی-ورودی-Memora.docx` and `.pdf`: Persian RTL B Nazanin progress report with mentor acknowledgements and the supplied FARDIAT logo; the font and raw conversations are not redistributed.

```bash
git clone https://github.com/geniesinc/Memora.git ../memora-upstream
git -C ../memora-upstream checkout a6493188efc836d6511ed5e4163fe3ba87da30ff
python scripts/audit_phase14_memora.py --upstream ../memora-upstream
python scripts/validate_phase14.py
python -m unittest tests/test_phase14_memora.py -v
```

## Phase 13: two-session provenance audit

The [Phase 13 protocol](docs/phase13_plan.md) was [committed before scoring](https://github.com/yousofab/event-memory-retrieval/commit/a9796fd4781128c820531243e5b8c32cbbb1acd2). Phases 7 and 12 had already inspected this source; Phase 13 is an exploratory, not independent confirmatory, experiment. A single top-20 BM25 candidate from a different session is promoted to second place; the newest other-session candidate and 20 randomized other-session choices provide controls under the same whole-turn word budget. Answer text and evidence labels do not enter ranking.

- [Persian Phase 13 report](docs/phase13.md) and [machine-readable plan](configs/phase13_plan.json): question, literature, effect size, guardrail and limitations.
- `scripts/run_phase13_provenance.py`, `scripts/package_phase13.py`, `scripts/validate_phase13.py`, `tests/test_phase13_provenance.py`: CPU-only reproducible experiment and controls.
- `results/phase13_summary.json`, `results/phase13_provenance.json.gz`: 4,968 numeric rows, exact parity with 144 Phase 12 BM25 question-budget rows, no source transcript.
- `deliverables/گزارش-پژوهشی-مرحله-۱۳-بازیابی-شاهد-از-دو-جلسه.docx` and `.pdf`: RTL B Nazanin progress report, FARDIAT logo and mentor acknowledgements. Supplied textbooks and the licensed font are not redistributed.

Reproduce after fetching the pinned LongMemEval-S source:

```bash
python -m unittest discover -s tests -v
python scripts/run_phase13_provenance.py --source data/raw/longmemeval_s_cleaned.json
python scripts/package_phase13.py
python scripts/validate_phase13.py
```

## Phase 12: evidence after a knowledge update

The [Phase 12 protocol](docs/phase12_plan.md) was [committed before scoring](https://github.com/yousofab/event-memory-retrieval/commit/fe74edcf9beef264bbf5f0186f6290b751e81a58). The source dataset schema and earlier Phase 7 results were already known, so this is an exploratory registered analysis rather than an independent confirmatory test. It compares a shared BM25 turn index with a chronological reorder of its top 20 candidates and 20 randomized reorders under identical word budgets. Gold answers and evidence IDs are excluded from the ranking functions.

- [Persian report](docs/phase12.md) and [frozen protocol](configs/phase12_plan.json); journal literature, current LongMemEval-V2 context, limitations, and acknowledgements.
- `scripts/run_phase12_temporal.py`, `scripts/package_phase12.py`, `scripts/validate_phase12.py`, `tests/test_phase12_temporal.py`: CPU-only reproducible scoring and validation.
- `results/phase12_summary.json` and `results/phase12_temporal.json.gz`: summary and 4,752 numeric per-query rows without conversation or answer text.
- `scripts/phase12_posthoc.py` and `results/phase12_posthoc.json`: explicitly post-result explanatory diagnostics.
- `deliverables/گزارش-پژوهشی-مرحله-۱۲-حافظه-و-اصلاح-اطلاعات.docx` and `.pdf`: RTL B Nazanin report with FARDIAT acknowledgement and supplied logo; font and upstream corpus are not redistributed.

Reproduce after the pinned Phase 7 dataset is downloaded:

```bash
python -m unittest discover -s tests -v
python scripts/run_phase12_temporal.py --source data/raw/longmemeval_s_cleaned.json
python scripts/package_phase12.py
python scripts/validate_phase12.py
python scripts/phase12_posthoc.py --source data/raw/longmemeval_s_cleaned.json
```

Research question: Under the same retrieval ranker and retrieved-text budget, does lightweight event-oriented segmentation improve retrieval of annotated evidence turns from long conversations over fixed-size chunks and session chunks? The project evaluates retrieval only. It does not claim to build or evaluate a complete dialogue agent, answer generator, or neural memory mechanism.

## Data provenance

Source: [LoCoMo](https://github.com/snap-research/locomo), Maharana et al., ACL 2024. The dataset is distributed under [CC BY-NC 4.0](https://github.com/snap-research/locomo/blob/main/LICENSE.txt). `data/raw/locomo10.json` is intentionally excluded from git. The code and documentation here are original project work; cite the upstream authors when using the data.

Pinned upstream blob SHA-1: `d95b872480b413d935821fdc3c84f8a8f5f29e73`  
Dataset SHA-256: `79fa87e90f04081343b8c8debecb80a9a6842b76a7aa537dc9fdf651ea698ff4`

The original file can be downloaded and verified with `python scripts/fetch_data.py` on a machine with Internet access. If upstream changes, the script fails instead of silently substituting a new dataset. Then run `python scripts/audit_data.py`. Python 3.9+ standard library suffices for Phase 1.

## Phase 1 result

The verified source has 10 conversations, 272 sessions, 5,882 turns and 1,986 questions. The frozen text-only evaluation subset contains 873 questions: 274 from three development conversations and 599 from seven held-out conversations. The complete eligibility manifest and counts are in `results/phase1_audit.json`; exact rules are in `configs/protocol.json` and explained in [`docs/phase1.md`](docs/phase1.md).

The small 12-question locally authored T4 demonstration is **not** a result for this dataset and will not be reported as an empirical finding in the thesis.

## Research phases

1. Data audit and precommitted eligibility (this commit).
2. Fixed and session baselines with a shared lexical ranker (development run complete).
3. Lightweight event segmentation; development-only tuning (complete; selected settings frozen).
4. Held-out comparison at equal retrieved-text budgets and descriptive error/cost analysis (complete).
5. Post hoc diagnostic audit of structural feasibility, discordant pairs, and leave-one-conversation-out sensitivity (complete; descriptive only).
6. Post-Phase-4 exploratory extension: local LSA boundary representation compared with the frozen lexical method (complete; exploratory).
7. External transfer to LongMemEval-S with frozen methods, evidence-label audit and paired retrieval comparison (complete; exploratory).
8. Causal turn-arrival memory writer with immutable segments and exploratory transfer (complete).
9. Random valid boundaries with exactly matched per-session segment counts, 20 seeds and fixed retrieval budgets (complete; exploratory).
10. Frozen causal writer transferred to human-labeled QMSum meeting topic spans, with 20 matched-count controls and specific-query evidence retrieval (complete; independent topic labels, not perceptual event boundaries).
11. Controlled segment-to-turn routing and evaluation-granularity audit on the previously inspected QMSum meetings (complete; exploratory reuse of data).

## Repository map

- `configs/protocol.json`: pinned source, split, eligibility, metric definition.
- `scripts/fetch_data.py`: upstream retrieval and checksum validation.
- `scripts/audit_data.py`: audit and deterministic eligibility manifest.
- `results/phase1_audit.json`: observed counts and selected evidence IDs, no conversational text.
- `docs/phase1.md`: methodological decisions, risks, and next checkpoint.
- `scripts/run_baselines.py`: shared BM25 ranker and fixed/session development baselines.
- `tests/test_baselines.py`: partition, budget and leakage invariants.
- `results/phase2_development_baselines.json`: development-only question and conversation results.
- `docs/phase2.md`: precise cost, selection, and scoring contracts and provisional observations.
- `configs/phase3_search.json`: small development search and selection rule.
- `configs/phase3_frozen.json`: selected method and budgets for the held-out run.
- `scripts/run_event_development.py`: lexical change-point segmentation and development selection.
- `results/phase3_development_event.json`: development results for all four settings.
- `docs/phase3.md`: method, provisional comparison, and limitations.
- `docs/phase4_plan.md`: analysis contract committed before the held-out run.
- `scripts/run_held_out.py`: one-time frozen evaluation, with checksum and overwrite guards.
- `scripts/validate_held_out.py`: consistency checks on the recorded results, without re-running retrieval.
- `results/phase4_held_out.json`: 599 held-out questions, three methods, three budgets, no source text.
- `docs/phase4.md`: Persian results, paired conversation comparison, error and cost analysis.
- `configs/phase5_audit_plan.json` and `docs/phase5_audit_plan.md`: post hoc audit definitions and recorded scope.
- `scripts/run_phase5_audit.py`: recompute the primary-budget rows and classify structural feasibility.
- `scripts/validate_phase5_audit.py`: check saved diagnostic output against Phase 4 without raw data.
- `results/phase5_diagnostics.json`: diagnostic counts and discordant case identifiers, no source text.
- `docs/phase5.md`: Persian Phase 5 research progress report.
- `deliverables/گزارش-پژوهشی-مرحله-۵-ممیزی.docx` and `.pdf`: editable and fixed-layout versions of that progress report.
- `configs/phase6_semantic_plan.json` and `docs/phase6_plan.md`: exploratory protocol registered on GitHub before Phase 6 computation; the seven evaluation conversations were already examined in Phases 4 and 5.
- `requirements-phase6.txt`: exact observed CPU environment for the optional LSA experiment.
- `scripts/run_phase6_semantic.py`, `scripts/validate_phase6.py`, `scripts/run_phase6_analysis.py`: label-free text fitting and segmentation, integrity validation, descriptive analysis.
- `results/phase6_development_lsa.json`, `results/phase6_held_out_lsa.json`, `results/phase6_diagnostics.json`: question-level numeric results and diagnostics without conversation or question text.
- `docs/phase6.md`: full Persian interpretation of the exploratory result and its limits.
- `deliverables/گزارش-پژوهشی-مرحله-۶-مرزبندی-معنایی.docx` and `.pdf`: editable and fixed-layout Persian progress report.
- `configs/phase7_external_plan.json`, `docs/phase7_plan.md`, `docs/phase7_label_amendment.md`, `docs/phase7_source_audit_amendment.md`: protocol and pre-score source-data amendments, all preserved in Git history.
- `scripts/fetch_phase7_data.py`, `scripts/run_phase7_external.py`, `scripts/validate_phase7.py`: pinned LongMemEval-S download, frozen transfer and integrity checks.
- `scripts/run_phase7_boundary_audit.py`: post hoc label-free boundary diagnostics.
- `results/phase7_summary.json`, `results/phase7_external.json.gz`, `results/phase7_boundary_audit.json`: browsable summary, compressed full per-question record and structural diagnostics; no source text.
- [`docs/phase7.md`](docs/phase7.md): full Persian external-transfer report and limitations.
- `deliverables/گزارش-پژوهشی-مرحله-۷-آزمون-بیرونی.docx` and `.pdf`: editable RTL and fixed-layout Persian progress report.

The optional Word builders are `scripts/build_phase5_report.py`, `scripts/build_phase6_report.py` and `scripts/build_phase7_report.py`. They need `python-docx` and a locally installed B Nazanin font to reproduce the intended layout; the font is not redistributed. Phases 1-5 retain their standard-library-only runtime. Phases 6-7 additionally require `numpy`, `scipy`, and `scikit-learn` on CPU. They do not download pretrained model weights or call an API.

Phase 6 reproduction, after fetching the pinned data and installing `requirements-phase6.txt`:

```bash
python -m unittest discover -s tests -v
python scripts/validate_held_out.py
python scripts/validate_phase5_audit.py
python scripts/validate_phase6.py --split development
python scripts/validate_phase6.py --split held_out
# Fresh paths only: the recorded outputs are never overwritten by the runner.
python scripts/run_phase6_semantic.py --split development --output /tmp/phase6-dev-recheck.json
python scripts/run_phase6_semantic.py --split held_out --output /tmp/phase6-eval-recheck.json
python scripts/run_phase6_analysis.py --output /tmp/phase6-analysis-recheck.json
```

**The Phase 4 held-out result is recorded. The Phase 6 exploratory comparison (468 versus 467 of 599 at 1,024 words) does not establish a reliable LSA advantage. Neither phase measures answer generation or philosophical understanding.**

Phase 7 reproduction, after installing `requirements-phase6.txt` and fetching the pinned LoCoMo data:

```bash
python scripts/fetch_phase7_data.py
python -m unittest discover -s tests -v
python scripts/validate_phase7.py
python scripts/run_phase7_external.py --output /tmp/phase7-recheck.json
python scripts/run_phase7_boundary_audit.py --output /tmp/phase7-boundary-recheck.json
```

The official LongMemEval-S source is downloaded to ignored `data/raw/`; its SHA-256 and dataset revision are fixed in `configs/phase7_external_plan.json`. The recorded question-level result is compressed in `results/phase7_external.json.gz`; `scripts/validate_phase7.py` reads it directly and checks its digest against the browsable summary. The post hoc diagnostic output is a separate file. The 30 abstention questions are excluded from evidence retrieval, and the discovered label/session-ID irregularities are disclosed in the two pre-score amendments. Under the 1,024-word budget, LSA and lexical boundaries both recover all marked evidence on 320/470 answerable questions; the difference was one case each in opposite directions.


## Phase 8 causal writer

`configs/phase8_causal_plan.json` and `docs/phase8_plan.md` were committed on the Phase 8 branch before scoring. Earlier LoCoMo and LongMemEval outcomes had already been inspected, so this is exploratory even with a timestamped plan. `scripts/run_phase8_causal.py` builds immutable segments using only the current and three previous turns, then queries the final index using the same BM25 ranker and word budgets. Tests exercise prefix stability, immutable closure, session reset and label isolation. `scripts/validate_phase8.py` compares the frozen methods exactly to the Phase 4 and Phase 7 records.

- `docs/phase8.md`: Persian full report with the research gap, method, results, limitations and next study.
- `results/phase8_summary.json`, `results/phase8_causal.json.gz`: numeric summaries and full question-level result with provenance, without raw conversation text.
- `deliverables/گزارش-پژوهشی-مرحله-۸-نویسنده-علّی-حافظه.docx` and `.pdf`: editable RTL B Nazanin and fixed-layout reports.

Reproduce on CPU after fetching both pinned datasets and installing `requirements-phase6.txt`:

```bash
python -m unittest discover -s tests -v
python scripts/validate_phase8.py
python scripts/run_phase8_causal.py --output /tmp/phase8-recheck.json
```

The official cleaned LongMemEval-S file must match the SHA-256 in `configs/phase7_external_plan.json`; the runner refuses a truncated or modified copy. At 1,024 words, the online writer covered 463/599 LoCoMo held-out questions versus 467/599 for the retrospective boundary and 460/599 for fixed chunks. External coverage was 320/470 for both online and retrospective methods. These are evidence retrieval results, not generated-answer accuracy or human event-boundary judgments.

## Phase 9 matched-count boundary control

The plan in `configs/phase9_boundary_plan.json` and [`docs/phase9_plan.md`](docs/phase9_plan.md) was committed on the research branch before Phase 9 scoring. Earlier LoCoMo results had already been seen. `scripts/run_phase9_controls.py` uniformly samples valid contiguous partitions with the online writer's **exact segment count in every session**, preserving full turns and the 160-word cap except a single overlong turn. The 20 deterministic seeds (0–19) use turn lengths and the online segment count, without question or evidence labels for boundary placement. The control sees each session's final count, so it is retrospective, not a deployable streaming writer.

- [`docs/phase9.md`](docs/phase9.md): Persian report with the research gap, exact method, sensitivity and limits.
- `results/phase9_summary.json`, `results/phase9_controls.json.gz`: numeric summary and full question-level record with checksums, without source text.
- `scripts/validate_phase9.py` and `tests/test_phase9_controls.py`: integrity and sampler tests.
- `deliverables/گزارش-پژوهشی-مرحله-۹-کنترل-مرزها.docx` and `.pdf`: Persian RTL B Nazanin editable and fixed-layout reports.

Reproduce on CPU after fetching pinned LoCoMo data and installing `requirements-phase6.txt`:

```bash
python -m unittest discover -s tests -v
python scripts/validate_phase9.py
python scripts/run_phase9_controls.py --output /tmp/phase9-recheck.json
```

The primary observed outcome was 463/599 for the online writer versus a random-control median of 453.5/599, range 444–471. Four of 20 sampled controls tied or exceeded the writer. The count is descriptive, not a p-value. Segment length distributions and BM25 ties can differ, and the benchmark does not label human event boundaries or measure philosophical understanding.

## Phase 10 independent topic-onset transfer

The Phase 10 plan, metric definitions, exact QMSum source manifest and all 35 upstream Git blob hashes were committed on the research branch **before Phase 10 scoring**. The official [QMSum](https://github.com/Yale-LILY/QMSum) test split has 35 meetings, 20,718 turns, 161 unique nonzero human topic-span starts and 244 specific queries. The pre-existing online writer was transferred without retuning. Each of 20 deterministic random partitions has exactly the writer's segment count in each meeting and respects complete turns and the same size cap. The random control knows the writer's final segment count and is therefore retrospective.

- [`docs/phase10_plan.md`](docs/phase10_plan.md), `configs/phase10_plan.json` and `configs/phase10_source_manifest.json`: committed study contract and pinned source.
- [`docs/phase10.md`](docs/phase10.md): Persian RTL research report with primary and secondary results, limits, references and acknowledgements.
- `scripts/fetch_phase10_data.py`, `scripts/run_phase10_topic_transfer.py`, `scripts/package_phase10.py` and `scripts/validate_phase10.py`: source verification, analysis, compact output and integrity validation.
- `results/phase10_summary.json`, `results/phase10_transfer.json.gz`: numerical summaries and 16,104 query-method-budget rows, without raw meeting transcripts.
- `deliverables/گزارش-پژوهشی-مرحله-۱۰-مرزهای-موضوعی.docx` and `.pdf`: Persian RTL B Nazanin editable and fixed-layout reports; the supplied FARDIAT mark appears with the acknowledgements.

Reproduce with Python after fetching the pinned source:

```bash
python scripts/fetch_phase10_data.py --download
python -m unittest discover -s tests -v
python scripts/validate_phase10.py
python scripts/run_phase10_topic_transfer.py --output /tmp/phase10-recheck.json
```

At a two-turn tolerance, the writer covers 84.37% of topic starts versus the 65.91% random median, and zero of 20 controls match or exceed the writer. Exact-start coverage and relevant-turn retrieval give different results (see above); these must not be merged into an overall claim of semantic or cognitive superiority. The committee subset is saturated at 100% for both methods. These labels describe meeting topics, not human perceptual event boundaries; the result is descriptive and the 20 seeds do not supply an inferential p-value.

## Phase 11 controlled retrieval routing

The Phase 11 contract was [committed before Phase 11 scoring](docs/phase11_plan.md), but Phase 10 results on the same QMSum test meetings had already been inspected. This is an exploratory, not independent confirmatory, audit. The frozen online writer, 20 exact-count random controls and fixed chunks feed the same BM25 and budgets. The new two-stage path ranks segments, collects complete candidate segments under a 4× processing-scope cap, then ranks full turns inside those candidates under the original 512/1024/2048-word **output** cap. Direct ranking of all turns is a diagnostic with a larger search scope.

- [`docs/phase11.md`](docs/phase11.md): full Persian RTL report, frontier literature map, preregistered outcomes, post-result diagnostic, limitations and mentor acknowledgement.
- [`docs/phase11_plan.md`](docs/phase11_plan.md), `configs/phase11_plan.json`: the registered contract; its Git history predates scoring.
- `scripts/run_phase11_hierarchical.py`, `scripts/package_phase11.py`, `scripts/validate_phase11.py`, `tests/test_phase11_hierarchical.py`: reproducible CPU implementation, packaging, exact Phase 10 baseline parity and controls.
- `scripts/phase11_diagnostics.py`, `results/phase11_posthoc_diagnostics.json`: explicitly **post-result** any-evidence and annotated-density diagnostics.
- `results/phase11_summary.json`, `results/phase11_retrieval.json.gz`: 16,836 numeric rows without transcript or answer text.
- `deliverables/گزارش-پژوهشی-مرحله-۱۱-مسیر-حافظه-تا-شاهد.docx` and `.pdf`: Persian RTL reports, with user-provided B Nazanin embedded in the PDF and the supplied FARDIAT mark. The font binaries are not redistributed.

Reproduce after fetching the pinned QMSum test data:

```bash
python scripts/fetch_phase10_data.py --download
python -m unittest discover -s tests -v
python scripts/run_phase11_hierarchical.py --output results/phase11_retrieval.json
python scripts/package_phase11.py
python scripts/validate_phase11.py
python scripts/phase11_diagnostics.py
```

At 1,024 words, mean relevant-turn coverage across meetings was 16.78% for the online two-stage path, 16.91% for the random median, 17.06% for fixed chunks with the same path, and 16.96% for global-turn BM25. The candidate stage exposed 68.94% of relevant turns for the online writer before the final output cap. The registered primary result is negative. The later any-evidence diagnostic increases under two-stage routing, but it does not replace the primary metric. All 16,104 original flat rows were matched exactly to Phase 10.

## Educational acknowledgement

The researcher thanks **FARDIAT**, a specialized brain and cognition institute, and **Dr Arash Fekri**, its founder and their teacher, for the Cognitive Neuroscience education that inspired the event-segmentation question. Dr Fekri reviewed and approved the project's proposal. The researcher also thanks **Professor Noori Volandeh**, their university instructor for this project, for supporting new ideas and the research process. The supplied FARDIAT mark appears in the printable Phase 9, 10 and 11 reports. Each future phase report includes this acknowledgement.
