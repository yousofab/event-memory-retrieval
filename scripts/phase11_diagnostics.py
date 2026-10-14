"""Post-result descriptive checks of QMSum annotation-grain sensitivity.

These checks were introduced after the planned relevant-turn recall was seen.
They do not replace or reclassify the registered primary outcome.
"""
import gzip
import hashlib
import json
import statistics
from collections import defaultdict

from run_baselines import ROOT


def macro(group, field):
    by_meeting = defaultdict(list)
    for r in group:
        if field == "any_hier":
            value = r["hier_gold"] > 0
        elif field == "any_flat":
            value = r["flat_gold"] > 0
        elif field == "density_hier":
            value = r["hier_gold"] / r["selected_turns"] if r["selected_turns"] else 0
        elif field == "density_flat":
            value = r["flat_gold"] / r["flat_turns"] if r["flat_turns"] else 0
        else:
            raise ValueError(field)
        by_meeting[r["meeting"]].append(value)
    assert len(by_meeting) == 35
    return statistics.mean(statistics.mean(v) for v in by_meeting.values())


def calculate():
    data = json.loads(gzip.decompress((ROOT / "results/phase11_retrieval.json.gz").read_bytes()))
    rows = [r for r in data["per_query"] if r["budget_words"] == 1024 and r["method"] != "global_turn"]
    result = {"status": "post-result exploratory; not prespecified primary", "budget_words": 1024,
              "source_result_sha256": hashlib.sha256(
                  gzip.decompress((ROOT / "results/phase11_retrieval.json.gz").read_bytes())).hexdigest()}
    for field in ("any_hier", "any_flat", "density_hier", "density_flat"):
        values = {}
        for method in ("online", "fixed"):
            values[method] = macro([r for r in rows if r["method"] == method], field)
        randoms = [macro([r for r in rows if r["method"] == "random" and r["seed"] == seed], field)
                   for seed in range(20)]
        values["random_by_seed"] = randoms
        values["random_median"] = statistics.median(randoms)
        result[field] = values
    (ROOT / "results/phase11_posthoc_diagnostics.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return result


if __name__ == "__main__":
    r = calculate()
    for name in ("any_flat", "any_hier", "density_flat", "density_hier"):
        print(name, {k: round(v, 5) for k, v in r[name].items() if k != "random_by_seed"})
