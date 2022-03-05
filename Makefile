.PHONY: bootstrap
bootstrap:
	pip install -U wheel
	pip install -U -e .[all]
	prisma db push --schema=tests/data/schema.prisma
	cp tests/data/dev.db dev.db
	pre-commit install

.PHONY: database
database:
	prisma db push --schema=tests/data/schema.prisma
	cp tests/data/dev.db dev.db

. PHONY: package
package:
	python scripts/docs.py
	python -m prisma_cleanup
	rm -rf dist/*
	python setup.py sdist
	python setup.py sdist bdist_wheel
	sh scripts/check_pkg.sh

. PHONE: release
release:
	sh scripts/check_pkg.sh
	twine upload dist/*

.PHONY: test
test:
	tox $(ARGS)

.PHONY: format
format:
	blue .
	for schema in `find . -name '*.schema.prisma'` ; do \
        prisma format --schema=$$schema ; \
    done

.PHONY: lint
lint:
	tox -e lint

.PHONY: mypy
mypy:
	tox -e mypy

.PHONY: pyright
pyright:
	prisma generate --schema=tests/data/schema.prisma
	pyright

.PHONY: typesafety
typesafety:
	tox -e typesafety-pyright,typesafety-mypy

.PHONY: docs
docs:
	python scripts/docs.py
	mkdocs build

.PHONY: docs-serve
docs-serve:
	python scripts/docs.py
	mkdocs serve

.PHONY: clean
clean:
	python -m prisma_cleanup
	rm -rf /tmp/tox/prisma-client-py
	rm -rf `find . -name __pycache__`
	rm -rf `find examples -name '.venv' `
	rm -rf `find tests/integrations -name '.venv' `
	rm -rf .tests_cache
	rm -rf .mypy_cache
	rm -rf htmlcov
	rm -rf *.egg-info
	rm -f .coverage
	rm -f .coverage.*
	rm -rf build
	rm -rf dist
	rm -f coverage.xml
