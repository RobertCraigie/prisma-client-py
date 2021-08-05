.PHONY: bootstrap
bootstrap:
	pip install -U -e .[all]
	prisma db push --schema=tests/data/schema.prisma
	cp tests/data/dev.db dev.db
	pre-commit install

.PHONY: test
test:
	tox $(ARGS)

.PHONY: format
format:
	black .

.PHONY: lint
lint:
	tox -e lint

.PHONY: pyright
pyright:
	prisma generate --schema=tests/data/schema.prisma
	pyright

.PHONY: typesafety
typesafety:
	tox -e typesafety $(ARGS)

.PHONY: clean
clean:
	python tests/scripts/cleanup.py
	rm -rf /tmp/tox/prisma-client-py
	rm -rf `find . -name __pycache__`
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
