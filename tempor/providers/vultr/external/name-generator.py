#!/usr/bin/env python3
# -*- coding:utf-8 -*-
from pathlib import Path
import string
import random
import json


def random_line(f):
    with open(f) as fr:
        lines = fr.read().splitlines()
        return random.choice(lines).replace("'", "").lower()


def random_number(min_val=0, max_val=100):
    return str(random.randint(min_val, max_val))


def random_str(min_val=5, max_val=10):
    return "".join(
        [
            random.choice(string.ascii_lowercase)
            for _ in range(random.randint(min_val, max_val))
        ]
    )


try:
    wordlist = Path("/usr/share/dict/american-english")
    if not wordlist.is_file():
        raise FileNotFoundError
    name = f"{random_line(wordlist)}{random_number()}"
except FileNotFoundError:
    name = f"{random_str()}{random_number()}"

result = {"name": name}
print(json.dumps(result))
