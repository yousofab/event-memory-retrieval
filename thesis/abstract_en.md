# Abstract

Conversational memory must retrieve useful evidence from long histories under a limited context budget. Changing memory boundaries can also change document counts, lengths, ranking statistics and selection opportunities, making architectural effects difficult to attribute. This thesis develops a controlled evaluation framework and an offline diagnostic for annotated evidence retrieval.

The central evaluation holds a turn-level BM25 index, anchors, legal windows and actual source-word costs fixed across selectors. An annotation-assisted auditor then determines exact complete-evidence feasibility and the minimum budget within that geometry. The core LoCoMo analysis uses 599 reused questions from seven conversations. Complementary analyses use 244 QMSum queries from 35 meetings and 609 fine-grained EverMemBench-Dynamic queries from four generated projects.

At 1,024 source words, the frozen writer completely covers 443 LoCoMo references, while the conditional diagnostic ceiling is 468. Its 156 failures comprise 106 missing-session cases, 25 geometry-infeasible cases and 25 feasible selection misses. Reserving eight sessions increases complete-session access from 493 to 507 questions, but decreases realized complete evidence from 443 to 401. QMSum similarly shows that approximate topic-onset alignment need not translate into higher retrieval coverage.

The contributions are controlled architecture evaluation, exact diagnosis within a fixed window space, and the empirical separation of session access from local evidence assembly. These are bounded retrieval findings. They do not measure answer accuracy, philosophical understanding or human episodic perception. Reused data, descriptive cluster uncertainty and post-result amendments retain their explicit status. The experimental scope ends at Phase19; the integrated manuscript synthesizes existing measurements without a new experiment.

Keywords  conversational memory, event segmentation, evidence retrieval, feasibility, failure diagnosis, reproducibility
