# Bitcoin CLI Wrapper - Project Structure

This document outlines the complete project structure and explains the purpose of each component.

## 📁 Project Overview

```
bitcoin-CLI-RPC-weapper/
├── 📄 bitcoin_cli_wrapper.py          # Main CLI entry point
├── 📁 src/                            # Core library modules
│   ├── 📄 config.py                   # Configuration management
│   ├── 📄 rpc_client.py               # Bitcoin RPC client
│   ├── 📄 validators.py               # Input validation & crypto
│   └── 📁 commands/                   # Command modules
│       ├── 📄 blockchain.py           # Blockchain commands
│       ├── 📄 wallet.py               # Wallet commands
│       └── 📄 network.py              # Network commands
├── 📁 tests/                          # Test suite
│   ├── 📄 test_config.py              # Configuration tests
│   ├── 📄 test_rpc_client.py          # RPC client tests
│   ├── 📄 test_integration.py         # Integration tests
│   ├── 📄 test_validators.py          # Validator tests
│   ├── 📄 test_commands.py            # Command tests
│   └── 📄 conftest.py                 # Test configuration
├── 📁 config/                         # Configuration files
│   ├── 📄 bitcoin.conf                # Bitcoin node config
│   ├── 📄 bitcoin-dev.conf            # Development config
│   ├── 📄 nginx.conf                  # Nginx configuration
│   ├── 📄 nginx-dev.conf              # Nginx dev config
│   └── 📄 fluent-bit.conf             # Log aggregation
├── 📁 certs/                          # SSL certificates
│   ├── 📄 localhost.pem               # Development certificate
│   ├── 📄 localhost-key.pem           # Development private key
│   └── 📄 production.pem              # Production certificate
├── 📁 secrets/                        # Docker secrets
│   ├── 📄 bitcoin_rpc_user.txt        # RPC username secret
│   └── 📄 bitcoin_rpc_password.txt    # RPC password secret
├── 📁 scripts/                        # Utility scripts
│   ├── 📄 setup-dev.sh                # Development setup
│   ├── 📄 generate-certs.sh           # SSL certificate generation
│   ├── 📄 backup.sh                   # Backup script
│   └── 📄 health-check.sh             # Health check script
├── 📁 docs/                           # Documentation
│   ├── 📄 index.rst                   # Main documentation
│   ├── 📄 api.rst                     # API reference
│   ├── 📄 deployment.rst              # Deployment guide
│   └── 📄 conf.py                     # Sphinx configuration
├── 📁 logs/                           # Application logs
│   ├── 📁 wrapper/                    # Wrapper logs
│   ├── 📁 bitcoin/                    # Bitcoin node logs
│   ├── 📁 nginx/                      # Nginx logs
│   └── 📁 dev/                        # Development logs
├── 📁 data/                           # Data directories
│   └── 📁 bitcoin/                    # Bitcoin blockchain data
├── 📄 .env                            # Environment configuration
├── 📄 .env.example                    # Configuration template
├── 📄 .env.test                       # Test configuration
├── 📄 requirements.txt                # Python dependencies
├── 📄 requirements-dev.txt            # Development dependencies
├── 📄 Dockerfile                      # Container definition
├── 📄 docker-compose.yml              # Production containers
├── 📄 docker-compose.dev.yml          # Development containers
├── 📄 Makefile                        # Build automation
├── 📄 README.md                       # Project documentation
├── 📄 CHANGELOG.md                    # Version history
├── 📄 LICENSE                         # License file
├── 📄 .gitignore                      # Git ignore rules
├── 📄 .dockerignore                   # Docker ignore rules
├── 📄 .pre-commit-config.yaml         # Pre-commit hooks
└── 📄 pyproject.toml                  # Python project config
```

## 🔧 Core Components

### Main Application (`bitcoin_cli_wrapper.py`)
- **Purpose**: CLI entry point and command router
- **Features**: Argument parsing, command execution, error handling
- **Dependencies**: All lib modules, argparse, logging

### Configuration Management (`lib/config.py`)
- **Purpose**: Hybrid configuration loading and validation
- **Features**: .env files, environment variables, Docker secrets
- **Security**: Credential validation, SSL configuration

### RPC Client (`lib/rpc_client.py`)
- **Purpose**: Secure Bitcoin RPC communication
- **Features**: SSL/TLS, connection pooling, retry logic, error handling
- **Security**: Request validation, timeout handling, session management

### Validators (`lib/validators.py`)
- **Purpose**: Input validation and cryptographic utilities
- **Features**: Bitcoin address validation, hash functions, parameter sanitization
- **Security**: Prevents injection attacks, validates all inputs

### Command Modules (`lib/commands/`)
- **blockchain.py**: Block and chain operations
- **wallet.py**: Wallet management and transactions
- **network.py**: Network and peer management

## 🧪 Testing Structure

### Test Categories
1. **Unit Tests**: Individual component testing
2. **Integration Tests**: End-to-end functionality with real Bitcoin node
3. **Docker Tests**: Container and orchestration validation

### Test Files
- `test_config.py`: Configuration loading and validation
- `test_rpc_client.py`: RPC client functionality
- `test_integration.py`: Full system integration
- `test_validators.py`: Input validation
- `test_commands.py`: Command module testing

## 🐳 Container Architecture

### Multi-Stage Dockerfile
1. **Builder Stage**: Dependency installation and compilation
2. **Production Stage**: Minimal runtime environment
3. **Development Stage**: Enhanced with development tools

### Docker Compose Services
- **bitcoin-node**: Bitcoin Knots/Core container
- **bitcoin-wrapper**: Python application container
- **nginx-proxy**: SSL termination and reverse proxy
- **log-aggregator**: Centralized logging (optional)

### Development Services
- **test-db**: PostgreSQL for testing
- **redis-dev**: Caching layer
- **grafana-dev**: Metrics visualization
- **prometheus-dev**: Metrics collection
- **docs**: Documentation server

## 📁 Directory Purposes

### `/config`
- **Purpose**: Configuration templates and service configs
- **Contents**: Bitcoin node, Nginx, monitoring configurations
- **Security**: Read-only mounts, template-based generation

### `/certs`
- **Purpose**: SSL/TLS certificates and keys
- **Security**: Proper permissions (600/700), encrypted storage
- **Types**: Development self-signed, production CA-signed

### `/secrets`
- **Purpose**: Docker secrets for production
- **Security**: File-based secrets, proper permissions
- **Usage**: Alternative to environment variables

### `/scripts`
- **Purpose**: Automation and utility scripts
- **Contents**: Setup, backup, health checks, certificate generation
- **Usage**: Development and operations automation

### `/logs`
- **Purpose**: Application and service logs
- **Structure**: Organized by service and environment
- **Rotation**: Configured log rotation and retention

### `/data`
- **Purpose**: Persistent data storage
- **Contents**: Bitcoin blockchain data, application state
- **Backup**: Regular backup procedures

## 🔐 Security Architecture

### Credential Management
1. **Development**: .env files with validation
2. **Production**: Docker secrets with file-based storage
3. **Fallback**: Environment variables for compatibility

### Network Security
- **Internal Networks**: Container isolation
- **SSL/TLS**: Encrypted communication
- **Reverse Proxy**: SSL termination and routing
- **Firewall**: Port restrictions and access control

### Input Validation
- **Parameter Sanitization**: All RPC parameters validated
- **Type Checking**: Strong typing with validation
- **Injection Prevention**: SQL and command injection protection
- **Rate Limiting**: Request throttling and timeout handling

## 📊 Monitoring and Observability

### Logging Strategy
- **Structured Logging**: JSON format for machine parsing
- **Log Levels**: Configurable verbosity
- **Centralization**: Optional log aggregation
- **Retention**: Configurable retention policies

### Health Checks
- **Application**: Python application health
- **Bitcoin Node**: RPC connectivity validation
- **Dependencies**: Database and cache health
- **Custom**: Business logic validation

### Metrics Collection
- **System Metrics**: CPU, memory, disk usage
- **Application Metrics**: Request rates, error rates
- **Business Metrics**: Bitcoin node status, RPC performance
- **Custom Dashboards**: Grafana visualization

## 🚀 Deployment Patterns

### Local Development
```bash
# Quick start
make setup
make up-dev
```

### Production Deployment
```bash
# Full production stack
docker-compose --profile ssl --profile monitoring up -d
```

### CI/CD Integration
```bash
# Automated testing
make ci-test

# Automated deployment
make ci-deploy
```

## 📈 Scaling Considerations

### Horizontal Scaling
- **Load Balancing**: Multiple wrapper instances
- **Session Affinity**: Stateless design
- **Database Scaling**: Read replicas for monitoring data

### Vertical Scaling
- **Resource Limits**: Container resource management
- **Performance Tuning**: Connection pooling, caching
- **Optimization**: Database query optimization

### High Availability
- **Redundancy**: Multiple Bitcoin nodes
- **Failover**: Automatic failover mechanisms
- **Backup**: Regular data backups and recovery procedures

## 🔄 Development Workflow

### Code Changes
1. Local development with hot reload
2. Unit testing with pytest
3. Integration testing with regtest
4. Code quality checks (lint, format, type)
5. Security scanning
6. Documentation updates

### Release Process
1. Version tagging and changelog
2. Docker image building and testing
3. Security scanning and vulnerability assessment
4. Deployment to staging environment
5. Production deployment with monitoring

### Maintenance
- Regular dependency updates
- Security patch management
- Performance monitoring and optimization
- Backup validation and recovery testing

This structure provides a solid foundation for enterprise-grade Bitcoin operations with comprehensive security, testing, and deployment capabilities.
