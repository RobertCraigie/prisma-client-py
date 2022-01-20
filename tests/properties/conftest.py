from typing import Any
from hypothesis import strategies as st

from prisma.types import Serializable
from .utils import GRAPHQL_MAX_INT, GRAPHQL_MIN_INT


st.register_type_strategy(
    int, st.integers(min_value=GRAPHQL_MIN_INT, max_value=GRAPHQL_MAX_INT)
)

# TODO: how should we handle infinity and nan?
st.register_type_strategy(float, st.floats(allow_nan=False, allow_infinity=False))

# TODO: properly
st.register_type_strategy(Any, st.from_type(Serializable))
