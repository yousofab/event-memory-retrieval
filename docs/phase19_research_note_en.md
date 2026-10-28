# Session access can improve while annotated evidence coverage falls

Yousef Abolfathi Roozbahani

Research checkpoint 19, 25 October 2026. This is a working research note, not a peer-reviewed publication or a final thesis.

## Abstract

We audit whether session-diverse anchors improve evidence retrieval under a fixed source-word cap. A frozen text-only BM25 ranking supplies 64 candidates and 8 anchors. Reserving4 distinct sessions is the locally registered primary policy; reserving 8 is a secondary dose. A causal writer and centered selector share each policy's native midpoint cells and round-robin widths. We recompute exact complete-reference feasibility and minimum budgets for each changed anchor space. The study uses 599 reused LoCoMo questions in 7 conversations and 609 prospectively sealed fine-grained questions in 4 generated EverMemBench-Dynamic projects after excluding a schema-only topic. At1,024 words, reserve 4 is nearly a no-op and shows no useful benefit. Reserve8 increases all-reference-session access from 493 to 507 LoCoMo queries and 49 to 59 external queries, but reduces LoCoMo complete evidence from 443 to 401 and external equal-project complete-message recall from 19.53% to 15.65%. A separately registered exploratory amendment matches the number of anchor edits and derives an exact combinatorial session-access expectation. Reserve8 exceeds that expectation on access but underperforms the mean of 10 matched-edit controls on realized coverage by 4.01 and 1.42 percentage points, respectively. This bounded negative finding separates reaching an annotated session from assembling its annotated evidence.

## Motivation and prior art

MMR establishes relevance–diversity reranking; SeCom studies memory granularity; BFR studies complementary evidence and expansion; Raw-RAG supplies a strong raw-history baseline. MemDerive and other diagnostics establish that final answers alone hide intermediate failures. Our contribution is the specific reproducible intervention and audit contract, an edit-count-matched analytical access null, and a transfer study with explicit measurement limits. We do not claim global priority for diversification, oracle diagnosis or complete evidence metrics. The12-entry primary-source atlas records versions, source status and actual reading scope. Other papers' methods were not rerun and their answer scores are not ranked against ours.

## Design

Within each source history, BM25 uses the unchanged tokenizer and constants. For R_r, reserve the first representatives of r distinct native sessions in top 64, fill to 8 with the original ranking, then restore original rank order. R4 is primary and R8 secondary. R_r retains rank 1, represents at least min(r,S) pool groups and replaces at most r-1 original top 8 anchors. This does not guarantee gold coverage. Native sessions are released LoCoMo sessions or external(date,group) units, not human event boundaries. All-speaker message text is indexed; answer strings, reference locators, profiles and role/time prefixes do not enter selection.

Policy-specific anchors induce new native cells. We reuse the proved Phase18 criterion: all gold sessions must be available and each allocated width must cover its anchor-containing required interval. Exact minimum budget and constructive witnesses are recalculated; the old 468 ceiling is not transferred. The two selectors share opportunities within a policy, while opportunities differ across policies. All primary conditions spend exactly 1,024 unique source words; cap saturation is reported for secondary budgets.

Question means are averaged equally across histories. The primary LoCoMo endpoint is complete coverage of all nonempty annotated turns; the external endpoint is mean complete-reference-message recall. These outcomes are not pooled. Paired history bootstrap intervals and leave-one-history-out ranges are descriptive. The predefined 2-point advancement rule failed. Four generated projects and repeated questions/seeds do not constitute a large independent sample.

## Main findings and manipulation check

R4 changes 8/599 and 1/609 anchor sets; the five shuffled-label controls are also almost entirely unchanged. This weak intervention prevents interpreting a null effect as a general rejection of session structure. R8 changes 529/599 and 344/609 sets. It improves complete-session access, yet its LoCoMo exact feasibility falls 468→461 and realized complete coverage falls 443→401, comprising 51 lost and 9 gained successes. Every evaluated history has a negative R8-minus-top 8 point effect on its source's registered outcome. The equal-history effects are-8.07 and-3.88 percentage points. These are algorithmic paired comparisons under this contract, not a general causal claim about semantic boundaries.

## Exploratory matched-edit amendment

After viewing the weak sham manipulation, a separate protocol was committed before supplemental scoring. For each query, let d be R8's number of replacements. Keep rank 1, uniformly retain 7-d of the other 7 original anchors and choose d of ranks 9–64. Ten deterministic seeds are averaged within question. Labels enter only evaluation, not anchor selection. The controls match edit count, not BM25 scores or semantic quality.

For a forbidden subset T of reference sessions, if rank 1 lies in T the probability of avoiding T is zero. Otherwise it is

```text
P(avoid T) = choose(7 - n_base(T), 7 - d) / choose(7, 7 - d)
          * choose(56 - n_out(T), d) / choose(56, d).
P(all gold sessions represented) = sum_T (-1)^|T| P(avoid T).
```

More than 8 required sessions implies zero all-session access. Expected fractional session recall follows from each session's miss probability. Fractions are computed exactly. Exhaustive tiny-space enumeration verifies the expectation. This is a null expectation over anchor subsets, not an answer-confidence estimate or a p-value. R8's access exceeds this exact null by 4.25 and 3.71 points; its realized coverage is lower than matched random edits. The amendment remains exploratory and does not replace the failed primary result.

## Reference granularity and limits

External references have median 29 messages and 1,435 regex words, versus 1 message and 34 words in LoCoMo. Of609 external questions,431 contain more than 1,024 annotated words and 236 require more than 8 annotated sessions. Complete annotation coverage is structurally impossible in those respective contracts; semantic answer sufficiency may still be attainable. Only185 external questions have every annotated session in top 64, versus 586/599 LoCoMo questions. References are contextual snippets, not minimal answer evidence. We report retrieval coverage, not official benchmark QA accuracy. A single lexical ranker, one writer and four new generated projects limit generalization. All external outcomes are now exposed for future phases. Human episodic perception, Searlean understanding and neural mechanisms are not measured.

## Reproducibility

There are 1,208 distinct questions and 130,464 policy–selector–budget conditions, not 130,464 independent observations. Core code uses the Python standard library and CPU, with 0 commercial inference calls. All3,594 historical LoCoMo baseline conditions reproduce exactly. Portable validators check 4,360+5,188 finite thresholds and 11,057+13,208 feasible witnesses, costs, legality and summaries. The full suite runs 70 tests with 69 successes and 1 historical missing-data skip; all 11 new tests run. Numeric artifacts reproduce byte-for-byte, and 47 historical result files remain unchanged. The initial 19B empty saved row artifact was rejected; only complete validated reruns are retained. See the execution ledger for the transparent chronology and source hashes.

## Acknowledgments

We thank Amir Noori for university supervision and support of new ideas, and Dr Arash Fekri, founder of FARDIAT, for education in cognitive neuroscience and review and approval of the original proposal.

## Primary sources

- [R01] The use of MMR, diversity-based reranking for reordering documents and producing summaries. https://doi.org/10.1145/290941.291025
- [R02] Relevance Is Not Sufficiency: What Actually Closes the Evidence Gap in Long-Term Memory QA. https://arxiv.org/abs/2610.09348
- [R03] Is Complex Agentic Memory Always Needed? Naive RAG Is Stronger Than We Thought. https://arxiv.org/abs/2610.30755
- [R04] SeCom: On Memory Construction and Retrieval for Personalized Conversational Agents. https://proceedings.iclr.cc/paper_files/paper/2025/hash/e56f394bbd4f0ec81393d767caa5a31b-Abstract-Conference.html
- [R05] MemDerive: A Diagnostic Benchmark for Agent Memory over Evolving Data. https://arxiv.org/html/2610.25373v1
- [R06] DyadMem: A Long-Term Memory Benchmark of How Agents Work with Users. https://arxiv.org/abs/2610.03020
- [R07] Entity-Memory Graph Retrieval Improves Evidence Coverage in Long-Conversation Question Answering. https://arxiv.org/abs/2608.27925
- [R08] Do Personalized LLMs Need the Whole Conversation? Matching the Full History with Only 5% of Its Text via Relevance-Filtered Context. https://arxiv.org/abs/2610.14952
- [R09] Evaluating Long-Horizon Memory for Multi-Party Collaborative Dialogues. https://arxiv.org/html/2602.01313v3
- [R10] Evaluating Very Long-Term Conversational Memory of LLM Agents. https://doi.org/10.18653/v1/2024.acl-long.747
- [R11] Multiple event segmentation mechanisms in the human brain. https://doi.org/10.7554/eLife.107955.3
- [R12] Lost in the Middle: How Language Models Use Long Contexts. https://doi.org/10.1162/tacl_a_00638
