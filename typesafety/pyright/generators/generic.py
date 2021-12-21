from pydantic import BaseModel
from prisma.generator import GenericGenerator, models


class Foo:
    pass


# case: missing / invalid type arguments
class MyGenerator1(
    GenericGenerator  # E: Expected type arguments for generic class "GenericGenerator"
):
    pass


class MyGenerator2(
    GenericGenerator[
        Foo  # E: Type "Foo" cannot be assigned to type variable "BaseModelT@GenericGenerator"
    ]
):
    pass


# case: custom config
class MyData(models.Data):
    generator: 'MyGeneratorWrapper'


class MyGeneratorWrapper(models.Generator):
    # TODO: this should be possible without a type: ignore
    config: 'MyConfig'  # type: ignore


class MyConfig(BaseModel):
    value: int


class MyGenerator3(GenericGenerator[MyData]):
    def generate(self, data: MyData) -> None:
        reveal_type(data.generator.config.value)  # T: int


MyGenerator3.invoke()


# case: unimplemented methods
class MyGenerator4(GenericGenerator[models.Data]):
    pass


MyGenerator4().run()  # E: Cannot instantiate abstract class "MyGenerator4"
