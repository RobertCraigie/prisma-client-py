from pathlib import Path


def main() -> None:
    """Remove auto-generated python files"""
    directory = Path.cwd().joinpath('prisma')
    templates = Path.cwd().joinpath('prisma/generator/templates')
    for template in templates.glob('[!_]*.py.jinja'):
        path = directory.joinpath(template.name.rstrip('.jinja'))

        if path.exists():
            path.unlink()


if __name__ == '__main__':
    main()
