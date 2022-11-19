import sys
import runpy
from pathlib import Path

import nox

# Global configuration
# https://nox.thea.codes/en/stable/config.html#modifying-nox-s-behavior-in-the-noxfile
nox.options.error_on_missing_interpreters = False

PIPELINES = Path(__file__).parent / 'pipelines'

sys.path.append(str(Path.cwd()))

for file in PIPELINES.iterdir():
    if file.name.endswith('.nox.py'):
        runpy.run_path(str(file))
