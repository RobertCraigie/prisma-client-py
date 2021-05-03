from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from prisma.generator import render_template


def test_repeated_rstrip_bug(tmp_path: Path) -> None:
    env = Environment(loader=FileSystemLoader(str(tmp_path)))

    template = 'schema.prisma.jinja'
    tmp_path.joinpath(template).write_text('foo')
    render_template(env, tmp_path, template, dict())

    assert tmp_path.joinpath('schema.prisma').read_text() == 'foo'
