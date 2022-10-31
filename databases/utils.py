from typing import Set, get_args
from typing_extensions import Literal

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

    def supports_feature(self, feature: DatabaseFeature) -> bool:
        if feature not in get_args(DatabaseFeature):
            raise RuntimeError(f'Unknown feature: {feature}')

        return feature not in self.unsupported_features
