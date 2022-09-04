from __future__ import annotations

import nox


def generate(
    session: nox.Session,
    *,
    schema: str | None = 'tests/data/schema.prisma',
    clean: bool = True,
) -> None:
    if clean:
        session.run('python', '-m', 'prisma_cleanup')

    if schema:
        args = (f'--schema={schema}',)
    else:
        args = ()

    session.run('prisma', 'generate', *args)
