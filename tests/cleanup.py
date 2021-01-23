import subprocess
from pathlib import Path


def main() -> None:
    """Remove auto-generated python files"""
    directory = Path.cwd().joinpath('prisma')
    templates = Path.cwd().joinpath('prisma/generator/templates')
    for template in templates.glob('**/[!_]*.py.jinja'):
        path = directory.joinpath(
            *template.parts[template.parts.index('templates') + 1 : -1],
            template.name.rstrip('.jinja')
        )

        if path.exists():
            path.unlink()

        # TODO: output error if unexpected error occurs
        # if the template replaces an existing file then we need to
        # revert to the original file
        subprocess.run(  # pylint: disable=subprocess-run-check
            ['git', 'checkout', path],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.STDOUT,
        )


if __name__ == '__main__':
    main()
