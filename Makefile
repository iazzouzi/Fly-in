.DEFAULT_GOAL := run

install:
	@python3 -m pip install -r requirements.txt

run:
	@python3 main.py maps/challenger/01_the_impossible_dream.txt || true

debug:
	@python3 -m pdb main.py maps/challenger/01_the_impossible_dream.txt || true

clean:
	@find . -type d -name "__pycache__" -exec rm -r {} +
	@find . -type d -name ".mypy_cache" -exec rm -r {} +
	@find . -type d -name ".pytest_cache" -exec rm -r {} +
	@find . -type f -name "*.pyc" -delete

lint:
	@python3 -m flake8 .
	@python3 -m mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	@python3 -m flake8 .
	@python3 -m mypy . --strict

.PHONY: install run debug clean lint lint-strict