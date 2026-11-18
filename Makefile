# Preferable for Linux and MacOS
# Windows Configuration: https://www.tilburgsciencehub.com/topics/automation/automation-tools/makefiles/make/#installation

all: run

.PHONY: run
run:
	streamlit run app.py

.PHONY:
fmt:
	ruff format --line-length=120 --no-cache src/**/*.py

.PHONY: lint
lint:
	ruff check src/**/*.py

.PHONY: lint-fix
lint-fix:
	ruff check --fix src/**/*.py --unsafe-fixes

.PHONY: clean
clean:
	-rm -rf .venv
