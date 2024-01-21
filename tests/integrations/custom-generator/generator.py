from pathlib import Path

from pydantic import BaseModel

from prisma.generator import Manifest, GenericData, GenericGenerator


class Config(BaseModel):
    header: str = '# My Prisma Models'


Data = GenericData[Config]


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
