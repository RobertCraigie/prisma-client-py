import shutil
from pathlib import Path
from prisma.cli import prisma


output = Path(__file__).parent / 'prisma'
if output.exists():
    shutil.rmtree(str(output))

prisma.run(['db', 'push', '--accept-data-loss', '--force-reset'], check=True)
