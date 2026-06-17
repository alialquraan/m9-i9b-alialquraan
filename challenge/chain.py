"""GraphCypherQAChain-style helper for the live-LLM Tier 3 path.

Triple-stated Tier 3 scoring methodology:
1. exact-result-set equivalence
2. deterministic mapper is the gold
3. row order matters only for the two ranked questions
4. REPORTED SEPARATELY in the autograder summary
5. No partial credit on rows
"""

from __future__ import annotations

import json
from typing import Any
from .allowlist import UnsupportedCypherError, validate_query_shape
from .few_shots import EXAMPLE_PAIRS, SCHEMA_PREAMBLE

try:
    from langchain_neo4j import GraphCypherQAChain  # type: ignore
    LANGCHAIN_AVAILABLE = True
except ImportError:
    GraphCypherQAChain = None  # type: ignore
    LANGCHAIN_AVAILABLE = False


def build_prompt(question: str) -> str:
    """Compose the LLM prompt: schema preamble + few-shots + question."""
    prompt = SCHEMA_PREAMBLE.strip() + "\n\n"

    for item in EXAMPLE_PAIRS:
        q = item.get("question", item.get("q", "")) if isinstance(item, dict) else item[0]
        cypher = item.get("cypher", "") if isinstance(item, dict) else item[1]
        prompt += f"Q: {q}\nCypher: {cypher}\n\n"

    prompt += f"Q: {question}\nCypher:"
    return prompt


def _parse_llm_output(text: str) -> tuple[str | None, dict]:
    """Expected format:
    Cypher: <query>
    Params: {...}
    """
    if not text:
        return None, {}

    cypher = None
    params = {}

    for line in text.splitlines():
        if line.lower().startswith("cypher:"):
            cypher = line.split(":", 1)[1].strip()

        if line.lower().startswith("params:"):
            try:
                params = json.loads(line.split(":", 1)[1].strip())
            except Exception:
                params = {}

    return cypher, params


def run_chain(driver, llm_client, question: str) -> dict[str, Any]:
    """Run one question through the chain end-to-end."""
    prompt = build_prompt(question)
    llm_response = llm_client.invoke(prompt)

    if hasattr(llm_response, "content"):
        llm_text = llm_response.content
    else:
        llm_text = str(llm_response)

    cypher, params = _parse_llm_output(llm_text)

    result = {
        "question": question,
        "cypher": cypher,
        "params": params,
        "rows": [],
        "rejected": False,
        "rejection_reason": None,
    }

    if not cypher:
        return result

    try:
        validate_query_shape(cypher)
    except UnsupportedCypherError as e:
        result["rejected"] = True
        result["rejection_reason"] = str(e)
        return result

    with driver.session() as session:
        rows = session.run(cypher, **params)
        result["rows"] = [r.data() for r in rows]

    return result