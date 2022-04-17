from prisma.generator import (
    GenericGenerator,
    GenericData,
    BaseConfig,
    Manifest,
)


# custom options must be defined using a pydantic BaseModel
class Config(BaseConfig):
    my_option: int


# we don't technically need to define our own Data class
# but it makes typing easier
class Data(GenericData[Config]):
    pass


# the GenericGenerator[Data] part is what tells Prisma Client Python to use our
# custom Data class with our custom Config class
class MyGenerator(GenericGenerator[Data]):
    def get_manifest(self) -> Manifest:
        return Manifest(
            name='My Custom Generator Options',
            default_output='schema.md',
        )

    def generate(self, data: Data) -> None:
        # generate some assets here
        pass


if __name__ == '__main__':
    MyGenerator.invoke()
