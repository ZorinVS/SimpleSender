import re

from mailings.management.utils.shared import emails


def has_value(value):
    return value != ""


def is_alpha(string):
    if string == "" or string == "*":
        return True
    return string.isalpha()


def is_email(email):
    if email in emails:
        print("          - Клиент с такой почтой уже имеется")
        return False
    elif email == "*":
        return True
    pattern = re.compile(r"^[a-z0-9_.]+@[a-z]+\.[a-z]+$")
    return pattern.match(email) is not None


def do_stop(*inputs):
    for command in inputs:
        if command == "*":
            return True
    return False
