"""Candidate generation against the live Fuseki endpoint.

Reference implementation. The function talks to Fuseki via an rdflib
``Graph`` backed by ``SPARQLStore`` — the same ``Graph.query(q,
initBindings=...)`` API the M9 Week B drill used against an in-memory
graph, now pointed at remote Fuseki. The KG was POSTed into the
``recipes`` dataset by ``load_dataset.py``. The SPARQL query body
itself does not contain the surface form as text; the surface form is
passed as a parameter binding.
"""

from rdflib import Literal, URIRef

from linker.kg import DEFAULT_ENDPOINT, connect

_CANDIDATES_Q = """
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
SELECT DISTINCT ?uri WHERE {
  VALUES ?surface_form { UNDEF }
  { ?uri skos:prefLabel ?label . } UNION { ?uri skos:altLabel ?label . }
  FILTER (LCASE(STR(?label)) = LCASE(STR(?surface_form)))
}
"""

_HAS_TYPE_Q = "ASK WHERE { ?s a ?t }"


def candidates(surface_form: str, endpoint: str = DEFAULT_ENDPOINT) -> list[str]:
    """Return KG URIs whose skos:prefLabel or skos:altLabel matches surface_form.

    Case-insensitive. The surface form is passed as a SPARQL parameter
    binding via ``initBindings`` — not interpolated into the query body.
    """
    g = connect(endpoint)
    rows = g.query(
        _CANDIDATES_Q, initBindings={"surface_form": Literal(surface_form)}
    )
    return [str(row[0]) for row in rows]


def has_type(uri: str, expected_type: str, endpoint: str = DEFAULT_ENDPOINT) -> bool:
    """Return True iff the KG asserts ``<uri> a <expected_type>``."""
    g = connect(endpoint)
    return bool(
        g.query(
            _HAS_TYPE_Q,
            initBindings={"s": URIRef(uri), "t": URIRef(expected_type)},
        ).askAnswer
    )
