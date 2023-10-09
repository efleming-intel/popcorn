install:
	pip install .

venv:
	python3 -m venv .venv

build:
	python -m build

testcov:
	pytest --cov=src/popcorn tests/

clean:
	pip uninstall popcorn -y
	rm -f .coverage
	rm -rf build .pytest_cache popcorn.egg-info src/popcorn/__pycache__ .vscode

purge: clean
	rm -rf .venv
