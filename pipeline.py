"""Pipeline orchestration: spaCy NER -> linker -> intent -> SPARQL -> ranked results.

You implement ``pipeline(query)`` per the integration guide. The reference
linker is wired up below; if you set ``USE_MY_LINKER=1`` in your env, the
pipeline imports ``link`` from ``linker_my`` instead — both modules must
expose ``link(text, ner_spans)`` with the same signature.
"""

import os
import sys
from typing import Any

# Linker override path: set USE_MY_LINKER=1 to use linker_my/ instead of
# the bundled reference linker. Both packages must expose
# `link(text, ner_spans)` with the same signature; see linker_my/README.md.
if os.environ.get("USE_MY_LINKER") == "1":
    from linker_my.link import link  # type: ignore
else:
    from linker.link import link

FUSEKI_ENDPOINT = "http://localhost:3030/recipes/sparql"


def pipeline(query: str) -> list[dict[str, Any]]:
    """Run the natural-language query through the full pipeline.

    Returns a list of result dicts (each with at least ``recipe`` and
    ``name`` keys) ranked by ``:popularityScore`` descending, top-5.
    Returns ``[]`` and writes a diagnostic to ``stderr`` when:
      - the intent classifier returns ``Intent.UNKNOWN``
      - the linker NILs every entity the chosen template depends on

    Order of operations:
      1. Run spaCy NER over ``query`` to extract entity spans.
      2. Call ``link(query, ner_spans)`` to resolve spans to KG URIs.
      3. Call ``classify(query)`` to pick an Intent.
      4. If UNKNOWN: write diagnostic to stderr and return [].
      5. Build slot bindings from the linked URIs for the intent.
      6. If required bindings are missing (all relevant linker results
         are NIL): write diagnostic to stderr and return [].
      7. Call ``query_for(intent, slots)`` to get the SPARQL body.
      8. Execute against Fuseki with ``initBindings`` carrying the slot URIs.
      9. Rank results by ``:popularityScore`` descending, return top-5.
    """
    # TODO: load spaCy en_core_web_sm and run NER over `query` to produce
    # the list of ner_spans dicts (keys: text, label, start, end).
    # TODO: call link(query, ner_spans) and classify(query).
    # TODO: on Intent.UNKNOWN, write a diagnostic to sys.stderr and return [].
    # TODO: build slot bindings from non-NIL LinkResults; if no relevant
    # bindings are available, write a diagnostic to sys.stderr and return [].
    # TODO: execute the parameterized SPARQL via rdflib Graph.query or
    # SPARQLWrapper, passing the slot URIs as initBindings (never as
    # f-string interpolation into the query body).
    # TODO: sort the rows by :popularityScore descending and return the top 5.
    raise NotImplementedError(
        "Implement pipeline() — see the integration guide for the task description."
    )
