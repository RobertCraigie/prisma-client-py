from prisma import validate, types


class Foo:
    pass


def validator() -> None:
    # case: return type instance of type passed
    validated = validate(types.PostCreateInput, {})
    reveal_type(validated)  # T: PostCreateInput

    # case: non-typeddict type
    # these are allowed as we cannot type the TypeVar properly due to a mypy limitation
    validate(Foo, {})
