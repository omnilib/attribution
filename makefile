PKG:=attribution

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
	python -m ufmt format $(PKG)

lint:
	python -m flake8 $(PKG)
	python -m ufmt check $(PKG)

test:
	python -m coverage run -m $(PKG).tests
	python -m coverage report
	python -m mypy $(PKG)

deps:
	python -m pessimist --requirements= -c "python -m attribution.tests" .


.PHONY: html
html:
	.venv/bin/sphinx-build -ab html docs html

clean:
	rm -rf build dist html README MANIFEST *.egg-info

distclean: clean
	rm -rf .venv
