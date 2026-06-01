# Integration 9B — NL → KG Semantic Search

A small natural-language → SPARQL pipeline over the Week B recipes KG. You
compose: spaCy NER → entity linker → intent classifier → parameterized
SPARQL template → ranked results.

Follow the learner-facing integration guide on the AISPIRE course site for
the full task description.

## What ships in this repo

- `linker/` — **reference** entity linker, fully implemented. Works
  against the lab's `recipes_kg.ttl` via Fuseki at
  `http://localhost:3030/recipes/sparql`.
- `linker_my/` — empty slot. Drop your lab linker here and set
  `USE_MY_LINKER=1` to run the pipeline against your own work.
- `intent/classify.py` — the `Intent` enum is fully defined; you implement
  `classify(query)`.
- `sparql/template.py` — you implement `query_for(intent, slots)`.
- `pipeline.py` — you implement `pipeline(query)`.
- `cli.py` — you implement the argparse + pretty-print entry point.
- `data/recipes_kg.ttl` — same KG as the Week B lab.
- `load_dataset.py` / `docker-compose.yml` — same as the lab.

## Deliverables

1. Implement `intent/classify.py::classify`, `sparql/template.py::query_for`,
   `pipeline.py::pipeline`, and `cli.py::main`.
2. Fill in `learner_notes.md` (4 numbered sections).
3. Open a PR with `learner_notes.md` rendered (or linked) in the description.

## Local run

```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
docker compose up -d
python load_dataset.py
pytest tests/ -v

# Once your CLI works:
python cli.py "find me a quick Italian recipe with eggplant"
```

## Submission

`Paste your PR URL into TalentLMS → Module 9 Week B → Integration Task to submit this assignment.`

---

## License

This repository is provided for educational use only. See [LICENSE](LICENSE) for terms.

You may clone and modify this repository for personal learning and practice, and reference code you wrote here in your professional portfolio. Redistribution outside this course is not permitted.
