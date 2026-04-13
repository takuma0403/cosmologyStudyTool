VENV_DIR := .venv
PYTHON := $(VENV_DIR)/bin/python
PIP := $(VENV_DIR)/bin/pip

$(VENV_DIR):
	@echo "Venv not found. Setting up..."
	$(MAKE) setup

freeze:
	$(PIP) freeze > requirements.txt

setup:
	python3 -m venv $(VENV_DIR)
	$(PIP) install -r requirements.txt
	$(PIP) install -e .

run: $(VENV_DIR)
	$(PYTHON) $(word 2, $(MAKECMDGOALS))

%:
	@: