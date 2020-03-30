import hashlib
import os
import re

from covidbelgium import Config

word_lists = {"fr": open("dictionaries/fr.txt").read().split("\n"),
              "en": open("dictionaries/en.txt").read().split("\n"),
              "nl": open("dictionaries/nl.txt").read().split("\n")}


def gen_password(lang, size=4):
    """ Generate a password from the word list """
    assert lang in word_lists
    password = []
    for _ in range(size):
        password.append(word_lists[lang][int.from_bytes(os.urandom(4), byteorder='big') % len(word_lists[lang])])
    return "-".join(password)


def hash_password(password):
    dk = hashlib.pbkdf2_hmac('sha256', bytes(password, encoding='utf8'), bytes(Config.SECRET_KEY, encoding='utf8'), 10000)
    return dk.hex()


def is_word_ok(w: str):
    return re.match(r"[a-z0-9]+$", w) and len(w) > 3 and len(w) < 8


def check_password(password):
    words = password.split("-")
    return len(words) == 4 and all(is_word_ok(w) for w in words)
