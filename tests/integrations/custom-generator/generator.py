from pathlib import Path
from pydantic import BaseModel
from prisma.generator import GenericGenerator, Manifest, models


class Data(models.Data):
    generator: 'GeneratorData'


class GeneratorData(models.Generator):
    config: 'Config'  # type: ignore


class Config(BaseModel):
    header: str = '# My Prisma Models'


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


Data.update_forward_refs()
GeneratorData.update_forward_refs()

if __name__ == '__main__':
    MyGenerator.invoke()
