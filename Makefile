# Preferable for Linux and MacOS
# Windows Configuration: https://www.tilburgsciencehub.com/topics/automation/automation-tools/makefiles/make/#installation

all: run

.PHONY: run
run:
	streamlit run app.py

.PHONY:
fmt-check:
	ruff format --line-length=120 --no-cache --check

.PHONY:
fmt:
	ruff format --line-length=120 --no-cache

.PHONY: lint
lint-check:
	ruff check

.PHONY: lint-fix
lint:
	ruff check --fix --unsafe-fixes

.PHONY: clean
clean:
	-rm -rf .venv
