from pydantic import BaseModel


__all__ = ('Engine',)


class Engine(BaseModel):
    name: str
    env: str
