from __future__ import annotations

import nox

from pipelines.utils import setup_env, maybe_install_nodejs_bin
from pipelines.utils.prisma import generate


@nox.session(python=['3.7', '3.8', '3.9', '3.10', '3.11', '3.12'])
def test(session: nox.Session) -> None:
    setup_env(session)
    session.install('-r', 'pipelines/requirements/test.txt')
    session.install('.')
    maybe_install_nodejs_bin(session)

    pydantic_v2 = True

    pytest_args: list[str] = []
    for arg in session.posargs:
        if arg.startswith('--pydantic-v2='):
            _, value = arg.split('=')
            if value == 'false':
                pydantic_v2 = False
        else:
            pytest_args.append(arg)

    if pydantic_v2:
        session.install('-r', 'pipelines/requirements/deps/pydantic.txt')
    else:
        session.install('pydantic<2')

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
            'PYTHONHASHSEED': '0',
        },
    )
