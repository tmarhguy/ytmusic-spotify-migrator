.PHONY: help install test lint format type-check clean dev setup

help: ## Show this help message
	@echo "YT2Spot Development Commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

setup: ## Set up development environment
	@chmod +x scripts/setup_dev.sh
	@scripts/setup_dev.sh

install: ## Install package in development mode
	pip install -e ".[dev]"

test: ## Run tests
	pytest tests/ -v --cov=yt2spot --cov-report=term-missing

test-fast: ## Run tests without coverage
	pytest tests/ -v

lint: ## Run linting
	ruff check .

lint-fix: ## Run linting with auto-fix
	ruff check --fix .

format: ## Format code with black
	black .

type-check: ## Run type checking
	mypy yt2spot

quality: lint type-check ## Run all quality checks

clean: ## Clean build artifacts
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

build: ## Build distribution packages
	python -m build

dev: ## Run development version
	python -m yt2spot.cli

# Sample data for testing
sample-data: ## Create sample input file for testing
	@echo "Creating sample input file..."
	@echo "Bohemian Rhapsody - Queen" > sample_likes.txt
	@echo "Hotel California - Eagles" >> sample_likes.txt
	@echo "Stairway to Heaven - Led Zeppelin" >> sample_likes.txt
	@echo "Sweet Child O' Mine - Guns N' Roses" >> sample_likes.txt
	@echo "Don't Stop Believin' - Journey" >> sample_likes.txt
	@echo "Sample input file created: sample_likes.txt"

# Docker commands
docker-build: ## Build Docker image
	docker build -t yt2spot .

docker-run: ## Run in Docker container
	docker run -it --rm -v $(PWD):/workspace yt2spot

# Release commands
version-patch: ## Bump patch version
	@python scripts/bump_version.py patch

version-minor: ## Bump minor version
	@python scripts/bump_version.py minor

version-major: ## Bump major version
	@python scripts/bump_version.py major
