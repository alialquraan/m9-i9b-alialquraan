# linker_my/ — Optional override slot for your lab linker

The integration ships with a fully-implemented reference linker in `linker/`
so you can build the pipeline even if your lab linker fell short of the
P/R/F1 thresholds. If you'd rather run the pipeline against your own lab
linker:

1. Copy your lab `linker/` package contents into this directory
   (`linker_my/lookup.py`, `linker_my/disambiguate.py`, `linker_my/link.py`,
   `linker_my/types.py`, `linker_my/ner_to_kg_type.py`).
2. Make sure `linker_my/__init__.py` exposes a `link(text, ner_spans)`
   function with the same signature as the reference linker.
3. Run the pipeline with `USE_MY_LINKER=1`:

   ```bash
   USE_MY_LINKER=1 python cli.py "find Italian recipes"
   ```

The autograder runs against the reference linker (`USE_MY_LINKER` unset);
the override is for your own exploration.
