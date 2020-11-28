#!/usr/bin/env python
# -*- coding:utf-8 -*-
from pathlib import Path
import random
import json

def random_line(f):
    with open(f) as fr:
        lines = fr.read().splitlines()
        return random.choice(lines).replace('\'', '').lower()

def random_number(min_val=0, max_val=100):
    return str(random.randint(min_val, max_val))

try:
    wordlist = Path('/usr/share/dict/american-english')
    if not wordlist.is_file():
        raise FileNotFoundError
    result = {
        'name': f'{random_line(wordlist)}{random_number()}'
    }
    print(json.dumps(result))
except FileNotFoundError:
    print('Install dictionary not found')
    exit(1)
