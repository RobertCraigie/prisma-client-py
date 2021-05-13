from typing import Set


__all__ = ('contexts',)


# we use the contexts variable to track code paths in situations where
# nonlocal variables cannot be utilised
# for examples see tests/test_plugins.py for examples
contexts: Set[str] = set()
