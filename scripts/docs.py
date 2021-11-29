import re
from pathlib import Path


ROOTDIR = Path(__file__).parent.parent


def main() -> None:
    # TODO: this should be a mkdocs plugin
    # then we don't have to run this every time the README is updated
    # and remove docs/index.md from version control
    content = ROOTDIR.joinpath('README.md').read_text()
    content = re.sub(r'\(docs(\/.*)\.md(#.*)?\)', r'(\1/\2)', content)
    content = content.replace('./docs/showcase.gif', './showcase.gif')
    ROOTDIR.joinpath('docs/index.md').write_text(content)


if __name__ == '__main__':
    main()
