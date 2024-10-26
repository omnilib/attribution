PKG:=attribution
EXTRAS:=dev,docs

ifeq ($(OS),Windows_NT)
    ACTIVATE:=.venv/Scripts/activate
else
    ACTIVATE:=.venv/bin/activate
endif

UV:=$(shell uv --version)
ifdef UV
	VENV:=uv venv
	PIP:=uv pip
else
	VENV:=python -m venv
	PIP:=python -m pip
endif

.venv:
	$(VENV) .venv

venv: .venv
	source $(ACTIVATE) && make install
	echo 'run `source $(ACTIVATE)` to use virtualenv'

install:
	$(PIP) install -Ue .[$(EXTRAS)]

format:
	python -m ufmt format $(PKG)

lint:
	python -m flake8 $(PKG)
	python -m ufmt check $(PKG)

test:
	python -m coverage run -m $(PKG).tests
	python -m coverage report
	python -m mypy $(PKG)

.PHONY: html
html:
	.venv/bin/sphinx-build -ab html docs html

clean:
	rm -rf build dist html README MANIFEST *.egg-info

distclean: clean
	rm -rf .venv
