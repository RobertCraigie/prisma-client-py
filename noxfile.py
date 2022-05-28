import sys
import runpy
from pathlib import Path


PIPELINES = Path(__file__).parent / 'pipelines'

sys.path.append(str(Path.cwd()))

for file in PIPELINES.iterdir():
    if file.name.endswith('.nox.py'):
        runpy.run_path(str(file))
