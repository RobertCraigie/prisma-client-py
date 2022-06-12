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
class MyConfig(BaseModel):
    value: int


MyData = models.GenericData[MyConfig]


class MyGenerator3(GenericGenerator[MyData]):
    def generate(self, data: MyData) -> None:
        reveal_type(data.generator.config.value)  # T: int


MyGenerator3.invoke()


# case: unimplemented methods
class MyGenerator4(GenericGenerator[models.DefaultData]):
    pass


MyGenerator4().run()  # E: Cannot instantiate abstract class "MyGenerator4"


# case: mismatched type annotation
class MyGenerator5(GenericGenerator[models.DefaultData]):
    def generate(  # E: Method "generate" overrides class "GenericGenerator" in an incompatible manner
        self, data: MyConfig
    ) -> None:
        pass
