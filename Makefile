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

.PHONY: test
test:
	nox -s test $(ARGS)

.PHONY: format
format:
	blue .
	for schema in `find . -name '*.schema.prisma'` ; do \
        prisma format --schema=$$schema ; \
    done

.PHONY: lint
lint:
	nox -s lint

.PHONY: mypy
mypy:
	nox -s mypy

.PHONY: pyright
pyright:
	prisma generate --schema=tests/data/schema.prisma
	pyright

.PHONY: typesafety
typesafety:
	nox -s typesafety-pyright typesafety-mypy

.PHONY: docs
docs:
	python scripts/docs.py
	mkdocs build

.PHONY: docs-serve
docs-serve:
	python scripts/docs.py
	mkdocs serve

.PHONY: docker
docker:
	docker build -t prisma-client-py --load .

.PHONY: clean
clean:
	python -m prisma_cleanup
	pip cache remove prisma
	rm -rf .nox
	rm -rf .cache
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
