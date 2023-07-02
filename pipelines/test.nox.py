from __future__ import annotations

import nox

from pipelines.utils import setup_env, maybe_install_nodejs_bin
from pipelines.utils.prisma import generate


@nox.session(python=['3.7', '3.8', '3.9', '3.10', '3.11'])
def test(session: nox.Session) -> None:
    setup_env(session)
    session.install('-r', 'pipelines/requirements/test.txt')
    session.install('.')
    maybe_install_nodejs_bin(session)

    needs_pydantic_settings = True

    pytest_args: list[str] = []
    for arg in session.posargs:
        if arg.startswith('--pydantic-v2='):
            _, value = arg.split('=')
            if value == 'false':
                needs_pydantic_settings = False
                session.install('pydantic<2')
        else:
            pytest_args.append(arg)

    if needs_pydantic_settings:
        session.install('pydantic-settings==2.0.0')

    generate(session)

    session.run(
        'coverage',
        'run',
        '-m',
        'pytest',
        '--ignore=databases',
        *pytest_args,
        env={
            'PYTEST_PLUGINS': 'pytester',
        },
    )
