# Bitcoin CLI Wrapper - Makefile
# Automation for building, testing, and deployment

# =============================================================================
# CONFIGURATION
# =============================================================================

# Project configuration
PROJECT_NAME := bitcoin-CLI-RPC-weapper
VERSION := $(shell git describe --tags --always --dirty 2>/dev/null || echo "1.0.0")
BUILD_DATE := $(shell date -u +"%Y-%m-%dT%H:%M:%SZ")
VCS_REF := $(shell git rev-parse --short HEAD 2>/dev/null || echo "unknown")

# Docker configuration
DOCKER_IMAGE := $(PROJECT_NAME)
DOCKER_TAG := $(VERSION)
DOCKER_REGISTRY := # Set your registry here

# Python configuration
PYTHON := python3
PIP := pip3
VENV_DIR := venv
REQUIREMENTS := requirements.txt
DEV_REQUIREMENTS := requirements-dev.txt

# Test configuration
TEST_DIR := tests
COV_DIR := htmlcov
COV_REPORT := coverage.xml

# Documentation
DOCS_DIR := docs
DOCS_BUILD := $(DOCS_DIR)/_build

# =============================================================================
# HELP TARGET
# =============================================================================

.PHONY: help
help: ## Show this help message
	@echo "Bitcoin CLI Wrapper - Available Commands:"
	@echo ""
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo ""
	@echo "Environment Variables:"
	@echo "  DOCKER_REGISTRY  - Docker registry for pushing images"
	@echo "  BITCOIN_RPC_USER - Bitcoin RPC username for tests"
	@echo "  BITCOIN_RPC_PASS - Bitcoin RPC password for tests"

# =============================================================================
# DEVELOPMENT SETUP
# =============================================================================

.PHONY: setup
setup: ## Set up development environment
	@echo "Setting up development environment..."
	$(PYTHON) -m venv $(VENV_DIR)
	$(VENV_DIR)/bin/pip install --upgrade pip
	$(VENV_DIR)/bin/pip install -r $(REQUIREMENTS)
	$(VENV_DIR)/bin/pip install -r $(DEV_REQUIREMENTS)
	@echo "Development environment ready!"
	@echo "Activate with: source $(VENV_DIR)/bin/activate"

.PHONY: setup-pre-commit
setup-pre-commit: ## Set up pre-commit hooks
	$(VENV_DIR)/bin/pre-commit install
	$(VENV_DIR)/bin/pre-commit autoupdate

.PHONY: clean-setup
clean-setup: ## Clean development environment
	rm -rf $(VENV_DIR)
	rm -rf __pycache__
	rm -rf .pytest_cache
	rm -rf $(COV_DIR)
	rm -rf .coverage
	rm -rf $(COV_REPORT)

# =============================================================================
# CODE QUALITY
# =============================================================================

.PHONY: format
format: ## Format code with black and isort
	$(VENV_DIR)/bin/black bitcoin_cli_wrapper.py lib/ tests/
	$(VENV_DIR)/bin/isort bitcoin_cli_wrapper.py lib/ tests/

.PHONY: lint
lint: ## Run linting with flake8
	$(VENV_DIR)/bin/flake8 bitcoin_cli_wrapper.py lib/ tests/

.PHONY: type-check
type-check: ## Run type checking with mypy
	$(VENV_DIR)/bin/mypy bitcoin_cli_wrapper.py lib/

.PHONY: security-check
security-check: ## Run security checks
	$(VENV_DIR)/bin/safety check
	$(VENV_DIR)/bin/bandit -r lib/ bitcoin_cli_wrapper.py

.PHONY: check-all
check-all: format lint type-check security-check ## Run all code quality checks

# =============================================================================
# TESTING
# =============================================================================

.PHONY: test
test: ## Run unit tests
	$(VENV_DIR)/bin/pytest $(TEST_DIR) -v

.PHONY: test-cov
test-cov: ## Run tests with coverage
	$(VENV_DIR)/bin/pytest $(TEST_DIR) --cov=lib --cov-report=html --cov-report=xml --cov-report=term

.PHONY: test-integration
test-integration: ## Run integration tests (requires Bitcoin node)
	$(VENV_DIR)/bin/pytest $(TEST_DIR)/test_integration.py -v

.PHONY: test-all
test-all: test test-integration ## Run all tests

.PHONY: test-watch
test-watch: ## Run tests in watch mode
	$(VENV_DIR)/bin/pytest-watch $(TEST_DIR)

# =============================================================================
# DOCKER OPERATIONS
# =============================================================================

.PHONY: docker-build
docker-build: ## Build Docker image
	docker build \
		--build-arg BUILD_DATE=$(BUILD_DATE) \
		--build-arg VERSION=$(VERSION) \
		--build-arg VCS_REF=$(VCS_REF) \
		-t $(DOCKER_IMAGE):$(DOCKER_TAG) \
		-t $(DOCKER_IMAGE):latest \
		.

.PHONY: docker-build-dev
docker-build-dev: ## Build development Docker image
	docker build \
		--target development \
		--build-arg BUILD_DATE=$(BUILD_DATE) \
		--build-arg VERSION=$(VERSION) \
		--build-arg VCS_REF=$(VCS_REF) \
		-t $(DOCKER_IMAGE):dev \
		.

.PHONY: docker-test
docker-test: docker-build ## Test Docker image
	docker run --rm $(DOCKER_IMAGE):$(DOCKER_TAG) python3 -c "import lib.config; print('Import test passed')"

.PHONY: docker-push
docker-push: docker-build ## Push Docker image to registry
	@if [ -z "$(DOCKER_REGISTRY)" ]; then \
		echo "Error: DOCKER_REGISTRY not set"; \
		exit 1; \
	fi
	docker tag $(DOCKER_IMAGE):$(DOCKER_TAG) $(DOCKER_REGISTRY)/$(DOCKER_IMAGE):$(DOCKER_TAG)
	docker tag $(DOCKER_IMAGE):latest $(DOCKER_REGISTRY)/$(DOCKER_IMAGE):latest
	docker push $(DOCKER_REGISTRY)/$(DOCKER_IMAGE):$(DOCKER_TAG)
	docker push $(DOCKER_REGISTRY)/$(DOCKER_IMAGE):latest

.PHONY: docker-clean
docker-clean: ## Clean Docker images and containers
	docker system prune -f
	docker image prune -f

# =============================================================================
# DOCKER COMPOSE OPERATIONS
# =============================================================================

.PHONY: up
up: ## Start services with docker-compose
	docker-compose up -d

.PHONY: up-dev
up-dev: ## Start development services
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d

.PHONY: down
down: ## Stop services
	docker-compose down

.PHONY: down-dev
down-dev: ## Stop development services
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml down

.PHONY: logs
logs: ## Show service logs
	docker-compose logs -f

.PHONY: logs-wrapper
logs-wrapper: ## Show wrapper logs
	docker-compose logs -f bitcoin-wrapper

.PHONY: logs-bitcoin
logs-bitcoin: ## Show Bitcoin node logs
	docker-compose logs -f bitcoin-node

.PHONY: shell
shell: ## Access wrapper container shell
	docker-compose exec bitcoin-wrapper /bin/bash

.PHONY: shell-bitcoin
shell-bitcoin: ## Access Bitcoin node container shell
	docker-compose exec bitcoin-node /bin/bash

# =============================================================================
# BITCOIN OPERATIONS
# =============================================================================

.PHONY: bitcoin-info
bitcoin-info: ## Get Bitcoin node info
	docker-compose exec bitcoin-wrapper python3 bitcoin_cli_wrapper.py getblockchaininfo

.PHONY: bitcoin-generate
bitcoin-generate: ## Generate test blocks (regtest only)
	docker-compose exec bitcoin-node bitcoin-cli -regtest -rpcuser=$$BITCOIN_RPC_USER -rpcpassword=$$BITCOIN_RPC_PASSWORD generate 10

.PHONY: bitcoin-reset
bitcoin-reset: ## Reset Bitcoin regtest chain
	docker-compose down
	docker volume rm bitcoin-CLI-RPC-weapper_bitcoin_data || true
	docker-compose up -d bitcoin-node
	sleep 10
	$(MAKE) bitcoin-generate

# =============================================================================
# DOCUMENTATION
# =============================================================================

.PHONY: docs
docs: ## Build documentation
	cd $(DOCS_DIR) && $(VENV_DIR)/bin/sphinx-build -b html . $(DOCS_BUILD)

.PHONY: docs-serve
docs-serve: docs ## Serve documentation locally
	cd $(DOCS_BUILD) && $(PYTHON) -m http.server 8000

.PHONY: docs-clean
docs-clean: ## Clean documentation build
	rm -rf $(DOCS_BUILD)

# =============================================================================
# RELEASE OPERATIONS
# =============================================================================

.PHONY: version
version: ## Show current version
	@echo "Version: $(VERSION)"
	@echo "Build Date: $(BUILD_DATE)"
	@echo "VCS Ref: $(VCS_REF)"

.PHONY: tag-release
tag-release: ## Tag a new release (requires VERSION env var)
	@if [ -z "$(VERSION)" ]; then \
		echo "Error: VERSION not set"; \
		exit 1; \
	fi
	git tag -a v$(VERSION) -m "Release v$(VERSION)"
	git push origin v$(VERSION)

.PHONY: release
release: check-all test-all docker-build docker-push ## Full release process
	@echo "Release $(VERSION) completed successfully!"

# =============================================================================
# MONITORING AND HEALTH
# =============================================================================

.PHONY: health
health: ## Check service health
	docker-compose ps
	@echo ""
	@echo "Bitcoin Node Health:"
	@docker-compose exec bitcoin-node bitcoin-cli -rpcuser=$$BITCOIN_RPC_USER -rpcpassword=$$BITCOIN_RPC_PASSWORD getblockchaininfo | head -5 || echo "Bitcoin node not responding"
	@echo ""
	@echo "Wrapper Health:"
	@docker-compose exec bitcoin-wrapper python3 bitcoin_cli_wrapper.py getblockchaininfo | head -5 || echo "Wrapper not responding"

.PHONY: stats
stats: ## Show resource usage statistics
	docker stats --no-stream

.PHONY: backup
backup: ## Backup Bitcoin data and logs
	@mkdir -p backups/$(shell date +%Y%m%d_%H%M%S)
	docker run --rm -v bitcoin-CLI-RPC-weapper_bitcoin_data:/data -v $(PWD)/backups:/backup alpine tar czf /backup/$(shell date +%Y%m%d_%H%M%S)/bitcoin_data.tar.gz -C /data .
	cp -r logs backups/$(shell date +%Y%m%d_%H%M%S)/

# =============================================================================
# MAINTENANCE
# =============================================================================

.PHONY: update-deps
update-deps: ## Update Python dependencies
	$(VENV_DIR)/bin/pip-review --auto
	$(VENV_DIR)/bin/pip freeze > $(REQUIREMENTS)

.PHONY: security-audit
security-audit: ## Run security audit
	$(VENV_DIR)/bin/pip-audit
	docker scout cves $(DOCKER_IMAGE):$(DOCKER_TAG) || echo "Docker Scout not available"

.PHONY: clean
clean: ## Clean temporary files
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .pytest_cache
	rm -rf $(COV_DIR)
	rm -rf .coverage
	rm -rf $(COV_REPORT)
	rm -rf dist/
	rm -rf build/

.PHONY: clean-all
clean-all: clean docker-clean docs-clean ## Deep clean everything
	docker-compose down -v
	docker volume prune -f

# =============================================================================
# CI/CD HELPERS
# =============================================================================

.PHONY: ci-test
ci-test: ## CI test pipeline
	$(MAKE) setup
	$(MAKE) check-all
	$(MAKE) test-cov
	$(MAKE) docker-build
	$(MAKE) docker-test

.PHONY: ci-deploy
ci-deploy: ## CI deployment pipeline
	$(MAKE) docker-build
	$(MAKE) docker-push

# =============================================================================
# DEFAULT TARGET
# =============================================================================

.DEFAULT_GOAL := help
