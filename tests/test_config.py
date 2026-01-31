"""
Test suite for configuration management
"""

import os
import tempfile
import pytest
from unittest.mock import patch, mock_open
import sys

# Add lib directory to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'lib'))

from config import Config
from validators import ConfigValidator


class TestConfigValidator:
    """Test configuration validators"""
    
    def test_valid_hosts(self):
        validator = ConfigValidator()
        
        # Valid IP addresses
        assert validator.is_valid_host("127.0.0.1")
        assert validator.is_valid_host("192.168.1.1")
        assert validator.is_valid_host("::1")
        assert validator.is_valid_host("2001:db8::1")
        
        # Valid hostnames
        assert validator.is_valid_host("localhost")
        assert validator.is_valid_host("bitcoin-node")
        assert validator.is_valid_host("example.com")
        assert validator.is_valid_host("bitcoin.example.com")
    
    def test_invalid_hosts(self):
        validator = ConfigValidator()
        
        # Invalid inputs
        assert not validator.is_valid_host("")
        assert not validator.is_valid_host("256.256.256.256")
        assert not validator.is_valid_host("-invalid")
        assert not validator.is_valid_host("invalid-")
        assert not validator.is_valid_host("invalid..com")
    
    def test_valid_ports(self):
        validator = ConfigValidator()
        
        # Valid ports
        assert validator.is_valid_port(8332)
        assert validator.is_valid_port("8332")
        assert validator.is_valid_port(1)
        assert validator.is_valid_port(65535)
        assert validator.is_valid_port("18332")
    
    def test_invalid_ports(self):
        validator = ConfigValidator()
        
        # Invalid ports
        assert not validator.is_valid_port(0)
        assert not validator.is_valid_port(-1)
        assert not validator.is_valid_port(65536)
        assert not validator.is_valid_port("invalid")
        assert not validator.is_valid_port("")
        assert not validator.is_valid_port(None)
    
    def test_valid_timeouts(self):
        validator = ConfigValidator()
        
        # Valid timeouts
        assert validator.is_valid_timeout(30)
        assert validator.is_valid_timeout("30")
        assert validator.is_valid_timeout(1)
        assert validator.is_valid_timeout(300)
    
    def test_invalid_timeouts(self):
        validator = ConfigValidator()
        
        # Invalid timeouts
        assert not validator.is_valid_timeout(0)
        assert not validator.is_valid_timeout(-1)
        assert not validator.is_valid_timeout(301)
        assert not validator.is_valid_timeout("invalid")
        assert not validator.is_valid_timeout(None)


class TestConfig:
    """Test configuration loading and validation"""
    
    def create_temp_config(self, content):
        """Helper to create temporary config file"""
        temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.env')
        temp_file.write(content)
        temp_file.close()
        return temp_file.name
    
    def test_default_config(self):
        """Test default configuration values"""
        with patch.dict(os.environ, {
            'BITCOIN_RPC_USER': 'testuser',
            'BITCOIN_RPC_PASSWORD': 'testpass'
        }):
            config = Config('nonexistent.env')
            
            assert config.host == '127.0.0.1'
            assert config.port == 8332
            assert config.user == 'testuser'
            assert config.password == 'testpass'
            assert config.timeout == 30
            assert config.network == 'mainnet'
            assert config.use_ssl == False
            assert config.ssl_verify == True
            assert config.log_level == 'INFO'
    
    def test_env_file_loading(self):
        """Test loading configuration from .env file"""
        config_content = """
# Test configuration
BITCOIN_RPC_HOST=192.168.1.100
BITCOIN_RPC_PORT=18332
BITCOIN_RPC_USER=testuser
BITCOIN_RPC_PASSWORD=testpass
BITCOIN_NETWORK=testnet
BITCOIN_RPC_USE_SSL=true
LOG_LEVEL=DEBUG
"""
        
        config_file = self.create_temp_config(config_content)
        
        try:
            config = Config(config_file)
            
            assert config.host == '192.168.1.100'
            assert config.port == 18332
            assert config.user == 'testuser'
            assert config.password == 'testpass'
            assert config.network == 'testnet'
            assert config.use_ssl == True
            assert config.log_level == 'DEBUG'
        finally:
            os.unlink(config_file)
    
    def test_environment_variable_override(self):
        """Test environment variables override .env file"""
        config_content = """
BITCOIN_RPC_HOST=192.168.1.100
BITCOIN_RPC_PORT=18332
BITCOIN_RPC_USER=fileuser
BITCOIN_RPC_PASSWORD=filepass
"""
        
        config_file = self.create_temp_config(config_content)
        
        try:
            with patch.dict(os.environ, {
                'BITCOIN_RPC_HOST': '10.0.0.1',
                'BITCOIN_RPC_USER': 'envuser',
                'BITCOIN_RPC_PASSWORD': 'envpass'
            }):
                config = Config(config_file)
                
                # Environment variables should override file values
                assert config.host == '10.0.0.1'
                assert config.user == 'envuser'
                assert config.password == 'envpass'
                
                # File values should be used when no env var exists
                assert config.port == 18332
        finally:
            os.unlink(config_file)
    
    def test_docker_secrets(self):
        """Test Docker secrets support"""
        # Mock Docker secret files
        with patch('os.path.exists') as mock_exists:
            with patch('builtins.open', mock_open(read_data='secret_value')):
                # Simulate Docker secret files exist
                mock_exists.side_effect = lambda path: path in [
                    '/run/secrets/bitcoin_rpc_user',
                    '/run/secrets/bitcoin_rpc_password'
                ]
                
                config_content = """
BITCOIN_RPC_HOST=127.0.0.1
BITCOIN_RPC_PORT=8332
"""
                
                config_file = self.create_temp_config(config_content)
                
                try:
                    config = Config(config_file)
                    
                    # Should use Docker secrets
                    assert config.user == 'secret_value'
                    assert config.password == 'secret_value'
                finally:
                    os.unlink(config_file)
    
    def test_quoted_values(self):
        """Test handling of quoted values in .env file"""
        config_content = '''
BITCOIN_RPC_USER="quoted_user"
BITCOIN_RPC_PASSWORD='single_quoted_pass'
BITCOIN_RPC_HOST=unquoted_host
'''
        
        config_file = self.create_temp_config(config_content)
        
        try:
            config = Config(config_file)
            
            assert config.user == 'quoted_user'
            assert config.password == 'single_quoted_pass'
            assert config.host == 'unquoted_host'
        finally:
            os.unlink(config_file)
    
    def test_comments_and_empty_lines(self):
        """Test handling of comments and empty lines"""
        config_content = """
# This is a comment
BITCOIN_RPC_HOST=127.0.0.1

# Another comment
BITCOIN_RPC_PORT=8332

BITCOIN_RPC_USER=testuser
BITCOIN_RPC_PASSWORD=testpass
"""
        
        config_file = self.create_temp_config(config_content)
        
        try:
            config = Config(config_file)
            
            assert config.host == '127.0.0.1'
            assert config.port == 8332
            assert config.user == 'testuser'
            assert config.password == 'testpass'
        finally:
            os.unlink(config_file)
    
    def test_validation_errors(self):
        """Test configuration validation errors"""
        # Test missing credentials
        with pytest.raises(ValueError, match="Required configuration BITCOIN_RPC_USER not found"):
            Config('nonexistent.env')
        
        # Test invalid port
        with patch.dict(os.environ, {
            'BITCOIN_RPC_USER': 'testuser',
            'BITCOIN_RPC_PASSWORD': 'testpass',
            'BITCOIN_RPC_PORT': '99999'
        }):
            with pytest.raises(ValueError, match="Invalid port"):
                Config('nonexistent.env')
        
        # Test invalid network
        with patch.dict(os.environ, {
            'BITCOIN_RPC_USER': 'testuser',
            'BITCOIN_RPC_PASSWORD': 'testpass',
            'BITCOIN_NETWORK': 'invalid'
        }):
            with pytest.raises(ValueError, match="Invalid network"):
                Config('nonexistent.env')
    
    def test_rpc_url_generation(self):
        """Test RPC URL generation"""
        with patch.dict(os.environ, {
            'BITCOIN_RPC_USER': 'testuser',
            'BITCOIN_RPC_PASSWORD': 'testpass',
            'BITCOIN_RPC_HOST': 'bitcoin.example.com',
            'BITCOIN_RPC_PORT': '8332',
            'BITCOIN_RPC_USE_SSL': 'false'
        }):
            config = Config('nonexistent.env')
            assert config.rpc_url == 'http://bitcoin.example.com:8332'
        
        with patch.dict(os.environ, {
            'BITCOIN_RPC_USER': 'testuser',
            'BITCOIN_RPC_PASSWORD': 'testpass',
            'BITCOIN_RPC_HOST': 'bitcoin.example.com',
            'BITCOIN_RPC_PORT': '8332',
            'BITCOIN_RPC_USE_SSL': 'true'
        }):
            config = Config('nonexistent.env')
            assert config.rpc_url == 'https://bitcoin.example.com:8332'
    
    def test_auth_tuple(self):
        """Test authentication tuple generation"""
        with patch.dict(os.environ, {
            'BITCOIN_RPC_USER': 'testuser',
            'BITCOIN_RPC_PASSWORD': 'testpass'
        }):
            config = Config('nonexistent.env')
            assert config.auth == ('testuser', 'testpass')
    
    def test_to_dict(self):
        """Test configuration dictionary representation"""
        with patch.dict(os.environ, {
            'BITCOIN_RPC_USER': 'testuser',
            'BITCOIN_RPC_PASSWORD': 'testpass'
        }):
            config = Config('nonexistent.env')
            config_dict = config.to_dict()
            
            # Should not include sensitive data
            assert 'user' not in config_dict
            assert 'password' not in config_dict
            
            # Should include non-sensitive data
            assert config_dict['host'] == '127.0.0.1'
            assert config_dict['port'] == 8332
            assert config_dict['network'] == 'mainnet'
    
    def test_ssl_certificate_validation(self):
        """Test SSL certificate path validation"""
        # Create a temporary certificate file
        temp_cert = tempfile.NamedTemporaryFile(suffix='.pem', delete=False)
        temp_cert.close()
        
        try:
            with patch.dict(os.environ, {
                'BITCOIN_RPC_USER': 'testuser',
                'BITCOIN_RPC_PASSWORD': 'testpass',
                'BITCOIN_RPC_SSL_CERT_PATH': temp_cert.name
            }):
                config = Config('nonexistent.env')
                assert config.ssl_cert_path == temp_cert.name
        finally:
            os.unlink(temp_cert.name)
        
        # Test invalid certificate path
        with patch.dict(os.environ, {
            'BITCOIN_RPC_USER': 'testuser',
            'BITCOIN_RPC_PASSWORD': 'testpass',
            'BITCOIN_RPC_SSL_CERT_PATH': '/nonexistent/cert.pem'
        }):
            with pytest.raises(ValueError, match="SSL certificate file not found"):
                Config('nonexistent.env')


if __name__ == '__main__':
    pytest.main([__file__])
