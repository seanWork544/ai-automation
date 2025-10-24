.PHONY: install dev seed server web test

install:
	pip install -r server/requirements.txt
	npm --prefix web install

dev:
	python scripts/dev.py

seed:
	PYTHONPATH=server python -m app.seed

server:
	PYTHONPATH=server uvicorn app.main:app --reload

web:
	npm --prefix web run dev

test:
	PYTHONPATH=server pytest server/tests
