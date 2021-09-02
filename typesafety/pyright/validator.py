from prisma import validate, types


class Foo:
    pass


def validator() -> None:
    # case: return type instance of type passed
    validated = validate(types.PostCreateInput, {})
    reveal_type(validated)  # T: PostCreateInput

    # case: non-typeddict type
    validate(
        Foo,  # E: Argument of type "Type[Foo]" cannot be assigned to parameter "typ" of type "Type[TypedDictT@validate]" in function "validate"
        {},
    )
