# Event Memory Retrieval — BSc software project

**Status: Phase 4 complete: the frozen three-way comparison has been run once on seven held-out conversations. The observed event-over-fixed difference is small and mixed across conversations; thesis writing is pending.**

Research question: Under the same retrieval ranker and retrieved-text budget, does lightweight event-oriented segmentation improve retrieval of annotated evidence turns from long conversations over fixed-size chunks and session chunks? The project evaluates retrieval only. It does not claim to build or evaluate a complete dialogue agent, answer generator, or neural memory mechanism.

## Data provenance

Source: [LoCoMo](https://github.com/snap-research/locomo), Maharana et al., ACL 2024. The dataset is distributed under [CC BY-NC 4.0](https://github.com/snap-research/locomo/blob/main/LICENSE.txt). `data/raw/locomo10.json` is intentionally excluded from git. The code and documentation here are original project work; cite the upstream authors when using the data.

Pinned upstream blob SHA-1: `d95b872480b413d935821fdc3c84f8a8f5f29e73`  
Dataset SHA-256: `79fa87e90f04081343b8c8debecb80a9a6842b76a7aa537dc9fdf651ea698ff4`

The original file can be downloaded and verified with `python scripts/fetch_data.py` on a machine with Internet access. If upstream changes, the script fails instead of silently substituting a new dataset. Then run `python scripts/audit_data.py`. Python 3.9+ standard library suffices for Phase 1.

## Phase 1 result

The verified source has 10 conversations, 272 sessions, 5,882 turns and 1,986 questions. The frozen text-only evaluation subset contains 873 questions: 274 from three development conversations and 599 from seven held-out conversations. The complete eligibility manifest and counts are in `results/phase1_audit.json`; exact rules are in `configs/protocol.json` and explained in [`docs/phase1.md`](docs/phase1.md).

The small 12-question locally authored T4 demonstration is **not** a result for this dataset and will not be reported as an empirical finding in the thesis.

## Planned phases

1. Data audit and precommitted eligibility (this commit).
2. Fixed and session baselines with a shared lexical ranker (development run complete).
3. Lightweight event segmentation; development-only tuning (complete; selected settings frozen).
4. Held-out comparison at equal retrieved-text budgets and descriptive error/cost analysis (complete).
5. Reproducible results, demo, and Persian RTL B Nazanin undergraduate thesis.

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

**The held-out result is recorded. It does not establish a reliable advantage for event segmentation over fixed chunks.**
