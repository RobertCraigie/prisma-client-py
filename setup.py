#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re

from setuptools import setup, find_packages


with open('requirements.txt') as f:
    requirements = f.read().splitlines()

with open('README.md', 'r') as f:
    readme = f.read()

version = ''
with open('prisma/__init__.py') as f:
    match = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', f.read(), re.MULTILINE)
    if not match:
        raise RuntimeError('version is not set')

    version = match.group(1)

if not version:
    raise RuntimeError('version is not set')


setup(
    name='prisma',
    version=version,
    author='Robert Craigie',
    maintainer='Robert Craigie',
    license='APACHE',
    url='https://github.com/RobertCraigie/prisma-client-py',
    description='Prisma Client Py is an unofficial implementation of the Prisma Client',
    install_requires=requirements,
    long_description=readme,
    long_description_content_type='text/markdown',
    packages=find_packages(include=['prisma', 'prisma.*']),
    project_urls={},
    python_requires='>=3',
    package_data={'': ['generator/templates/*.py.jinja', 'py.typed']},
    include_package_data=True,
    zip_safe=False,
    entry_points={
        'console_scripts': [
            'prisma=prisma.cli:main',
        ],
    },
    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Developers',
        'Topic :: Database :: Database Engines/Servers',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
)
