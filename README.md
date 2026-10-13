# Event Memory Retrieval — BSc software project

**Status: Phase 7 external transfer complete on LongMemEval-S, with protocol and data-quality amendments recorded before scoring. At 1,024 words, semantic LSA and lexical event boundaries each retrieved all marked evidence for 320/470 answerable questions; fixed chunks retrieved 323/470. This is an evidence-retrieval result, not an official answer-generation score. The final thesis remains a later deliverable.**

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
8. Causal turn-arrival memory writer with immutable segments and exploratory transfer (complete); independently labeled event-boundary study and final thesis remain future work.

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
