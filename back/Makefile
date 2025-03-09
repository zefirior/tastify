BIN ?= .venv/bin
CODE = .

init:
	python3.11 -m venv .venv
	$(BIN)/pip install --upgrade pip
	$(BIN)/pip install -r requirements.txt
	$(BIN)/pip install -r requirements-test.txt

pretty:
	$(BIN)/isort $(CODE)
	$(BIN)/black --target-version py312 --skip-string-normalization --line-length=119 $(CODE)
	$(BIN)/unify --in-place --recursive $(CODE)

run-db:
	docker-compose --file ../docker/local.docker-compose.yaml up -d db

test-data: run-db
	PYTHONPATH=.. $(BIN)/python3 db/base.py

run-app:
	PYTHONPATH=.. $(BIN)/litestar --app entrypoint:app run

test:
	PYTHONPATH=back $(BIN)/pytest -v
