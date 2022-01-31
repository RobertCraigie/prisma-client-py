import re
from pathlib import Path
from prisma.binaries.constants import PRISMA_VERSION


ROOTDIR = Path(__file__).parent.parent
DOCS_DIR = ROOTDIR / 'docs'


def main() -> None:
    # TODO: this should be a mkdocs plugin
    # then we don't have to run this every time the README is updated
    # and remove docs/index.md from version control
    content = ROOTDIR.joinpath('README.md').read_text()
    content = re.sub(r'\(docs(\/.*)\.md(#.*)?\)', r'(\1/\2)', content)
    content = content.replace('./docs/showcase.gif', './showcase.gif')
    ROOTDIR.joinpath('docs/index.md').write_text(content)

    # update the referenced PRISMA_VERSION to the latest version we support
    binaries_doc = DOCS_DIR / 'reference' / 'binaries.md'
    assert binaries_doc.exists()
    content = binaries_doc.read_text()
    content = re.sub(
        r'(git clone https://github.com/prisma/prisma-engines --branch)=(\d+\.\d+\.\d+)',
        r'\1' + '=' + PRISMA_VERSION,
        content,
    )
    binaries_doc.write_text(content)


if __name__ == '__main__':
    main()
