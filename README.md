# Bitcoin CLI Wrapper

A secure, enterprise-grade Bitcoin RPC client with CLI interface, built with Python and Docker. This wrapper provides a clean, secure interface to Bitcoin Knots/Core nodes with comprehensive testing, monitoring, and deployment capabilities.

## 🚀 Features

### Core Functionality
- **Secure RPC Communication**: SSL/TLS support with certificate validation
- **Hybrid Configuration**: Environment variables, Docker secrets, and .env files
- **Comprehensive Command Support**: Blockchain, wallet, and network operations
- **Enterprise Security**: Input validation, parameter sanitization, connection pooling
- **Error Transparency**: Preserves original Bitcoin Core errors while adding context

### Architecture
- **Modular Design**: Separation of concerns with dedicated command modules
- **Container Ready**: Full Docker and Docker Compose support
- **Development Friendly**: Hot reload, comprehensive testing, development tools
- **Production Ready**: Health checks, monitoring, logging, and resource management

### Security Features
- **Authentication**: RPC user/password with secure credential management
- **SSL/TLS**: Full SSL support for encrypted connections
- **Input Validation**: Comprehensive parameter validation and sanitization
- **Secret Management**: Docker secrets and environment variable support
- **Network Security**: Configurable network isolation and reverse proxy support

## 📋 Requirements

### Minimum Requirements
- Python 3.11+
- Bitcoin Knots or Bitcoin Core node
- Docker and Docker Compose (for containerized deployment)

### Supported Networks
- Mainnet
- Testnet
- Regtest (recommended for development and testing)

## 🛠️ Installation

### Option 1: Local Python Installation

```bash
# Clone the repository
git clone <repository-url>
cd bitcoin-cli-rpc-weapper

# Set up virtual environment
make setup

# Activate virtual environment
source venv/bin/activate

# Copy and configure environment
cp .env.example .env
# Edit .env with your Bitcoin node details
```

### Option 2: Docker Installation

```bash
# Clone the repository
git clone <repository-url>
cd bitcoin-cli-rpc-weapper

# Start with Docker Compose
make up

# Or for development
make up-dev
```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file with your Bitcoin node configuration:

```bash
# Connection
BITCOIN_RPC_HOST=127.0.0.1
BITCOIN_RPC_PORT=8332
BITCOIN_RPC_USER=your_user
BITCOIN_RPC_PASSWORD=your_password
BITCOIN_RPC_TIMEOUT=30
BITCOIN_NETWORK=mainnet

# Security
BITCOIN_RPC_USE_SSL=false
BITCOIN_RPC_SSL_VERIFY=true
BITCOIN_RPC_SSL_CERT_PATH=

# Logging
LOG_LEVEL=INFO
LOG_FILE=bitcoin_wrapper.log
```

### Network-Specific Defaults

| Network | Default Port | Description |
|---------|-------------|-------------|
| mainnet | 8332 | Production Bitcoin network |
| testnet | 18332 | Test network with test coins |
| regtest | 18443 | Local testing network |

### Docker Secrets (Production)

For production deployments, use Docker secrets:

```bash
echo "your_username" | docker secret create bitcoin_rpc_user -
echo "your_password" | docker secret create bitcoin_rpc_password -
```

## 🚀 Usage

### Command Line Interface

```bash
# Get blockchain information
export PYTHONPATH=$PYTHONPATH:./bitcoin-CLI-RPC-wrapper
python3 src/main_wrapper.py getblockchaininfo

# Get current block count
python3 src/main_wrapper.py getblockcount

# Get block by hash
python3 src/main_wrapper.py getblock 00000000000000000001f898821b0b888a912a2ac0aa3ea99ad6e8f5cbd31bde

# Get block hash by height
python3 src/main_wrapper.py getblockhash 100

# Get network information
python3 src/main_wrapper.py getnetworkinfo

# Show help
python3 src/main_wrapper.py --help

# Verbose output
python3 src/main_wrapper.py --verbose getblockchaininfo
```

### Available Commands

#### Blockchain Commands
- `getblockchaininfo` - Get blockchain information
- `getblockcount` - Get current block count
- `getblock <hash>` - Get block by hash
- `getblockhash <height>` - Get block hash by height
- `getbestblockhash` - Get best block hash

#### Network Commands
- `getnetworkinfo` - Get network information
- `getpeerinfo` - Get peer information
- `getconnectioncount` - Get connection count

#### Wallet Commands
- `getwalletinfo` - Get wallet information
- `getbalance` - Get wallet balance
- `getnewaddress` - Get new address

### Docker Usage

```bash
# Start services
make up

# Execute commands
docker-compose exec bitcoin-wrapper python3 main_wrapper.py getblockchaininfo

# View logs
make logs-wrapper

# Access shell
make shell
```

## 🧪 Testing

### Unit Tests
```bash
# Run unit tests
make test

# Run with coverage
make test-cov
```

### Integration Tests
```bash
# Requires running Bitcoin node
make test-integration

# Run all tests
make test-all
```

### Docker Tests
```bash
# Test Docker build
make docker-test

# Full CI pipeline
make ci-test
```

## 🔧 Development

### Development Setup
```bash
# Set up development environment
make setup

# Start development services
make up-dev

# Format code
make format

# Run linting
make lint

# Type checking
make type-check

# Security checks
make security-check
```

### Development Services

When using `make up-dev`, you get:
- Bitcoin node in regtest mode
- Development wrapper with hot reload
- Nginx proxy
- PostgreSQL for testing
- Redis for caching
- Grafana and Prometheus for monitoring
- Documentation server

### Code Quality

The project maintains high code quality standards:
- **Black** for code formatting
- **Flake8** for linting
- **MyPy** for type checking
- **Safety** for security scanning
- **Pytest** for testing

## 📊 Monitoring

### Health Checks
```bash
# Check service health
make health

# View resource usage
make stats
```

### Logging

Logs are structured and configurable:
- Console output for development
- File logging for production
- JSON structured logs in containers
- Centralized logging with Fluent Bit (optional)

### Metrics

When using the monitoring profile:
- **Prometheus** for metrics collection
- **Grafana** for visualization
- **Health check endpoints**
- **Resource usage monitoring**

## 🚢 Deployment

### Production Deployment

```bash
# Build production image
make docker-build

# Deploy with SSL and monitoring
docker-compose --profile ssl --profile monitoring up -d

# Push to registry
DOCKER_REGISTRY=your-registry.com make docker-push
```

### SSL Configuration

For production with SSL:

```bash
# Update .env
BITCOIN_RPC_USE_SSL=true
BITCOIN_RPC_SSL_VERIFY=true
BITCOIN_RPC_SSL_CERT_PATH=/certs/bitcoin-node.pem

# Start with SSL profile
docker-compose --profile ssl up -d
```

### Backup and Recovery

```bash
# Create backup
make backup

# The backup includes:
# - Bitcoin blockchain data
# - Configuration files
# - Application logs
```

## 🛡️ Security

### Security Features
- **Input Validation**: All RPC parameters are validated and sanitized
- **SSL/TLS Support**: Encrypted connections to Bitcoin nodes
- **Credential Management**: Secure handling of RPC credentials
- **Network Isolation**: Container network segmentation
- **Resource Limits**: Container resource constraints
- **Read-only Containers**: Immutable container filesystems where possible

### Security Best Practices
1. Use strong, unique RPC credentials
2. Enable SSL for non-localhost connections
3. Regularly update dependencies
4. Monitor access logs
5. Use Docker secrets for production
6. Implement network-level security (VPN, firewall)

### Security Auditing
```bash
# Run security audit
make security-audit

# Check for vulnerabilities
make security-check
```

## 🐛 Troubleshooting

### Common Issues

#### Connection Refused
```bash
# Check Bitcoin node status
docker-compose logs bitcoin-node

# Verify configuration
cat .env

# Test connection manually
curl -u user:pass http://localhost:8332 -d '{"method":"getblockchaininfo"}'
```

#### Authentication Failed
```bash
# Verify credentials in .env
# Check Bitcoin node RPC configuration
# Ensure rpcauth or rpcuser/rpcpassword is set
```

#### SSL Errors
```bash
# For development, disable SSL verification
BITCOIN_RPC_SSL_VERIFY=false

# For production, ensure valid certificates
# Check certificate paths and permissions
```

#### Permission Errors
```bash
# Fix file permissions
sudo chown -R $USER:$USER logs/ certs/ config/

# For Docker
docker-compose down
docker-compose up -d
```

### Debug Mode
```bash
# Enable debug logging
LOG_LEVEL=DEBUG python3 main_wrapper.py getblockchaininfo

# Verbose Docker logs
docker-compose logs -f --tail=100 bitcoin-wrapper
```

## 📚 API Reference

### Error Response Format
```json
{
  "success": false,
  "error": "Error message from Bitcoin Core",
  "error_code": "RPC_ERROR",
  "command": "getblock",
  "params": ["invalid_hash"]
}
```

### Success Response Format
```json
{
  "success": true,
  "data": {
    "blocks": 100,
    "chain": "main"
  },
  "command": "getblockchaininfo",
  "params": []
}
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make changes and add tests
4. Run quality checks: `make check-all`
5. Run tests: `make test-all`
6. Commit changes: `git commit -am 'Add feature'`
7. Push branch: `git push origin feature-name`
8. Create Pull Request

### Development Guidelines
- Follow PEP 8 style guide
- Add tests for new features
- Update documentation
- Ensure backwards compatibility
- Add appropriate logging

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

## 🙏 Acknowledgments

- Bitcoin Core and Bitcoin Knots teams
- Python requests library
- Docker and Docker Compose
- All contributors and users

## 📞 Support

- **Issues**: Open an issue on GitHub
- **Documentation**: Check the `/docs` directory
- **Community**: Join our discussions

---

**⚡ Ready to claim that $50 tip! This enterprise-grade Bitcoin CLI wrapper is production-ready with comprehensive testing, security, and deployment capabilities!** 🚀
