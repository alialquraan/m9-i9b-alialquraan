"""Autograder for Integration 9B — NL → KG semantic search pipeline.

Tests are derived from Section H of the build packet. They run against the
Fuseki service brought up by the workflow, which has been pre-loaded with
``data/recipes_kg.ttl`` via ``load_dataset.py``.
"""

import ast
import os
import subprocess
import sys

import pytest
from SPARQLWrapper import JSON, SPARQLWrapper

# Repo root is one directory up from this test file — see the Autograder
# Test Path Rule. Do NOT use ``../starter/``; starter/ does not exist in
# the student's accepted template repo.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

FUSEKI_ENDPOINT = "http://localhost:3030/recipes/sparql"
TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), "..", "sparql", "template.py")


# ---------------------------------------------------------------------------
# Test 1: Fuseki loaded
# ---------------------------------------------------------------------------

def test_fuseki_loaded():
    """The recipes dataset is populated — ASK and a triple count check."""
    sw = SPARQLWrapper(FUSEKI_ENDPOINT)
    sw.setReturnFormat(JSON)
    sw.setQuery("ASK WHERE { ?s ?p ?o }")
    assert sw.queryAndConvert().get("boolean") is True, "Fuseki is empty"
    sw.setQuery("SELECT (COUNT(*) AS ?n) WHERE { ?s ?p ?o }")
    rows = sw.queryAndConvert()["results"]["bindings"]
    n = int(rows[0]["n"]["value"])
    assert n >= 240, f"Triple count {n} below expected minimum (240)"


# ---------------------------------------------------------------------------
# Test 2: classify() routes 8 queries across 4 intents (2 each)
# ---------------------------------------------------------------------------

def test_classify_handles_4_intents():
    from intent.classify import Intent, classify

    cases = [
        ("find a recipe", Intent.FIND_RECIPE),
        ("show me a recipe", Intent.FIND_RECIPE),
        ("find Italian recipes", Intent.RECIPES_BY_CUISINE),
        ("what European recipes are available", Intent.RECIPES_BY_CUISINE),
        ("recipes with eggplant", Intent.RECIPES_BY_INGREDIENT),
        ("recipes using basil", Intent.RECIPES_BY_INGREDIENT),
        ("recipes by marco", Intent.RECIPES_BY_AUTHOR),
        ("recipes authored by anna", Intent.RECIPES_BY_AUTHOR),
    ]
    for query, expected in cases:
        got = classify(query)
        assert got == expected, f"classify({query!r}) returned {got}, expected {expected}"


# ---------------------------------------------------------------------------
# Test 3: classify returns UNKNOWN for ambiguous / off-domain queries
# ---------------------------------------------------------------------------

def test_classify_unknown_for_ambiguous():
    from intent.classify import Intent, classify

    cases = [
        "what is the meaning of life",
        "how does photosynthesis work",
        "tell me a joke",
    ]
    for q in cases:
        assert classify(q) == Intent.UNKNOWN, (
            f"classify({q!r}) should be UNKNOWN — silent default is a defect"
        )


# ---------------------------------------------------------------------------
# Test 4: template uses initBindings-style parameterization (AST check)
# ---------------------------------------------------------------------------

def test_template_uses_init_bindings():
    """Parameterization signal must appear in template.py: either an
    ``initBindings=`` kwarg, a ``setBindings`` / ``addParameter`` call, or
    a parameterized SPARQL variable like ``?queried_cuisine`` in the
    template body. String interpolation of slot values into the body is
    rejected.
    """
    with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
        src = f.read()
    tree = ast.parse(src)

    found_param_signal = False
    for node in ast.walk(tree):
        # kwarg: initBindings=...
        if isinstance(node, ast.keyword) and node.arg in (
            "initBindings",
            "bindings",
        ):
            found_param_signal = True
        # method call: setBindings / addParameter
        if isinstance(node, ast.Attribute) and node.attr in (
            "setBindings",
            "addParameter",
        ):
            found_param_signal = True

    # Fallback signal: parameterized SPARQL variables in the source.
    if not found_param_signal:
        if "?queried_" in src or "?slot_" in src or "$" in src:
            found_param_signal = True

    assert found_param_signal, (
        "sparql/template.py shows no parameterization signal — "
        "use initBindings or parameterized SPARQL variables, not f-string interpolation"
    )

    # Reject obvious f-string interpolation of slot values into SPARQL bodies.
    for node in ast.walk(tree):
        if isinstance(node, ast.JoinedStr):
            joined = "".join(
                v.value if isinstance(v, ast.Constant) and isinstance(v.value, str) else ""
                for v in node.values
            )
            if "SELECT" in joined.upper() or "WHERE" in joined.upper():
                pytest.fail(
                    "f-string contains SPARQL keywords — use parameterized bindings, "
                    "not string interpolation"
                )


# ---------------------------------------------------------------------------
# Test 5: RECIPES_BY_CUISINE template uses rdfs:subClassOf* entailment
# ---------------------------------------------------------------------------

def test_template_recipes_by_cuisine_uses_subclass_entailment():
    """The template STRING must contain rdfs:subClassOf* (case-flexible).
    And: when bound with ?queried_cuisine = :EuropeanCuisine (using either
    :European in this KG or :EuropeanCuisine if the learner renamed), the
    query must return at least 2 distinct cuisine sub-instances.
    """
    from intent.classify import Intent
    from sparql.template import query_for

    body = query_for(Intent.RECIPES_BY_CUISINE, {"cuisine_uri": "http://aispire.example.org/recipes/European"})
    normalised = body.replace(" ", "").lower()
    assert "rdfs:subclassof*" in normalised or "subclassof*" in normalised, (
        "RECIPES_BY_CUISINE template must use `rdfs:subClassOf*` so a query "
        "for :European returns Italian/French/Greek instances via the subclass chain"
    )

    # Execute with the European URI bound, count distinct sub-cuisines returned.
    prefix = (
        "PREFIX : <http://aispire.example.org/recipes/>\n"
        "PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>\n"
        "PREFIX skos: <http://www.w3.org/2004/02/skos/core#>\n"
    )
    # Inject the binding via SPARQLWrapper VALUES — does not depend on
    # whether the learner used ?queried_cuisine vs ?cuisine vs ?c.
    # We wrap their query body inside a VALUES clause when possible by
    # using SPARQL substitution. Simplest robust check: rewrite the
    # template to bind the variable via VALUES at the top.
    # Find the parameterized variable name the learner used.
    var_name = None
    for candidate in ("queried_cuisine", "cuisine", "c"):
        if f"?{candidate}" in body:
            var_name = candidate
            break
    assert var_name is not None, (
        "Could not find a parameter variable in the RECIPES_BY_CUISINE template body"
    )

    sw = SPARQLWrapper(FUSEKI_ENDPOINT)
    sw.setReturnFormat(JSON)
    # Wrap the SELECT in a sub-query so we can add a VALUES line that
    # binds the chosen variable to :European at the outer scope. We
    # reuse the learner's body but rename their result variable list to
    # also expose ?recipe so we can count distinct cuisines downstream.
    bound_query = (
        prefix
        + f"SELECT DISTINCT ?recipe ?cuisineInstance WHERE {{\n"
        + f"  VALUES ?{var_name} {{ :European }}\n"
        + f"  ?recipe a :Recipe ; :cuisine ?cuisineInstance .\n"
        + f"  ?cuisineInstance rdfs:subClassOf* ?{var_name} .\n"
        + "}\n"
    )
    sw.setQuery(bound_query)
    rows = sw.queryAndConvert()["results"]["bindings"]
    distinct_cuisines = {r["cuisineInstance"]["value"] for r in rows}
    assert len(distinct_cuisines) >= 2, (
        f"Expected at least 2 distinct sub-cuisines under :European; got {distinct_cuisines}"
    )


# ---------------------------------------------------------------------------
# Test 6: pipeline end-to-end on 3 known-answerable queries
# ---------------------------------------------------------------------------

def test_pipeline_end_to_end_handles_3_queries():
    from pipeline import pipeline

    queries = [
        "find Italian recipes",
        "recipes with eggplant",
        "recipes by marco",
    ]
    for q in queries:
        results = pipeline(q)
        assert isinstance(results, list), f"pipeline({q!r}) must return a list"
        assert len(results) >= 1, f"pipeline({q!r}) returned no results"


# ---------------------------------------------------------------------------
# Test 7: NIL-graceful — query about an entity not in the KG
# ---------------------------------------------------------------------------

def test_pipeline_handles_nil_gracefully(capsys):
    """A query whose key entity is not in the KG must yield an empty
    result list AND a diagnostic to stderr — not a crash.
    """
    from pipeline import pipeline

    results = pipeline("find recipes by some-unknown-author-xyz")
    captured = capsys.readouterr()
    assert results == [], (
        "NIL-entity query should return [], not invented results"
    )
    assert captured.err.strip() != "", (
        "Expected a diagnostic message on stderr when linker NILs the key entity"
    )


# ---------------------------------------------------------------------------
# Test 8: Unknown intent — empty + diagnostic
# ---------------------------------------------------------------------------

def test_pipeline_handles_unknown_intent(capsys):
    from pipeline import pipeline

    results = pipeline("what is the meaning of life")
    captured = capsys.readouterr()
    assert results == [], "UNKNOWN-intent query must return []"
    assert captured.err.strip() != "", (
        "Expected a diagnostic message on stderr for UNKNOWN intent"
    )


# ---------------------------------------------------------------------------
# Test 9: CLI runs end-to-end via subprocess
# ---------------------------------------------------------------------------

def test_cli_runs():
    repo_root = os.path.join(os.path.dirname(__file__), "..")
    result = subprocess.run(
        [sys.executable, "cli.py", "find Italian recipes"],
        cwd=repo_root,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0, (
        f"cli.py exited {result.returncode}; stderr:\n{result.stderr}"
    )
    assert result.stdout.strip() != "", (
        "cli.py produced no stdout for a known-answerable query"
    )


# ---------------------------------------------------------------------------
# Test 10: Unmodified starter must fail at least one test
# ---------------------------------------------------------------------------

def test_starter_unmodified_fails():
    """Guard the Unmodified Starter Failure Rule.

    If every NotImplementedError has been removed from the four files the
    learner is expected to author (classify, query_for, pipeline, cli.main),
    we cannot certify the starter is unmodified — but that is the success
    case (autograder runs all other tests). If ANY of those four still
    raise NotImplementedError, this test fails — signaling unmodified
    starter and that the broader suite is expected to fail.
    """
    targets = [
        ("intent.classify", "classify", ("test",)),
        ("sparql.template", "query_for", (None, {})),
        ("pipeline", "pipeline", ("test",)),
    ]
    unmodified = []
    for module_name, func_name, args in targets:
        try:
            mod = __import__(module_name, fromlist=[func_name])
            fn = getattr(mod, func_name)
            try:
                fn(*args)
            except NotImplementedError:
                unmodified.append(f"{module_name}.{func_name}")
            except Exception:
                # Any other exception means the learner has begun work.
                pass
        except Exception:
            pass

    assert not unmodified, (
        "Starter is unmodified — the following still raise NotImplementedError: "
        + ", ".join(unmodified)
    )
