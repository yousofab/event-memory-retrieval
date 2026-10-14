# Event Memory Retrieval — BSc software project

**Status: Phase 11 controlled segment-to-turn retrieval audit complete. On the previously inspected 35 QMSum test meetings, two-stage retrieval at 1,024 output words covered 16.78% of annotated relevant turns with frozen online boundaries versus 16.91% for the median of 20 exact-count random partitions. The earlier whole-segment path covered 34.69% for the online writer. A post-result any-evidence diagnostic improved from 87.81% to 92.14% for that writer. These answer different questions, and neither establishes generated-answer quality or human event perception. The final thesis remains a later deliverable.**

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
