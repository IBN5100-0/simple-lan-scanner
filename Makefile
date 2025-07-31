# Simple LAN Scanner Makefile

.PHONY: help install install-dev test test-cov clean lint

help:  ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install:  ## Install the package
	pip install -e .[cli]

install-dev:  ## Install development dependencies
	pip install -e .[cli,test]

test:  ## Run tests
	python -m pytest tests/ -v

test-cov:  ## Run tests with coverage report
	python -m pytest tests/ --cov=simple_scanner --cov-report=term-missing --cov-report=html

clean:  ## Clean up generated files
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

lint:  ## Run code quality checks (if you have linting tools installed)
	@echo "Install linting tools with: pip install black flake8 isort mypy"
	@echo "Then run: black src/ tests/ && flake8 src/ tests/ && isort src/ tests/ && mypy src/"

scan:  ## Run a quick scan
	lan-scan scan --verbose

gui:  ## Launch the GUI
	lan-scan gui