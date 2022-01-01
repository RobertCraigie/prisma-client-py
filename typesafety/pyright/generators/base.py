from prisma.generator import BaseGenerator


# case: unimplemented methods
class Generator(BaseGenerator):
    pass


Generator().run()  # E: Cannot instantiate abstract class "Generator"
