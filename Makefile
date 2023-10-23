install:
	pip install .

venv:
	python3 -m venv .venv

test:
	pytest

testenv:
	pip install -e .[test]

testcov:
	pytest --cov=src/popcorn tests/

build:
	python -m build

clean:
	pip uninstall popcorn -y
	rm -f .coverage
	rm -rf build .hypothesis popcorn.egg-info popcorn/__pycache__ tests/__pycache__ tests/functional/__pycache__ tests/unit/__pycache__ .pytest_cache

purge: clean
	rm -rf .venv .vscode
