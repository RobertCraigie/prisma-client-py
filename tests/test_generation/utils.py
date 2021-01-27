import os
import sys
import subprocess

import py


class Tmpdir(py.path.local):
    def generate(self, schema: str, options: str) -> None:
        schema_path = self.join('prisma.schema')
        schema_path.write(schema.format(output=self, options=options))
        subprocess.run(
            ['python', '-m', 'prisma', 'generate', f'--schema={schema_path}'],
            check=True,
            env=os.environ,
            stdout=sys.stdout,
            stderr=sys.stderr,
        )
