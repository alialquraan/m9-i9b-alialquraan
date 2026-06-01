"""Orchestrate candidate generation and disambiguation over a set of NER spans.

Reference implementation. ``link(text, ner_spans)`` is the entry point the
integration pipeline calls. ``text`` is the source string (kept for parity
with the lab signature; the reference linker does not use it directly).
``ner_spans`` is a list of dicts with keys ``text``, ``label``, ``start``, ``end``.
"""

from linker.disambiguate import disambiguate
from linker.lookup import DEFAULT_ENDPOINT, candidates
from linker.ner_to_kg_type import NER_LABEL_TO_KG_TYPE
from linker.types import LinkResult


def link(
    text: str,
    ner_spans: list[dict],
    endpoint: str = DEFAULT_ENDPOINT,
) -> list[LinkResult]:
    """Link each NER span to a KG URI (or NIL).

    Returns a list of LinkResult of the same length as ``ner_spans``, in the
    same order. ``reason`` is always populated so downstream debugging can
    attribute every NIL.
    """
    results: list[LinkResult] = []
    linked_uris: list[str] = []
    for span in ner_spans:
        surface = span["text"]
        ner_label = span["label"]
        start = span["start"]
        end = span["end"]

        if ner_label not in NER_LABEL_TO_KG_TYPE:
            results.append(
                LinkResult(surface, None, "nil-no-type-mapping", start, end)
            )
            continue

        cands = candidates(surface, endpoint)
        if len(cands) == 0:
            results.append(
                LinkResult(surface, None, "nil-no-candidates", start, end)
            )
        elif len(cands) == 1:
            uri = cands[0]
            results.append(LinkResult(surface, uri, "resolved-unique", start, end))
            linked_uris.append(uri)
        else:
            uri, reason = disambiguate(
                cands,
                ner_label,
                {"linked_uris": list(linked_uris)},
                endpoint,
            )
            results.append(LinkResult(surface, uri, reason, start, end))
            if uri is not None:
                linked_uris.append(uri)
    return results
