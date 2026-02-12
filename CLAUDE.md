# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Bitcoin CLI Wrapper: A secure, enterprise-grade Bitcoin RPC client with CLI interface. Provides a Python wrapper around Bitcoin Core/Knots RPC API with comprehensive security, validation, and error handling.

## Development Commands

### Setup
```bash
# Initial setup - creates venv and installs all dependencies
make setup

# Activate virtual environment
source venv/bin/activate
```

### Running the CLI

**Recommended: Use the launcher script (handles venv automatically):**
```bash
./bitcoin-cli <command> [params]

# Examples
./bitcoin-cli getblockchaininfo
./bitcoin-cli getblock <hash>
./bitcoin-cli --verbose getblockcount
```

**Alternative: Manual method (requires venv activation):**
```bash
# Activate venv first
source venv/bin/activate

# Set PYTHONPATH
export PYTHONPATH=$PYTHONPATH:./bitcoin-CLI-RPC-wrapper

# Run commands
python3 src/main_wrapper.py <command> [params]
```

### Testing
```bash
# Unit tests only
make test

# Unit tests with coverage report
make test-cov

# Integration tests (requires running Bitcoin node)
make test-integration

# All tests
make test-all

# Run a single test file
venv/bin/pytest tests/test_rpc_client.py -v

# Run a specific test
venv/bin/pytest tests/test_rpc_client.py::TestBitcoinRPCClient::test_successful_rpc_call -v
```

### Code Quality
```bash
# Format code (black + isort)
make format

# Lint (flake8)
make lint

# Type check (mypy)
make type-check

# Security scan (safety + bandit)
make security-check

# Run all quality checks
make check-all
```

### Docker
```bash
# Start production services
make up

# Start development services (includes Bitcoin regtest node, monitoring, etc)
make up-dev

# Stop services
make down

# View logs
make logs-wrapper    # Wrapper logs only
make logs-bitcoin    # Bitcoin node logs only
make logs           # All logs

# Access container shell
make shell          # Wrapper container
make shell-bitcoin  # Bitcoin node container
```

## Architecture

### Command Dispatch Pattern

Commands are routed through a two-level dispatch system in [src/main_wrapper.py](src/main_wrapper.py):

1. **COMMAND_MAP**: Maps CLI command names to (module_name, method_name) tuples
2. **COMMAND_MODULES**: Maps module names to command handler classes

To add a new command:
1. Add method to appropriate command class in [src/commands/](src/commands/) (blockchain.py, wallet.py, or network.py)
2. Add mapping entry to COMMAND_MAP in main_wrapper.py
3. Add appropriate validation in the command method using validators from [src/commands/validators.py](src/commands/validators.py)

### Configuration Priority Order

Configuration is loaded with the following priority (highest to lowest) in [src/config.py](src/config.py):

1. **Environment variables** (highest priority)
2. **Docker secrets** (from `/run/secrets/`)
3. **.env file** (lowest priority)
4. **Default values** (fallback)

When debugging configuration issues, check sources in this order. Credentials (RPC_USER, RPC_PASSWORD) are handled specially through `_get_secret()` method.

### Validation Architecture

All input validation happens in [src/commands/validators.py](src/commands/validators.py) with three validator classes:

- **ConfigValidator**: Validates configuration values (host, port, timeout)
- **InputValidator**: Validates user inputs (block hashes, addresses, transaction IDs)
- **CryptoValidator**: Cryptographic operations and certificate validation

RPC parameters are validated in [src/rpc_client.py](src/rpc_client.py) via `InputValidator.validate_json_rpc_params()` before any RPC call is made.

### Error Handling Philosophy

**Critical Design Principle**: Preserve original Bitcoin Core errors for transparency.

When Bitcoin Core returns an error, the wrapper adds context but preserves the original error message and code. See [src/rpc_client.py](src/rpc_client.py) `_handle_response()` and [src/main_wrapper.py](src/main_wrapper.py) `execute_command()`.

Error responses always include:
- `success`: false
- `error`: Original error message from Bitcoin Core
- `error_code`: Error code (RPC_ERROR, UNKNOWN_COMMAND, etc.)
- `command`: The command that was attempted
- `params`: The parameters that were passed

### Module Organization

```
src/
├── main_wrapper.py        # CLI entry point, command routing
├── rpc_client.py          # Core RPC client with retry logic and session management
├── config.py              # Hybrid configuration loader (env/secrets/.env)
└── commands/
    ├── validators.py      # All input validation logic
    ├── blockchain.py      # Blockchain RPC commands (getblock, getblockchaininfo, etc.)
    ├── wallet.py          # Wallet RPC commands (getbalance, getnewaddress, etc.)
    └── network.py         # Network RPC commands (getpeerinfo, getnetworkinfo, etc.)
```

Command handler classes receive an RPC client instance and delegate to it with validated parameters.

### RPC Client Features

[src/rpc_client.py](src/rpc_client.py) implements:

- **Connection pooling** via requests.Session with HTTPAdapter
- **Retry strategy** for transient failures (3 retries, exponential backoff)
- **SSL/TLS support** with certificate validation
- **Timeout handling** (configurable, default 30s)
- **Context manager** support for automatic cleanup

The client uses persistent sessions for performance. Always use as context manager or call `.close()` explicitly in tests.

## Testing Patterns

### Mock Configuration

Tests use `MockConfig` class (see [tests/test_rpc_client.py](tests/test_rpc_client.py)) instead of real Config objects to avoid file I/O and Docker secret lookups.

### Mocking RPC Calls

Use `@patch('requests.Session.post')` to mock RPC responses. Structure:
```python
mock_response = Mock()
mock_response.status_code = 200
mock_response.raise_for_status.return_value = None
mock_response.json.return_value = {
    "jsonrpc": "2.0",
    "id": 1,
    "result": {...}
}
mock_post.return_value = mock_response
```

### Path Handling in Tests

Tests add lib directory to path: `sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'lib'))`

This is necessary because of the module structure. Keep this pattern when adding new test files.

## Important Patterns

### Python Version
Requires Python 3.11+. Uses modern type hints (`from typing import Any, Dict, List, Optional, Union`).

### Logging
All modules use standard library logging:
```python
self.logger = logging.getLogger(__name__)
self.logger.debug("message")
self.logger.info("message")
self.logger.error("message")
```

Log level is configured via `LOG_LEVEL` environment variable or .env file.

### Network-Specific Defaults
Default ports vary by network (see config.py):
- mainnet: 8332
- testnet: 18332
- regtest: 18443

## Common Development Tasks

### Adding a New Blockchain Command

1. Add method to BlockchainCommands class in [src/commands/blockchain.py](src/commands/blockchain.py)
2. Add validation for parameters using validators
3. Add entry to COMMAND_MAP in [src/main_wrapper.py](src/main_wrapper.py)
4. Write unit tests in [tests/test_commands.py](tests/test_commands.py) (if exists) or [tests/test_integration.py](tests/test_integration.py)

### Debugging RPC Connection Issues

1. Check configuration priority: env vars > docker secrets > .env
2. Verify Bitcoin node is running and accessible
3. Enable verbose logging: `python3 src/main_wrapper.py --verbose <command>`
4. Check Docker logs: `make logs-bitcoin`
5. Test direct RPC access: `curl -u user:pass http://localhost:8332 -d '{"method":"getblockchaininfo"}'`

### Running with Docker Development Environment

`make up-dev` starts full development stack:
- Bitcoin node in regtest mode
- Wrapper with hot reload
- PostgreSQL (for testing)
- Redis (for caching)
- Grafana + Prometheus (monitoring)
- Nginx proxy

This is useful for integration testing and development.
