import shutil
from pathlib import Path


output = Path(__file__).parent / 'prisma'
if output.exists():
    shutil.rmtree(str(output))


from prisma.cli import prisma

prisma.run(['db', 'push', '--accept-data-loss', '--force-reset'], check=True)
