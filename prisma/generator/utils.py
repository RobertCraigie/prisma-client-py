import re


CAMEL_TO_SNAKE_1 = re.compile(r'(.)([A-Z][a-z]+)')
CAMEL_TO_SNAKE_2 = re.compile(r'([a-z0-9])([A-Z])')


def camelcase_to_snakecase(name):
    name = CAMEL_TO_SNAKE_1.sub(r'\1_\2', name)
    return CAMEL_TO_SNAKE_2.sub(r'\1_\2', name).lower()
