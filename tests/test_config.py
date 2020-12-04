#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import pytest

from tempor.utils import random_number

def test_random_number():
    assert random_number().isnumeric()

def test_raise_exception_on_invalid_random_number():
    with pytest.raises(Exception):
        random_number('j')

