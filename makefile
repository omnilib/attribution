venv:
	python -m venv .venv
	source .venv/bin/activate && make setup dev
	echo 'run `source .venv/bin/activate` to use virtualenv'

build:
	python setup.py build

dev:
	python setup.py develop

setup:
	python -m pip install -Ur requirements-dev.txt
	python -m pip install -Ur requirements.txt

release: lint test clean
	python setup.py sdist bdist_wheel
	python -m twine upload dist/*

format:
	python -m isort --apply --recursive attribution setup.py
	python -m black attribution setup.py

lint:
	python -m pylint --rcfile .pylint attribution setup.py
	python -m isort --diff --recursive attribution setup.py
	python -m black --check attribution setup.py

test:
	python -m coverage run -m attribution.tests
	python -m coverage report
	python -m mypy attribution

.PHONY: html
html:
	sphinx-build -b html docs html

clean:
	rm -rf build dist html README MANIFEST *.egg-info
