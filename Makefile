
.PHONY: clean dist pypi

clean:
	rm -rf dist *.egg-info build

dist: clean
	python3 setup.py sdist bdist_wheel

pypi: dist
	python3 -m twine upload --repository pypi dist/*
