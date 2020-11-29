#!/usr/bin/env python
# -*- coding:utf-8 -*-
import string
import secrets
import json

alphabet = string.ascii_letters + string.digits
while True:
    password = ''.join(secrets.choice(alphabet) for i in range(32))
    if (any(c.islower() for c in password)
            and any(c.isupper() for c in password)
            and sum(c.isdigit() for c in password) >= 3):
        break
result = {
    'value': password
}
print(json.dumps(result))
