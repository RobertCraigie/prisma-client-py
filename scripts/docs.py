import re
from pathlib import Path
from prisma import config


ROOTDIR = Path(__file__).parent.parent
DOCS_DIR = ROOTDIR / 'docs'

SHOWCASE_GIF = 'https://raw.githubusercontent.com/RobertCraigie/prisma-client-py/main/docs/showcase.gif'


def main() -> None:
    # TODO: this should be a mkdocs plugin
    # then we don't have to run this every time the README is updated
    # and remove docs/index.md from version control
    content = ROOTDIR.joinpath('README.md').read_text()
    if SHOWCASE_GIF not in content:
        raise RuntimeError(
            'Could not find showcase GIF in README, has it been updated?'
        )

    content = re.sub(r'\(docs(\/.*)\.md(#.*)?\)', r'(\1/\2)', content)
    content = content.replace(SHOWCASE_GIF, './showcase.gif')
    ROOTDIR.joinpath('docs/index.md').write_text(content)

    # update the referenced PRISMA_VERSION to the latest version we support
    binaries_doc = DOCS_DIR / 'reference' / 'binaries.md'
    assert binaries_doc.exists()
    content = binaries_doc.read_text()
    content = re.sub(
        r'(git clone https://github.com/prisma/prisma-engines --branch)=(\d+\.\d+\.\d+)',
        r'\1' + '=' + config.prisma_version,
        content,
    )
    binaries_doc.write_text(content)


if __name__ == '__main__':
    main()
