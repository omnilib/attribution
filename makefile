venv:
	python -m venv .venv
	source .venv/bin/activate && make setup dev
	echo 'run `source .venv/bin/activate` to use virtualenv'

build:
	python -m flit build

dev:
	python -m flit install --symlink

setup:
	python -m pip install -Ur requirements-dev.txt
	python -m pip install -Ur requirements.txt

release: lint test clean
	python -m flit publish

format:
	python -m usort format attribution
	python -m black attribution

lint:
	python -m pylint --rcfile .pylint attribution
	python -m usort check attribution
	python -m black --check attribution

test:
	python -m coverage run -m attribution.tests
	python -m coverage report
	python -m mypy attribution

.PHONY: html
html:
	sphinx-build -b html docs html

clean:
	rm -rf build dist html README MANIFEST *.egg-info

distclean: clean
	rm -rf .venv