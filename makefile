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
	python -m usort format $(PKG)
	python -m black $(PKG)

lint:
	python -m flake8 $(PKG)
	python -m usort check $(PKG)
	python -m black --check $(PKG)

test:
	python -m coverage run -m $(PKG).tests
	python -m coverage report
	python -m mypy $(PKG)

.PHONY: html
html: venv
	.venv/bin/sphinx-build -b html docs html

clean:
	rm -rf build dist html README MANIFEST *.egg-info

distclean: clean
	rm -rf .venv
