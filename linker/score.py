"""Precision / recall / F1 against a gold set — reference implementation.

Not used by the integration pipeline; bundled so the lab-style evaluation
harness still works from inside this repo if a learner wants to re-run
their evaluation here.

Evaluation Methodology (identical to the lab spec, lab guide, and the lab
starter docstring — see Evaluation Methodology Rule):

- **Filter** ``predictions`` to the ``(doc_id, start, end)`` keys present
  in ``gold`` before scoring. A prediction whose key is not in gold is
  dropped (not counted as a false positive).
- **Counting rules** for each gold key:
  * **TP** iff predicted URI exactly matches gold URI AND gold URI is not NIL.
  * **FP** iff prediction is a non-NIL URI different from gold (mismatch
    OR gold is NIL).
  * **FN** iff gold URI is non-NIL but prediction is NIL or missing.
  * **TN** iff both gold URI and prediction are NIL — excluded from P/R denominators.
- **Macro-average across docs** — compute precision/recall/F1 per
  ``doc_id`` first, then average across docs.
"""

from collections import defaultdict


def _group_by_doc(items: list[dict]) -> dict[str, list[dict]]:
    grouped = defaultdict(list)
    for item in items:
        grouped[item["doc_id"]].append(item)
    return grouped


def score(predictions: list[dict], gold: list[dict]) -> dict:
    """Compute macro-averaged precision / recall / F1.

    Returns dict with keys ``precision``, ``recall``, ``f1`` (4-decimal floats).
    """
    gold_by_doc = _group_by_doc(gold)
    pred_by_doc = _group_by_doc(predictions)
    per_doc = []
    for doc_id, gold_spans in gold_by_doc.items():
        pred_spans = pred_by_doc.get(doc_id, [])
        gold_map = {(g["start"], g["end"]): g.get("gold_uri") for g in gold_spans}
        pred_map = {
            (p["start"], p["end"]): p.get("predicted_uri")
            for p in pred_spans
            if (p["start"], p["end"]) in gold_map
        }
        tp = fp = fn = 0
        for key, g_uri in gold_map.items():
            p_uri = pred_map.get(key)
            if g_uri and p_uri == g_uri:
                tp += 1
            elif g_uri and p_uri is None:
                fn += 1
            elif g_uri and p_uri and p_uri != g_uri:
                fp += 1
            elif (g_uri is None) and (p_uri is not None):
                fp += 1
            # TN-NIL excluded
        p = tp / (tp + fp) if (tp + fp) else 0.0
        r = tp / (tp + fn) if (tp + fn) else 0.0
        f = 2 * p * r / (p + r) if (p + r) else 0.0
        per_doc.append((p, r, f))
    if not per_doc:
        return {"precision": 0.0, "recall": 0.0, "f1": 0.0}
    n = len(per_doc)
    return {
        "precision": round(sum(t[0] for t in per_doc) / n, 4),
        "recall": round(sum(t[1] for t in per_doc) / n, 4),
        "f1": round(sum(t[2] for t in per_doc) / n, 4),
    }
