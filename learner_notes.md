# Integration 9B — Learner Notes

## 1. Intents you handled and how you classified them

I implemented a rule-based intent classifier using keyword matching and
regex patterns over the lowercase question text. Each ShapeId is triggered
by a distinct lexical signal such as "but not" for Q14 (negation),
"authors of" for Q12, and cuisine names for Q3–Q6.

Ambiguity arose mainly between cuisine hierarchy shapes (Q4, Q5, Q6).
For example, "Find Sichuan recipes that use ginger" could be mistaken for
a general cuisine + ingredient conjunction, but I resolved it by prioritizing
Sichuan → Q5 as a specific cuisine level below Chinese/Asian.

A concrete ambiguous case is:
"Find Asian recipes that use ginger" where both Q4 and Q6 patterns could
partially match, resolved by strict hierarchy ordering.

---

## 2. A question that worked end-to-end

Question:
Find recipes by author Maria Rossi

- detect_shape → Q2
- extract_slots → {"author": "Maria Rossi"}
- compile_to_cypher → static template with $author
- params → {"author": "Maria Rossi"}

CLI output:
{'recipe': 'Carbonara'}
{'recipe': 'Lasagna'}
{'recipe': 'Tiramisu'}

---

## 3. A failure mode you diagnosed

Initially, author extraction produced values like "Author Maria Rossi"
which caused parameter mismatch in Cypher execution.

The failure appeared as:
Neo4j ClientError: Expected parameter(s): author

Fix was removing lexical prefixing and returning canonical name only.

For Tier 3 allowlist failures, unsafe Cypher such as DELETE or SET
would be rejected by validate_query_shape and returned with rejected=True.

---

## 4. A design tradeoff between deterministic mapper and Tier 3 chain

The deterministic mapper is preferred for production systems requiring
predictability, auditability, and zero latency variability. It guarantees
exact-result-set equivalence and avoids LLM hallucination risk.

The Tier 3 LLM chain is preferable when schema coverage expands rapidly
or when natural language variability exceeds rule-based intent capacity.
However, it introduces risks in safety validation, latency, and
non-deterministic outputs, requiring allowlist enforcement.