import re
from pathlib import Path

from prisma import config

ROOTDIR = Path(__file__).parent.parent
DOCS_DIR = ROOTDIR / 'docs'

SHOWCASE_GIF = 'https://raw.githubusercontent.com/RobertCraigie/prisma-client-py/main/docs/showcase.gif'


# TODO: make this nicer


def main() -> None:
    # TODO: this should be a mkdocs plugin
    # then we don't have to run this every time the README is updated
    # and remove docs/index.md from version control
    content = ROOTDIR.joinpath('README.md').read_text()
    if SHOWCASE_GIF not in content:
        raise RuntimeError('Could not find showcase GIF in README, has it been updated?')

    content, n = re.subn(
        r'(<img src="https:\/\/img\.shields\.io\/static\/v1\?label=prisma&message)=(\d?.)+(&color=blue&logo=prisma" alt="Supported Prisma version is) (\d?.)+">',
        r'\1=' + config.prisma_version + r'\3 ' + config.prisma_version + '">',
        content,
    )
    assert n > 0, "Didn't make any replacements"
    ROOTDIR.joinpath('README.md').write_text(content)

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

    # ensure all config defaults are up to date
    config_doc = DOCS_DIR / 'reference' / 'config.md'
    assert config_doc.exists()
    content = config_doc.read_text()
    content = re.sub(
        r'(`PRISMA_VERSION`      \| )`(.*)`',
        r'\1' + '`' + config.prisma_version + '`',
        content,
    )

    content = re.sub(
        r'(`PRISMA_EXPECTED_ENGINE_VERSION` \| )`(.*)`',
        r'\1' + '`' + config.expected_engine_version + '`',
        content,
    )

    config_doc.write_text(content)


if __name__ == '__main__':
    main()
