# Reproduce Phase19

The experiment and portable validators use Python3.12 and its standard library.
Plots require matplotlib; Word packaging requires python-docx, B Nazanin and the
document renderer/LibreOffice. Those are not inference dependencies. No commercial
model/API key or GPU is needed. Raw conversations, questions, answers, supplied
textbooks and font binaries are not redistributed.

## Portable checks without raw data

```bash
python -m unittest discover -s tests -v
python scripts/validate_phase17.py --directory results
python scripts/validate_phase18.py --directory results
python scripts/validate_phase19.py --directory results
python scripts/validate_phase19.py --directory results --prefix phase19b
```

The first two historical suites require the pinned numpy/scipy/scikit-learn
versions in `requirements-phase6.txt`; these are historical LSA test dependencies,
not new Phase19 model dependencies. The full recorded suite has70 tests,69 pass
and1 historical Phase14 missing-source skip. All11 Phase19 tests run.

The Phase19 validators independently score window unions, verify native cells,
all policy selections, exact costs, thresholds, feasible witnesses and summaries.
They do not authenticate BM25 rankings against transcripts; that requires the
source-backed replay below. The19B checker also verifies edit counts and exact
rational null expectations. Tiny enumeration tests cover768 null configurations.

## Source-backed replay

Use a new empty directory for each command; runners refuse existing outcomes.
The LoCoMo download must match its original SHA-256. Eight external files are
authenticated by pinned revision, size, Git blob SHA-1 and recorded SHA-256 in
`results/phase19_data_audit.json`. Do not substitute `main` for the pinned dataset
revision `a6b210a32248e841967b7b64a64281d2ff3f669d`.

```bash
python scripts/fetch_data.py
python scripts/fetch_phase19_data.py --download
python scripts/run_phase19_session_access.py --output-dir /tmp/phase19-a-replay
python scripts/validate_phase19.py --directory /tmp/phase19-a-replay
python scripts/run_phase19_edit_controls.py --output-dir /tmp/phase19-b-replay --base-dir results
python scripts/validate_phase19.py --directory /tmp/phase19-b-replay --prefix phase19b --base-dir results
```

For a complete source-only rebuild of19B using newly replayed19A data, use
`--base-dir /tmp/phase19-a-replay` in both19B commands. The query and row files
and deterministic summaries must be byte-identical to the recorded files.
Runtime JSON naturally differs by elapsed time, RSS, current commit and the
tracked-state flag; these fields are not part of deterministic numeric claims.

The canonical19B rows are about49.6MB before gzip. A zero-byte artifact encountered
in an initial saved attempt was rejected, and two later complete runs matched
exactly. Check file hashes and run validators before treating any artifact as a
result. There was no data or parameter change to obtain the accepted reruns.

## Rebuild the analysis and report

```bash
python scripts/analyze_phase19.py --directory results --no-plots
python scripts/analyze_phase19.py --directory results
python scripts/build_phase19_text.py
python scripts/package_phase19.py
```

The first command needs no plotting dependency. Figures have English axes for
portable scientific export; the Persian report has RTL paragraphs, right-aligned
headings, B Nazanin and factual advisor/FARDIAT thanks. PDF is rendered from Word
and visually checked on every page. Exact report-byte reproduction is not claimed
across different Word/LibreOffice versions; numeric-byte reproduction is.

## Chronology and interpretation

- 19A protocol: `58418d8`, implementation: `f84a2ce`, before first new scores.
- 19A preserved outcomes and19B exploratory amendment: `999ac22`.
- 19B implementation and exact-null tests: `dc9b58e`, before19B scores.
- Canonical19B verified rerun: scientific code unchanged, repository commit
  `212d4a6` at start, with clean tracked state. That commit adds literature only.
- Local commits are not independent public preregistration.19B was designed after
  observing19A. EverMemBench topics02–05 are now exposed for any future phase.

The exact oracle uses labels offline. The10 controls are averaged within query.
Neither condition count nor seed count is an independent sample size. Other
papers' reported answer scores are not directly compared with these coverage
outcomes. See `phase19.md`, the two frozen plans and `phase19_execution_notes.md`.

Publication of this new cycle follows the project's final-approval workflow.
Local preparation and successful validation are not a claim of public release.
