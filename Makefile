.PHONY: style quality test test-cov

check_dirs := rexearch/ tests/
test_dirs := rexearch/

style:
	black $(check_dirs)
	isort $(check_dirs)
	flake8 $(check_dirs)

quality:
	black --check $(check_dirs)
	isort --check-only $(check_dirs)
	flake8 $(check_dirs)

test:
	python -m pytest

test-cov:
	python -m pytest --cov-branch --cov $(test_dirs)
