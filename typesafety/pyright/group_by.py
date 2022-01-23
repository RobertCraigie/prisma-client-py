from prisma.models import Profile


# TODO: more tests


async def order() -> None:
    # case: valid
    await Profile.prisma().group_by(
        ['country'],
        order={
            'country': 'desc',
        },
    )
    await Profile.prisma().group_by(
        ['country', 'city'],
        order={
            'country': 'desc',
        },
    )

    # case: limitation
    # this should error but it is not possible to both resolve the Mapping key type
    # from the TypeVar and limit the number of fields allowed to 1. I would rather
    # error if a non-grouped field is ordered by instead of if more than 1 field is ordered by
    # as I expect the first case to be a more common error
    await Profile.prisma().group_by(
        ['country', 'city'],
        order={
            'country': 'desc',
            'city': 'asc',
        },
    )

    # case: can only order by grouped fields
    await Profile.prisma().group_by(
        ['city'],
        order={  # E: Argument of type "dict[str, str]" cannot be assigned to parameter "order" of type "Mapping[ProfileScalarFieldKeysT@group_by, SortOrder] | List[Mapping[ProfileScalarFieldKeysT@group_by, SortOrder]] | None" in function "group_by"
            'country': 'desc',
        },
    )

    # case: invalid sort order
    await Profile.prisma().group_by(
        ['country'],
        order={  # E: Argument of type "dict[str, str]" cannot be assigned to parameter "order" of type "Mapping[ProfileScalarFieldKeysT@group_by, SortOrder] | List[Mapping[ProfileScalarFieldKeysT@group_by, SortOrder]] | None" in function "group_by"
            'country': 'foo',
        },
    )
