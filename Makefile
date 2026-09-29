PIP_INSTALL = flyin/bin/pip install
PYTHON = flyin/bin/python3

MYPY_FLAGS = --warn-return-any --warn-unused-ignores \
		--ignore-missing-imports --disallow-untyped-defs \
		--check-untyped-defs

RM = rm -rf

install:
	python3.12 -m venv flyin
	$(PIP_INSTALL) --upgrade pip
	$(PIP_INSTALL) flake8
	$(PIP_INSTALL) mypy
	$(PIP_INSTALL) pygame

run:
	@$(PYTHON) main.py $(MAP)

debug:
	$(PYTHON) -m pdb main.py $(MAP)

clean:
	$(RM) src/__pycache__
	$(RM) .mypy_cache

lint:
	$(PYTHON) -m flake8 main.py
	$(PYTHON) -m flake8 src
	$(PYTHON) -m mypy $(MYPY_FLAGS) main.py
	$(PYTHON) -m mypy $(MYPY_FLAGS) src

lint-strict:
	$(PYTHON) -m flake8 main.py
	$(PYTHON) -m flake8 src
	$(PYTHON) -m mypy --strict main.py
	$(PYTHON) -m mypy --strict src

destroy: clean
	$(RM) flyin