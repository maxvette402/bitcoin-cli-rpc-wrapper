"""
Test suite for Bitcoin RPC client
"""

import json
import pytest
import requests
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add lib directory to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'lib'))

from rpc_client import BitcoinRPCClient, BitcoinRPCError
from config import Config


class MockConfig:
    """Mock configuration for testing"""
    
    def __init__(self, **kwargs):
        self.host = kwargs.get('host', '127.0.0.1')
        self.port = kwargs.get('port', 8332)
        self.user = kwargs.get('user', 'testuser')
        self.password = kwargs.get('password', 'testpass')
        self.timeout = kwargs.get('timeout', 30)
        self.network = kwargs.get('network', 'mainnet')
        self.use_ssl = kwargs.get('use_ssl', False)
        self.ssl_verify = kwargs.get('ssl_verify', True)
        self.ssl_cert_path = kwargs.get('ssl_cert_path', None)
        self.log_level = kwargs.get('log_level', 'INFO')
        self.log_file = kwargs.get('log_file', None)
    
    @property
    def rpc_url(self):
        scheme = 'https' if self.use_ssl else 'http'
        return f"{scheme}://{self.host}:{self.port}"
    
    @property
    def auth(self):
        return (self.user, self.password)


class TestBitcoinRPCError:
    """Test Bitcoin RPC error handling"""
    
    def test_error_creation(self):
        error = BitcoinRPCError("Test error", -1, {"detail": "test"})
        
        assert error.message == "Test error"
        assert error.code == -1
        assert error.data == {"detail": "test"}
        assert str(error) == "Bitcoin RPC Error -1: Test error"
    
    def test_error_without_code(self):
        error = BitcoinRPCError("Test error")
        
        assert error.message == "Test error"
        assert error.code is None
        assert error.data is None


class TestBitcoinRPCClient:
    """Test Bitcoin RPC client functionality"""
    
    def setup_method(self):
        """Setup for each test method"""
        self.config = MockConfig()
        
    def test_client_initialization(self):
        """Test RPC client initialization"""
        client = BitcoinRPCClient(self.config)
        
        assert client.config == self.config
        assert client.session is not None
        assert client.session.auth == ('testuser', 'testpass')
        assert client.session.headers['Content-Type'] == 'application/json'
        assert 'Bitcoin-CLI-Wrapper' in client.session.headers['User-Agent']
    
    def test_ssl_configuration(self):
        """Test SSL configuration"""
        # Test SSL enabled
        ssl_config = MockConfig(use_ssl=True, ssl_verify=True, ssl_cert_path='/path/to/cert.pem')
        client = BitcoinRPCClient(ssl_config)
        
        assert client.session.verify == True
        assert client.session.cert == '/path/to/cert.pem'
        
        # Test SSL disabled verification
        ssl_config_no_verify = MockConfig(use_ssl=True, ssl_verify=False)
        with patch('requests.packages.urllib3.disable_warnings'):
            client = BitcoinRPCClient(ssl_config_no_verify)
            assert client.session.verify == False
    
    def test_create_request(self):
        """Test JSON-RPC request creation"""
        client = BitcoinRPCClient(self.config)
        
        request = client._create_request("getblockchaininfo")
        
        assert request["jsonrpc"] == "2.0"
        assert request["method"] == "getblockchaininfo"
        assert request["params"] == []
        assert isinstance(request["id"], int)
        
        # Test with parameters
        request_with_params = client._create_request("getblock", ["hash123", 1])
        
        assert request_with_params["params"] == ["hash123", 1]
    
    def test_handle_response_success(self):
        """Test successful response handling"""
        client = BitcoinRPCClient(self.config)
        
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "jsonrpc": "2.0",
            "id": 1,
            "result": {"blocks": 100, "chain": "main"}
        }
        
        result = client._handle_response(mock_response)
        
        assert result == {"blocks": 100, "chain": "main"}
    
    def test_handle_response_rpc_error(self):
        """Test RPC error response handling"""
        client = BitcoinRPCClient(self.config)
        
        # Mock RPC error response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "jsonrpc": "2.0",
            "id": 1,
            "error": {
                "code": -32601,
                "message": "Method not found"
            }
        }
        
        with pytest.raises(BitcoinRPCError) as exc_info:
            client._handle_response(mock_response)
        
        assert exc_info.value.code == -32601
        assert "Method not found" in str(exc_info.value)
    
    def test_handle_response_http_error(self):
        """Test HTTP error response handling"""
        client = BitcoinRPCClient(self.config)
        
        # Mock HTTP 401 error
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("401 Unauthorized")
        
        with pytest.raises(BitcoinRPCError) as exc_info:
            client._handle_response(mock_response)
        
        assert "Authentication failed" in str(exc_info.value)
        
        # Mock HTTP 404 error
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("404 Not Found")
        
        with pytest.raises(BitcoinRPCError) as exc_info:
            client._handle_response(mock_response)
        
        assert "RPC endpoint not found" in str(exc_info.value)
    
    def test_handle_response_invalid_json(self):
        """Test invalid JSON response handling"""
        client = BitcoinRPCClient(self.config)
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.raise_for_status.return_value = None
        mock_response.json.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)
        mock_response.text = "Invalid JSON response"
        
        with pytest.raises(BitcoinRPCError) as exc_info:
            client._handle_response(mock_response)
        
        assert exc_info.value.code == -32700
        assert "Invalid JSON response" in str(exc_info.value)
    
    @patch('requests.Session.post')
    def test_successful_rpc_call(self, mock_post):
        """Test successful RPC call"""
        client = BitcoinRPCClient(self.config)
        
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "jsonrpc": "2.0",
            "id": 1,
            "result": {"blocks": 100}
        }
        mock_post.return_value = mock_response
        
        result = client.call("getblockchaininfo")
        
        assert result == {"blocks": 100}
        assert mock_post.called
        
        # Verify request parameters
        call_args = mock_post.call_args
        assert call_args[1]['timeout'] == 30
        
        # Verify JSON payload
        json_data = call_args[1]['json']
        assert json_data['method'] == 'getblockchaininfo'
        assert json_data['params'] == []
    
    @patch('requests.Session.post')
    def test_rpc_call_with_parameters(self, mock_post):
        """Test RPC call with parameters"""
        client = BitcoinRPCClient(self.config)
        
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "jsonrpc": "2.0",
            "id": 1,
            "result": "block_data"
        }
        mock_post.return_value = mock_response
        
        result = client.call("getblock", ["hash123", 1])
        
        assert result == "block_data"
        
        # Verify parameters were passed correctly
        json_data = mock_post.call_args[1]['json']
        assert json_data['method'] == 'getblock'
        assert json_data['params'] == ["hash123", 1]
    
    @patch('requests.Session.post')
    def test_connection_error(self, mock_post):
        """Test connection error handling"""
        client = BitcoinRPCClient(self.config)
        
        mock_post.side_effect = requests.exceptions.ConnectionError("Connection refused")
        
        with pytest.raises(BitcoinRPCError) as exc_info:
            client.call("getblockchaininfo")
        
        assert "Cannot connect to Bitcoin node" in str(exc_info.value)
    
    @patch('requests.Session.post')
    def test_timeout_error(self, mock_post):
        """Test timeout error handling"""
        client = BitcoinRPCClient(self.config)
        
        mock_post.side_effect = requests.exceptions.Timeout("Request timeout")
        
        with pytest.raises(BitcoinRPCError) as exc_info:
            client.call("getblockchaininfo")
        
        assert "Request timeout after 30 seconds" in str(exc_info.value)
    
    @patch('requests.Session.post')
    def test_parameter_validation(self, mock_post):
        """Test parameter validation"""
        client = BitcoinRPCClient(self.config)
        
        # Test with invalid parameters
        with pytest.raises(BitcoinRPCError) as exc_info:
            client.call("getblock", ["invalid;chars"])
        
        assert "Invalid parameters" in str(exc_info.value)
        assert exc_info.value.code == -32602
    
    @patch('requests.Session.post')
    def test_connection_test(self, mock_post):
        """Test connection testing functionality"""
        client = BitcoinRPCClient(self.config)
        
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "jsonrpc": "2.0",
            "id": 1,
            "result": {"blocks": 100}
        }
        mock_post.return_value = mock_response
        
        # Test successful connection
        result = client.test_connection()
        assert result == True
        
        # Verify it called getblockchaininfo
        json_data = mock_post.call_args[1]['json']
        assert json_data['method'] == 'getblockchaininfo'
    
    @patch('requests.Session.post')
    def test_get_node_info(self, mock_post):
        """Test node information gathering"""
        client = BitcoinRPCClient(self.config)
        
        # Mock responses for blockchain and network info
        blockchain_response = Mock()
        blockchain_response.status_code = 200
        blockchain_response.raise_for_status.return_value = None
        blockchain_response.json.return_value = {
            "jsonrpc": "2.0",
            "id": 1,
            "result": {
                "chain": "main",
                "blocks": 100,
                "bestblockhash": "abc123"
            }
        }
        
        network_response = Mock()
        network_response.status_code = 200
        network_response.raise_for_status.return_value = None
        network_response.json.return_value = {
            "jsonrpc": "2.0",
            "id": 2,
            "result": {
                "version": 220000,
                "subversion": "/Satoshi:22.0.0/",
                "connections": 8
            }
        }
        
        mock_post.side_effect = [blockchain_response, network_response]
        
        node_info = client.get_node_info()
        
        assert node_info["chain"] == "main"
        assert node_info["blocks"] == 100
        assert node_info["version"] == 220000
        assert node_info["connections"] == 8
    
    def test_context_manager(self):
        """Test context manager functionality"""
        client = BitcoinRPCClient(self.config)
        
        with client as c:
            assert c.session is not None
        
        # Session should be closed after context exit
        assert client.session is None
    
    def test_session_cleanup(self):
        """Test session cleanup"""
        client = BitcoinRPCClient(self.config)
        
        # Verify session exists
        assert client.session is not None
        
        # Close session
        client.close()
        assert client.session is None
        
        # Should be safe to call close multiple times
        client.close()
        assert client.session is None
    
    def test_retry_strategy(self):
        """Test retry strategy configuration"""
        client = BitcoinRPCClient(self.config)
        
        # Verify retry adapter is configured
        adapter = client.session.get_adapter('http://')
        assert adapter.max_retries.total == 3
        assert adapter.max_retries.backoff_factor == 1
        assert 500 in adapter.max_retries.status_forcelist
        assert 502 in adapter.max_retries.status_forcelist
        assert 503 in adapter.max_retries.status_forcelist
    
    def test_session_configuration(self):
        """Test HTTP session configuration"""
        client = BitcoinRPCClient(self.config)
        
        # Check headers
        assert client.session.headers['Content-Type'] == 'application/json'
        assert 'Bitcoin-CLI-Wrapper' in client.session.headers['User-Agent']
        assert client.session.headers['Connection'] == 'keep-alive'
        
        # Check authentication
        assert client.session.auth == ('testuser', 'testpass')
    
    @patch('requests.Session.post')
    def test_error_propagation(self, mock_post):
        """Test that original Bitcoin errors are preserved"""
        client = BitcoinRPCClient(self.config)
        
        # Mock Bitcoin Core error response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "jsonrpc": "2.0",
            "id": 1,
            "error": {
                "code": -5,
                "message": "Block not found",
                "data": None
            }
        }
        mock_post.return_value = mock_response
        
        with pytest.raises(BitcoinRPCError) as exc_info:
            client.call("getblock", ["nonexistent_hash"])
        
        # Verify original error details are preserved
        assert exc_info.value.code == -5
        assert "Block not found" in str(exc_info.value)


if __name__ == '__main__':
    pytest.main([__file__])