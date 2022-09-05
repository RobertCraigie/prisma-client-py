from pathlib import Path
from typing import TYPE_CHECKING
from pydantic import BaseModel
from prisma.generator import GenericGenerator, GenericData, Manifest


class Config(BaseModel):
    header: str = '# My Prisma Models'


Data = GenericData[Config]


if TYPE_CHECKING:
    reveal_type(Manifest)
    reveal_type(Manifest.__init__)


class MyGenerator(GenericGenerator[Data]):
    def get_manifest(self) -> Manifest:
        return Manifest(
            name='My Cool Generator',
            default_output=Path(__file__).parent / 'generated.md',
        )

    def generate(self, data: Data) -> None:
        lines = [
            data.generator.config.header,
            '',
        ]
        for model in data.dmmf.datamodel.models:
            lines.append(f'- {model.name}')

        output = Path(data.generator.output.value)
        output.write_text('\n'.join(lines))


if __name__ == '__main__':
    MyGenerator.invoke()
