from typing import Set
from typing_extensions import Literal, get_args

from pydantic import BaseModel


DatabaseFeature = Literal[
    'enum',
    'json',
    'arrays',
    'raw_queries',
    'create_many',
    'case_sensitivity',
]


class DatabaseConfig(BaseModel):
    id: str
    name: str
    env_var: str
    unsupported_features: Set[DatabaseFeature]

    # TODO: run this under coverage
    def supports_feature(
        self, feature: DatabaseFeature
    ) -> bool:  # pragma: no cover
        if feature not in get_args(DatabaseFeature):
            raise RuntimeError(f'Unknown feature: {feature}')

        return feature not in self.unsupported_features
