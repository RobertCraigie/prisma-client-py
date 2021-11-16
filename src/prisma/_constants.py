from typing import Dict


# key aliases to transform query arguments to make them more pythonic
QUERY_BUILDER_ALIASES: Dict[str, str] = {
    'startswith': 'startsWith',
    'endswith': 'endsWith',
    'order_by': 'orderBy',
    'not_in': 'notIn',
    'is_not': 'isNot',
}
