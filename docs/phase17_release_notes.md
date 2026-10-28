Phase 17 is a completed research checkpoint, not the final thesis or a claim of a state-of-the-art memory system.

## Research package

- Controlled retrieval experiment: shared BM25 turn index, eight anchors, identical candidate windows and exact per-window word costs; centered context, frozen event writer and 20 random boundary controls.
- 599 reused LoCoMo questions and 244 reused QMSum queries, three budgets, 55,638 numeric condition rows.
- Phase 1–16 audit, 37-source literature atlas, ten candidate directions, reproducible code, nine Phase 17 tests, figures and Persian RTL B Nazanin reports.
- Original scientific package preserved byte-for-byte; public/local commit mapping and original local Git objects are recorded in `docs/phase17_local_git_history.json`.

## Findings and limitations

At 1,024 words, LoCoMo complete-evidence coverage was **443/599 for the writer versus 442/599 for centered context**. The writer-minus-random conversation-macro difference was **+0.84 percentage points**, below the predeclared two-point practical threshold. QMSum showed no stable transfer benefit. Results are exploratory on previously inspected datasets; they do not measure answer accuracy or human-like understanding. The protocol was registered locally before scoring, not independently timestamped in public. Internal episode lengths are not matched; 11 history–seed pairs have a zero-word partition, as documented in the correction audit.

The release workflow runs only after successful validation of the approved merge. It checks the original artifact hashes before attaching the reports and numeric rows. The full existing suite reports **51 passed and one historical Phase 14 test skipped** because the pinned local Memora copy is absent. All nine Phase 17 tests run. Validation covers **2,529 paired query–budget groups**. CI validates committed results; the separate end-to-end numeric reproduction is documented in the research package.

## Files and next step

Download the PDF or editable Word report from the assets below. `phase17_rows.json.gz` contains numeric results without raw conversations, questions or answers. `phase17_release_sha256.txt` records the approved file hashes; its paths are repository-relative. GitHub's source archives contain the full repository checkpoint, including `docs/phase17_reproduce.md` and `docs/phase18_handoff.md`.

The report files remain the approved pre-publication snapshot. Their historical publication-hold wording is superseded by the researcher's approval recorded in `docs/phase17_publication.md`. Phase 18 is prepared for planning; no Phase 18 experiment or result is claimed. Upstream datasets, supplied textbooks and font files are not redistributed.

<div dir="rtl">

با سپاس از استاد امیر نوری برای راهنمایی دانشگاهی و حمایت از ایده‌های نو، و دکتر آرش فکری، بنیان‌گذار فردیت (FARDIAT)، مجتمع فوق تخصصی مغز و شناخت، برای آموزش علوم اعصاب شناختی و بررسی و تایید پروپوزال.

</div>
