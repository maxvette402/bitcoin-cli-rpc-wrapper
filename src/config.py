"""
Configuration Management - Hybrid approach supporting .env, environment variables, and Docker secrets
"""

import os
import logging
from typing import Optional, Dict, Any
from commands.validators import ConfigValidator


class Config:
    """Configuration manager with hybrid secret handling"""
    
    def __init__(self, config_file: str = '.env'):
        self.config_file = config_file
        self.logger = logging.getLogger(__name__)
        
        # Load configuration
        self._load_config()
        self._validate_config()
    
    def _load_config(self):
        """Load configuration from multiple sources (priority: env vars > docker secrets > .env file)"""
        
        # Default values
        defaults = {
            'BITCOIN_RPC_HOST': '127.0.0.1',
            'BITCOIN_RPC_PORT': '8332',
            'BITCOIN_RPC_TIMEOUT': '30',
            'BITCOIN_NETWORK': 'mainnet',
            'BITCOIN_RPC_USE_SSL': 'false',
            'BITCOIN_RPC_SSL_VERIFY': 'true',
            'BITCOIN_RPC_SSL_CERT_PATH': '',
            'LOG_LEVEL': 'INFO',
            'LOG_FILE': 'bitcoin_wrapper.log'
        }
        
        # Start with defaults
        config = defaults.copy()
        
        # Load from .env file if exists
        env_config = self._load_env_file()
        config.update(env_config)
        
        # Override with environment variables
        for key in defaults.keys():
            env_value = os.getenv(key)
            if env_value is not None:
                config[key] = env_value
        
        # Handle Docker secrets (priority over everything)
        config['BITCOIN_RPC_USER'] = self._get_secret('BITCOIN_RPC_USER', 'bitcoin_rpc_user')
        config['BITCOIN_RPC_PASSWORD'] = self._get_secret('BITCOIN_RPC_PASSWORD', 'bitcoin_rpc_password')
        
        # Convert to instance attributes
        self.host = config['BITCOIN_RPC_HOST']
        self.port = int(config['BITCOIN_RPC_PORT'])
        self.user = config['BITCOIN_RPC_USER']
        self.password = config['BITCOIN_RPC_PASSWORD']
        self.timeout = int(config['BITCOIN_RPC_TIMEOUT'])
        self.network = config['BITCOIN_NETWORK']
        self.use_ssl = config['BITCOIN_RPC_USE_SSL'].lower() == 'true'
        self.ssl_verify = config['BITCOIN_RPC_SSL_VERIFY'].lower() == 'true'
        self.ssl_cert_path = config['BITCOIN_RPC_SSL_CERT_PATH'] or None
        self.log_level = config['LOG_LEVEL']
        self.log_file = config['LOG_FILE'] if config['LOG_FILE'] else None
    
    def _load_env_file(self) -> Dict[str, str]:
        """Load configuration from .env file"""
        config = {}
        
        if not os.path.exists(self.config_file):
            self.logger.warning(f"Configuration file not found: {self.config_file}")
            return config
        
        try:
            with open(self.config_file, 'r') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    
                    # Skip empty lines and comments
                    if not line or line.startswith('#'):
                        continue
                    
                    # Parse key=value
                    if '=' not in line:
                        self.logger.warning(f"Invalid line {line_num} in {self.config_file}: {line}")
                        continue
                    
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    
                    # Remove quotes if present
                    if value.startswith('"') and value.endswith('"'):
                        value = value[1:-1]
                    elif value.startswith("'") and value.endswith("'"):
                        value = value[1:-1]
                    
                    config[key] = value
            
            self.logger.debug(f"Loaded configuration from {self.config_file}")
            
        except Exception as e:
            self.logger.error(f"Error loading configuration file {self.config_file}: {e}")
            raise
        
        return config
    
    def _get_secret(self, env_var: str, secret_name: str) -> Optional[str]:
        """Get secret from environment variable, Docker secret, or .env file"""
        
        # 1. Check environment variable first
        value = os.getenv(env_var)
        if value:
            self.logger.debug(f"Using environment variable for {env_var}")
            return value
        
        # 2. Check Docker secret
        secret_path = f"/run/secrets/{secret_name}"
        if os.path.exists(secret_path):
            try:
                with open(secret_path, 'r') as f:
                    value = f.read().strip()
                self.logger.debug(f"Using Docker secret for {env_var}")
                return value
            except Exception as e:
                self.logger.warning(f"Error reading Docker secret {secret_path}: {e}")
        
        # 3. Check .env file
        env_config = self._load_env_file()
        value = env_config.get(env_var)
        if value:
            self.logger.debug(f"Using .env file for {env_var}")
            return value
        
        # 4. Not found anywhere
        self.logger.error(f"Required secret {env_var} not found in environment, Docker secrets, or .env file")
        raise ValueError(f"Required configuration {env_var} not found")
    
    def _validate_config(self):
        """Validate configuration values"""
        validator = ConfigValidator()
        
        # Validate required fields
        if not self.user:
            raise ValueError("BITCOIN_RPC_USER is required")
        
        if not self.password:
            raise ValueError("BITCOIN_RPC_PASSWORD is required")
        
        # Validate host
        if not validator.is_valid_host(self.host):
            raise ValueError(f"Invalid host: {self.host}")
        
        # Validate port
        if not validator.is_valid_port(self.port):
            raise ValueError(f"Invalid port: {self.port}")
        
        # Validate network
        if self.network not in ['mainnet', 'testnet', 'regtest']:
            raise ValueError(f"Invalid network: {self.network}. Must be mainnet, testnet, or regtest")
        
        # Validate SSL configuration
        if self.ssl_cert_path and not os.path.exists(self.ssl_cert_path):
            raise ValueError(f"SSL certificate file not found: {self.ssl_cert_path}")
        
        # Validate log level
        valid_log_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if self.log_level.upper() not in valid_log_levels:
            raise ValueError(f"Invalid log level: {self.log_level}. Must be one of: {valid_log_levels}")
        
        self.logger.info("Configuration validation successful")
    
    @property
    def rpc_url(self) -> str:
        """Get the full RPC URL"""
        scheme = 'https' if self.use_ssl else 'http'
        return f"{scheme}://{self.host}:{self.port}"
    
    @property
    def auth(self) -> tuple:
        """Get authentication tuple"""
        return (self.user, self.password)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary (excluding sensitive data)"""
        return {
            'host': self.host,
            'port': self.port,
            'network': self.network,
            'use_ssl': self.use_ssl,
            'ssl_verify': self.ssl_verify,
            'ssl_cert_path': self.ssl_cert_path,
            'timeout': self.timeout,
            'log_level': self.log_level,
            'log_file': self.log_file,
            'rpc_url': self.rpc_url
        }
    
    def __str__(self) -> str:
        """String representation (safe for logging)"""
        safe_config = self.to_dict()
        return f"BitcoinConfig({safe_config})"
