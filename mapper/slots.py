"""Slot extraction - fill the named slots a shape's Cypher template needs.

Each shape in `shapes.CANONICAL_CYPHER` carries `$param` placeholders.
Your `extract_slots(question, shape)` returns a dict whose keys are the
parameter names the template expects, e.g.:

  ShapeId.Q1 -> {"ingredient": "ginger"}
  ShapeId.Q5 -> {"cuisine": "Sichuan", "ingredient": "ginger"}
  ShapeId.Q9 -> {"cuisine": "Italian"}
  ShapeId.Q10 -> {"max_minutes": 30}
  ShapeId.Q14 -> {"ingredient": "ginger", "exclude_ingredient": "garlic"}

See `data/eval_questions.jsonl` for the gold (question_text, shape, slots)
triples used by the autograder.
"""

import re
from .shapes import ShapeId

# نلغي spacy تماماً لضمان عدم حدوث ModuleNotFoundError في الـ CI
nlp = None

CUISINES = [
    "Italian", "Sichuan", "Mexican", "Indian", "French", "Japanese", 
    "Thai", "Spanish", "Greek", "Lebanese", "Moroccan", "Turkish", 
    "Vietnamese", "Korean", "American", "Caribbean", "Asian", "Chinese"
]

INGREDIENTS = [
    "ginger", "garlic", "onion", "tomato", "chicken", "beef", "pork", 
    "tofu", "rice", "pasta", "basil", "cilantro", "cumin", "turmeric", 
    "chili", "soy sauce", "olive oil", "butter", "milk", "cheese", 
    "egg", "flour", "sugar", "lemon", "lime", "potato", "carrot", 
    "broccoli", "spinach", "mushroom", "shrimp", "salmon", "black pepper", 
    "thyme", "rosemary", "oregano", "parsley", "cinnamon", "honey", "vanilla",
    "peppercorn"
]

TECHNIQUES = [
    "wok", "baking", "grilling", "roasting", "steaming", "frying"
]


def _match_vocabulary(text: str, vocab_list: list) -> str:
    text_lower = text.lower()
    for item in vocab_list:
        if item.lower() in text_lower:
            return item
    return ""


def extract_slots(question: str, shape: ShapeId) -> dict:
    """Extract slot values for the given shape from the question text."""
    slots = {}
    question_lower = question.lower()

    # استخراج اسم الكاتب بالاعتماد الكامل على الـ Regex النظيف والمتوافق مع الاسئلة الـ 15
    if shape in [ShapeId.Q2, ShapeId.Q8]:
        match = re.search(r"by\s+author\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)", question)
        if not match:
            match = re.search(r"by\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)", question)
        if match:
            slots["author"] = match.group(1).strip()

    if shape == ShapeId.Q10:
        match = re.search(r"under\s+(\d+)\s*minutes", question_lower)
        if match:
            slots["max_minutes"] = int(match.group(1))

    if shape == ShapeId.Q14:
        parts = re.split(r"\bbut not\b|\bwithout\b", question_lower, maxsplit=1)
        if len(parts) > 0:
            ing = _match_vocabulary(parts[0], INGREDIENTS)
            if ing:
                slots["ingredient"] = ing
        if len(parts) > 1:
            ex_ing = _match_vocabulary(parts[1], INGREDIENTS)
            if ex_ing:
                slots["exclude_ingredient"] = ex_ing
    else:
        cuisine = _match_vocabulary(question, CUISINES)
        if cuisine:
            slots["cuisine"] = cuisine

        ingredient = _match_vocabulary(question, INGREDIENTS)
        if ingredient:
            slots["ingredient"] = ingredient
            
        technique = _match_vocabulary(question, TECHNIQUES)
        if technique:
            slots["technique"] = technique

    return slots