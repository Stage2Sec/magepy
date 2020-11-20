
.PHONY: clean dist pypi coverage test

clean:
	rm -rf dist *.egg-info build

dist: clean
	python3 setup.py sdist bdist_wheel

pypi: dist
	python3 -m twine upload --repository pypi dist/*

coverage:
	coverage run --source . test_runner.py
	coverage html

test:
	python test_runner.py
