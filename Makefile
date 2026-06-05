PYTHON ?= python3

.PHONY: install test lint format run-local dashboard

install:
	$(PYTHON) -m pip install -r requirements.txt

test:
	$(PYTHON) -m pytest

lint:
	$(PYTHON) -m ruff check .

format:
	$(PYTHON) -m ruff format .

run-local:
	PYTHONPATH=src $(PYTHON) scripts/run_training_pipeline.py

dashboard:
	streamlit run dashboard/streamlit_app.py
