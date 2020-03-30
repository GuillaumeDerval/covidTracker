import re

FILE = 'nl.txt'
words = open(FILE).read().split("\n")

replace = {
    "é": "e",
    "è": "e",
    "à": "a",
    "ö": "o",
    "ô": "o",
    "â": "a",
    "ï": "i",
    "ê": "e",
    "î": "i",
    "û": "u",
    "ç": "c"
}

def fix_word(w: str):
    for f, t in replace.items():
        w = w.replace(f, t)
    return w.lower()

def is_word_ok(w: str):
    return re.match(r"[a-z0-9]+$", w) and len(w) > 3 and len(w) < 8

words = [fix_word(w) for w in words]
words = sorted(set([w for w in words if is_word_ok(w)]))
open(FILE, 'w').write("\n".join(words))