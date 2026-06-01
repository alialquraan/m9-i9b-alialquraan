"""Parameterized SPARQL templates keyed by Intent.

Evaluation Methodology (this docstring is the THIRD statement of the
parameterization + entailment requirement; the same statement appears in
the integration spec and in the learner-facing integration guide):

Every template must use **parameterized variables** (e.g.,
``?queried_cuisine``, ``?queried_ingredient``, ``?queried_author``) —
slot values are bound at execution time in ``pipeline.py`` via
``Graph.query(q, initBindings={...})``, NOT f-string interpolated into
the query body. String interpolation of slot values is an injection
vector and will be rejected by the AST meta-test in the autograder.

The ``RECIPES_BY_CUISINE`` template MUST use ``rdfs:subClassOf*`` over the
cuisine hierarchy so a query bound with ``?queried_cuisine = :European``
returns the recipe instances whose ``:cuisine`` is ``:Italian``,
``:French``, or ``:Greek`` via the subclass chain — not just instances
that are exactly ``:cuisine :European``. Without ``rdfs:subClassOf*``,
the "European" query returns zero rows because no recipe has
``:cuisine :European`` directly.
"""

from intent.classify import Intent


def query_for(intent: Intent, slots: dict) -> str:
    """Return the SPARQL query body for ``intent``.

    The returned query must use parameter placeholders (e.g.,
    ``?queried_cuisine``) that ``pipeline.py`` binds at execution time
    via ``initBindings``. Do NOT interpolate slot values into the
    returned string.

    ``slots`` carries hints from the linker (e.g., which entity URIs were
    resolved) — your template body does not embed them.
    """
    # TODO: write one template per Intent. Each template references
    # the slot via a parameter variable that pipeline.py will bind.
    # TODO: the RECIPES_BY_CUISINE template must use rdfs:subClassOf* on
    # the cuisine variable so subclass entailment works (a query for
    # :European returns :Italian / :French / :Greek instances).
    raise NotImplementedError(
        "Implement query_for() — see the integration guide for the task description."
    )
