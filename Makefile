setup:
	pip install .

clean:
	pip uninstall popcorn -y
	rm -rf build src/popcorn.egg-info src/popcorn/__pycache__
