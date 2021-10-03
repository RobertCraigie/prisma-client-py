#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re
from typing import List
from pathlib import Path
from setuptools import setup, find_packages


def requirements(name: str) -> List[str]:
    root = Path(__file__).parent / 'requirements'
    return root.joinpath(name).read_text().splitlines()


with open('README.md', 'r') as f:
    readme = f.read()

version = ''
with open('src/prisma/__init__.py') as f:
    match = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', f.read(), re.MULTILINE)
    if not match:
        raise RuntimeError('version is not set')

    version = match.group(1)

if not version:
    raise RuntimeError('version is not set')


extras = {
    'dev': requirements('dev.txt'),
    'docs': requirements('docs.txt'),
}


setup(
    name='prisma-client',
    version=version,
    author='Robert Craigie',
    author_email='robert@craigie.dev',
    maintainer='Robert Craigie',
    license='APACHE',
    url='https://github.com/RobertCraigie/prisma-client-py',
    description='Prisma Client Python is an auto-generated and fully type-safe database client',
    install_requires=requirements('base.txt'),
    long_description=readme,
    long_description_content_type='text/markdown',
    packages=find_packages(where='src', include=['prisma', 'prisma.*']),
    package_dir={'': 'src'},
    python_requires='>=3',
    package_data={'': ['generator/templates/**/*.py.jinja', 'py.typed']},
    include_package_data=True,
    zip_safe=False,
    extras_require={
        **extras,
        'all': [req for requirements in extras.values() for req in requirements],
    },
    entry_points={
        'console_scripts': [
            'prisma=prisma.cli:main',
            'prisma-client-py=prisma.cli:main',
        ],
        'prisma': [],
    },
    project_urls={
        'Documentation': 'https://prisma-client-py.readthedocs.io',
        'Source': 'https://github.com/RobertCraigie/prisma-client-py',
        'Tracker': 'https://github.com/RobertCraigie/prisma-client-py/issues',
    },
    keywords=[
        'orm',
        'mysql',
        'typing',
        'prisma',
        'sqlite',
        'database',
        'postgresql',
    ],
    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Developers',
        'Typing :: Typed',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Database :: Database Engines/Servers',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
)
