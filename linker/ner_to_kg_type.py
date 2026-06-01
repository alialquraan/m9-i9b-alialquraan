"""Mapping from spaCy NER labels to KG class URIs.

This is the REFERENCE mapping bundled with the integration. The lab starter
ships only two entries and asks the learner to fill the rest; this integration
ships the complete mapping so the reference linker works out of the box.
"""

# Namespace prefix used for the KG types — matches the KG's `@prefix :`.
RECIPES = "http://aispire.example.org/recipes/"

NER_LABEL_TO_KG_TYPE: dict[str, str] = {
    "PERSON": f"{RECIPES}Author",
    "GPE": f"{RECIPES}Cuisine",
    "NORP": f"{RECIPES}Cuisine",
    "PRODUCT": f"{RECIPES}Ingredient",
    "ORG": f"{RECIPES}Cuisine",
}
