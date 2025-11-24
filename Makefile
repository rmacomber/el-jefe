# Makefile for AI Orchestrator SDK

.PHONY: help install test clean lint format examples docs

# Default target
help:
	@echo "AI Orchestrator SDK - Available Commands:"
	@echo ""
	@echo "  install       Install all dependencies"
	@echo "  install-dev   Install development dependencies"
	@echo "  test          Run the test suite"
	@echo "  test-cov      Run tests with coverage"
	@echo "  lint          Run linting checks"
	@echo "  format        Format code with black"
	@echo "  clean         Clean up temporary files"
	@echo "  examples      Run example scripts"
	@echo "  docs          Generate documentation"
	@echo "  run           Run the orchestrator CLI"
	@echo "  el-jefe-test   Test el-jefe command"
	@echo "  test-el-jefe   Test el-jefe with example task"
	@echo "  install-global Install CLI tools globally"
	@echo ""

# Installation
install:
	@echo "Installing dependencies..."
	pip install -r requirements.txt
	@echo "✅ Installation complete"

install-dev:
	@echo "Installing development dependencies..."
	pip install -r requirements.txt
	pip install -e ".[dev]"
	@echo "✅ Development installation complete"

# Testing
test:
	@echo "Running tests..."
	python -m pytest tests/ -v

test-cov:
	@echo "Running tests with coverage..."
	python -m pytest tests/ --cov=src --cov-report=html --cov-report=term

# Code quality
lint:
	@echo "Running linting checks..."
	flake8 src/ examples/
	mypy src/
	@echo "✅ Linting complete"

format:
	@echo "Formatting code..."
	black src/ examples/ tests/
	@echo "✅ Code formatted"

# Cleanup
clean:
	@echo "Cleaning up..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf build/ dist/ .coverage htmlcov/ .pytest_cache/
	@echo "✅ Cleanup complete"

# Examples
examples:
	@echo "Running example: Podcast Research"
	python examples/podcast_research.py

examples-data:
	@echo "Running example: Data Analysis"
	python examples/data_analysis.py

# Documentation
docs:
	@echo "Generating documentation..."
	@if command -v mkdocs >/dev/null 2>&1; then \
		mkdocs build; \
		echo "✅ Documentation built in site/"; \
	else \
		echo "❌ mkdocs not installed. Install with: pip install mkdocs mkdocs-material"; \
	fi

docs-serve:
	@echo "Starting documentation server..."
	@if command -v mkdocs >/dev/null 2>&1; then \
		mkdocs serve; \
	else \
		echo "❌ mkdocs not installed. Install with: pip install mkdocs mkdocs-material"; \
	fi

# Running the application
run:
	@echo "Starting AI Orchestrator CLI..."
	python main.py --help

run-goal:
	@read -p "Enter your goal: " goal; \
	python main.py "$$goal"

# CLI commands
el-jefe-test:
	@echo "Testing el-jefe command..."
	./el-jefe --help

test-el-jefe:
	@echo "Testing el-jefe with example task..."
	./el-jefe --non-interactive "Write a brief summary of AI orchestration"

install-global:
	@echo "Installing el-jefe CLI tool..."
	./install-local.sh

# Development helpers
dev-setup: install-dev
	@echo "Setting up development environment..."
	pre-commit install
	@echo "✅ Development setup complete"

check: lint test
	@echo "✅ All checks passed"

# Build distribution
build: clean
	@echo "Building distribution..."
	python setup.py sdist bdist_wheel
	@echo "✅ Build complete"

# Install in development mode
dev-install:
	@echo "Installing in development mode..."
	pip install -e .
	@echo "✅ Development install complete"