"""KG plumbing — connect an rdflib ``Graph`` to the live Fuseki endpoint.

Fully implemented helper. Provides ``connect()`` returning an rdflib
``Graph`` backed by ``SPARQLStore`` against the Fuseki endpoint, plus an
``ask_has_type()`` helper for the ASK queries the disambiguator runs.

This is plumbing — the integration's pedagogy is intent classification,
SPARQL template authoring, and pipeline orchestration, not how to wire
rdflib to a SPARQL endpoint.
"""

from rdflib import Graph, URIRef
from rdflib.plugins.stores.sparqlstore import SPARQLStore

DEFAULT_ENDPOINT = "http://localhost:3030/recipes/sparql"


def connect(endpoint: str = DEFAULT_ENDPOINT) -> Graph:
    """Return an rdflib ``Graph`` backed by the Fuseki endpoint at ``endpoint``.

    Use ``Graph.query(q, initBindings={...})`` for parameterized queries.
    """
    return Graph(SPARQLStore(query_endpoint=endpoint))


def ask_has_type(uri: str, expected_type: str, endpoint: str = DEFAULT_ENDPOINT) -> bool:
    """Return True iff the KG asserts ``<uri> a <expected_type>``.

    Uses parameterized ASK with ``initBindings`` — URI bindings flow safely
    through ``SPARQLStore`` because they appear in BGP position (not in a
    FILTER expression).
    """
    g = connect(endpoint)
    q = "ASK WHERE { ?s a ?t }"
    return bool(
        g.query(
            q,
            initBindings={"s": URIRef(uri), "t": URIRef(expected_type)},
        ).askAnswer
    )
