# Type Safety

<!-- TODO: expand more -->

!!! note
    This page is intended for users that are new to type hinting in python, if you are already using type hints this page will not benefit you.

All Prisma Client Python methods are fully[^1] statically typed, in this page we will explain what this means and why it is important.

## Introduction

Python has support for _hinting_[^2] at the types of objects.

For example, heres a function without any type hints.

```py
def add_numbers(a, b):
    return a + b
```

And heres the same function with type hints.

```py
def add_numbers(a: int, b: int) -> int:
    return a + b
```

For an exhaustive list of examples take a look at the [mypy cheat sheet](https://mypy.readthedocs.io/en/stable/cheat_sheet_py3.html).

## Why should you use type hints?

### Type Checkers

With type hints, python type checkers can easily find bugs before they reveal themselves in your code.

### Documentation

Someone unfamiliar with the codebase (or you in the future) will know what is expected where and can navigate the codebase with ease.

### Improved IDE experience

Among other improvements your IDE will:

- suggest more appropriate completions
- highlight errors in your code

[^1]: There are some limitations on this which are enabled by default, see [limitations](../reference/limitations.md) for why they are imposed and how to remove them.

[^2]: Type hints are not enforced at runtime
