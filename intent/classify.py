"""Map a natural-language query to one of the fixed intents.

The ``Intent`` enum is fully defined so you can import it and refer to
``Intent.FIND_RECIPE`` etc. without authoring the enum yourself. You
implement ``classify(query)`` — see the integration guide for the task
description.
"""

from enum import Enum


class Intent(Enum):
    """Fixed set of intents the pipeline routes between.

    UNKNOWN is reserved for the "no intent matched" case — the classifier
    must abstain rather than silently default to one of the other intents.
    """

    FIND_RECIPE = "find_recipe"
    RECIPES_BY_CUISINE = "recipes_by_cuisine"
    RECIPES_BY_INGREDIENT = "recipes_by_ingredient"
    RECIPES_BY_AUTHOR = "recipes_by_author"
    UNKNOWN = "unknown"


def classify(query: str) -> Intent:
    """Return the Intent the query expresses, or Intent.UNKNOWN on no match.

    The classifier must abstain to Intent.UNKNOWN when no intent applies —
    do not silently default to a specific intent. Implementation is up to
    you (regex, keyword matching, or a small ML classifier).
    """
    # TODO: inspect the query and decide which Intent it matches.
    # Use keyword cues or regex over the query string.
    # TODO: when nothing matches, return Intent.UNKNOWN (do NOT default
    # to FIND_RECIPE or any other intent).
    raise NotImplementedError(
        "Implement classify() — see the integration guide for the task description."
    )
