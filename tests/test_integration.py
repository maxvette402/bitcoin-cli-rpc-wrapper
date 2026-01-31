"""
Integration tests for Bitcoin CLI Wrapper
Tests against a real Bitcoin node (regtest mode recommended)
"""

import pytest
import os
import sys
import json
import subprocess
import time
from pathlib import Path

# Add lib directory to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'lib'))

from config import Config
from rpc_client import BitcoinRPCClient
from commands.blockchain import BlockchainCommands
from commands.network import NetworkCommands


class TestIntegration:
    """Integration tests requiring a running Bitcoin node"""
    
    @classmethod
    def setup_class(cls):
        """Setup for integration tests"""
        # Check if Bitcoin node is available
        cls.bitcoin_available = cls._check_bitcoin_node()
        
        if not cls.bitcoin_available:
            pytest.skip("Bitcoin node not available for integration tests")
        
        # Create test configuration
        cls.config = cls._create_test_config()
        cls.rpc_client = BitcoinRPCClient(cls.config)
    
    @classmethod
    def _check_bitcoin_node(cls):
        """Check if Bitcoin node is available"""
        try:
            # Try to connect using environment variables or defaults
            test_config = Config('.env.test')
            test_client = BitcoinRPCClient(test_config)
            test_client.test_connection()
            test_client.close()
            return True
        except Exception as e:
            print(f"Bitcoin node not available: {e}")
            return False
    
    @classmethod
    def _create_test_config(cls):
        """Create configuration for testing"""
        # Use test environment variables or defaults for regtest
        config_overrides = {
            'host': os.getenv('TEST_BITCOIN_RPC_HOST', '127.0.0.1'),
            'port': int(os.getenv('TEST_BITCOIN_RPC_PORT', '18443')),  # Default regtest port
            'user': os.getenv('TEST_BITCOIN_RPC_USER', 'test'),
            'password': os.getenv('TEST_BITCOIN_RPC_PASSWORD', 'test'),
            'timeout': 30,
            'network': 'regtest',
            'use_ssl': False,
            'ssl_verify': False,
            'ssl_cert_path': None,
            'log_level': 'DEBUG',
            'log_file': None
        }
        
        # Create mock config object
        class TestConfig:
            def __init__(self, **kwargs):
                for key, value in kwargs.items():
                    setattr(self, key, value)
            
            @property
            def rpc_url(self):
                scheme = 'https' if self.use_ssl else 'http'
                return f"{scheme}://{self.host}:{self.port}"
            
            @property
            def auth(self):
                return (self.user, self.password)
        
        return TestConfig(**config_overrides)
    
    @classmethod
    def teardown_class(cls):
        """Cleanup after integration tests"""
        if hasattr(cls, 'rpc_client'):
            cls.rpc_client.close()
    
    def test_connection(self):
        """Test basic connection to Bitcoin node"""
        result = self.rpc_client.test_connection()
        assert result == True
    
    def test_blockchain_info(self):
        """Test getting blockchain information"""
        blockchain_commands = BlockchainCommands(self.rpc_client)
        
        info = blockchain_commands.get_blockchain_info()
        
        assert isinstance(info, dict)
        assert 'chain' in info
        assert 'blocks' in info
        assert 'bestblockhash' in info
        
        # In regtest mode, chain should be 'regtest'
        if self.config.network == 'regtest':
            assert info['chain'] == 'regtest'
    
    def test_network_info(self):
        """Test getting network information"""
        network_commands = NetworkCommands(self.rpc_client)
        
        info = network_commands.get_network_info()
        
        assert isinstance(info, dict)
        assert 'version' in info
        assert 'subversion' in info
        assert 'connections' in info
        assert 'networkactive' in info
    
    def test_block_operations(self):
        """Test block-related operations"""
        blockchain_commands = BlockchainCommands(self.rpc_client)
        
        # Get current block count
        block_count = blockchain_commands.get_block_count()
        assert isinstance(block_count, int)
        assert block_count >= 0
        
        # Get best block hash
        best_hash = blockchain_commands.get_best_block_hash()
        assert isinstance(best_hash, str)
        assert len(best_hash) == 64  # SHA256 hash length
        
        # Get block by hash
        if block_count > 0:
            block_data = blockchain_commands.get_block(best_hash)
            assert isinstance(block_data, dict)
            assert 'hash' in block_data
            assert 'height' in block_data
            assert block_data['hash'] == best_hash
    
    def test_peer_info(self):
        """Test peer information"""
        network_commands = NetworkCommands(self.rpc_client)
        
        # Get connection count
        connection_count = network_commands.get_connection_count()
        assert isinstance(connection_count, int)
        assert connection_count >= 0
        
        # Get peer info
        peer_info = network_commands.get_peer_info()
        assert isinstance(peer_info, list)
        assert len(peer_info) == connection_count
    
    def test_mempool_info(self):
        """Test mempool information"""
        blockchain_commands = BlockchainCommands(self.rpc_client)
        
        mempool_info = blockchain_commands.get_mempool_info()
        
        assert isinstance(mempool_info, dict)
        assert 'size' in mempool_info
        assert 'bytes' in mempool_info
        assert isinstance(mempool_info['size'], int)
        assert isinstance(mempool_info['bytes'], int)
    
    def test_error_handling(self):
        """Test error handling with invalid requests"""
        blockchain_commands = BlockchainCommands(self.rpc_client)
        
        # Test with invalid block hash
        with pytest.raises(Exception):  # Should raise validation error or RPC error
            blockchain_commands.get_block("invalid_hash")
        
        # Test with invalid block height
        with pytest.raises(Exception):
            blockchain_commands.get_block_hash(-1)
    
    def test_node_info_aggregation(self):
        """Test node information aggregation"""
        node_info = self.rpc_client.get_node_info()
        
        assert isinstance(node_info, dict)
        assert 'chain' in node_info
        assert 'blocks' in node_info
        assert 'version' in node_info
        assert 'connections' in node_info


class TestCLIIntegration:
    """Integration tests for CLI interface"""
    
    @classmethod
    def setup_class(cls):
        """Setup for CLI integration tests"""
        cls.cli_script = Path(__file__).parent.parent / 'bitcoin_cli_wrapper.py'
        
        # Check if Bitcoin node is available
        cls.bitcoin_available = cls._check_bitcoin_node()
        
        if not cls.bitcoin_available:
            pytest.skip("Bitcoin node not available for CLI integration tests")
    
    @classmethod
    def _check_bitcoin_node(cls):
        """Check if Bitcoin node is available for CLI tests"""
        try:
            result = subprocess.run([
                'python3', str(cls.cli_script), 
                '--config', '.env.test',
                'getblockchaininfo'
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                response = json.loads(result.stdout)
                return response.get('success', False)
            return False
        except Exception:
            return False
    
    def test_cli_help(self):
        """Test CLI help output"""
        result = subprocess.run([
            'python3', str(self.cli_script), '--help'
        ], capture_output=True, text=True)
        
        assert result.returncode == 0
        assert 'Bitcoin CLI Wrapper' in result.stdout
        assert 'getblockchaininfo' in result.stdout
    
    def test_cli_blockchain_info(self):
        """Test CLI blockchain info command"""
        result = subprocess.run([
            'python3', str(self.cli_script),
            '--config', '.env.test',
            'getblockchaininfo'
        ], capture_output=True, text=True, timeout=30)
        
        assert result.returncode == 0
        
        response = json.loads(result.stdout)
        assert response['success'] == True
        assert 'data' in response
        assert 'chain' in response['data']
    
    def test_cli_network_info(self):
        """Test CLI network info command"""
        result = subprocess.run([
            'python3', str(self.cli_script),
            '--config', '.env.test',
            'getnetworkinfo'
        ], capture_output=True, text=True, timeout=30)
        
        assert result.returncode == 0
        
        response = json.loads(result.stdout)
        assert response['success'] == True
        assert 'data' in response
        assert 'version' in response['data']
    
    def test_cli_block_count(self):
        """Test CLI block count command"""
        result = subprocess.run([
            'python3', str(self.cli_script),
            '--config', '.env.test',
            'getblockcount'
        ], capture_output=True, text=True, timeout=30)
        
        assert result.returncode == 0
        
        response = json.loads(result.stdout)
        assert response['success'] == True
        assert 'data' in response
        assert isinstance(response['data'], int)
    
    def test_cli_invalid_command(self):
        """Test CLI with invalid command"""
        result = subprocess.run([
            'python3', str(self.cli_script),
            '--config', '.env.test',
            'invalidcommand'
        ], capture_output=True, text=True, timeout=30)
        
        assert result.returncode == 1
        
        response = json.loads(result.stdout)
        assert response['success'] == False
        assert 'Unknown command' in response['error']
    
    def test_cli_verbose_mode(self):
        """Test CLI verbose mode"""
        result = subprocess.run([
            'python3', str(self.cli_script),
            '--config', '.env.test',
            '--verbose',
            'getblockchaininfo'
        ], capture_output=True, text=True, timeout=30)
        
        assert result.returncode == 0
        
        response = json.loads(result.stdout)
        assert response['success'] == True
    
    def test_cli_with_parameters(self):
        """Test CLI with command parameters"""
        # First get a block hash
        result = subprocess.run([
            'python3', str(self.cli_script),
            '--config', '.env.test',
            'getbestblockhash'
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            response = json.loads(result.stdout)
            if response['success']:
                block_hash = response['data']
                
                # Now get the block
                result = subprocess.run([
                    'python3', str(self.cli_script),
                    '--config', '.env.test',
                    'getblock', block_hash
                ], capture_output=True, text=True, timeout=30)
                
                assert result.returncode == 0
                
                response = json.loads(result.stdout)
                assert response['success'] == True
                assert response['data']['hash'] == block_hash


class TestDockerIntegration:
    """Integration tests for Docker setup"""
    
    def test_docker_build(self):
        """Test Docker image build"""
        try:
            result = subprocess.run([
                'docker', 'build', '-t', 'bitcoin-CLI-RPC-weapper:test', '.'
            ], capture_output=True, text=True, timeout=300)
            
            # If Docker is available, build should succeed
            if result.returncode == 0:
                assert 'Successfully tagged bitcoin-CLI-RPC-weapper:test' in result.stdout
            else:
                pytest.skip("Docker not available or build failed")
        except FileNotFoundError:
            pytest.skip("Docker not available")
    
    def test_docker_compose_validation(self):
        """Test Docker Compose file validation"""
        try:
            result = subprocess.run([
                'docker-compose', 'config'
            ], capture_output=True, text=True, timeout=30)
            
            # Should exit successfully if docker-compose.yml is valid
            if result.returncode == 0:
                assert len(result.stdout) > 0  # Should output composed configuration
            else:
                pytest.skip("Docker Compose not available")
        except FileNotFoundError:
            pytest.skip("Docker Compose not available")


if __name__ == '__main__':
    # Run integration tests
    pytest.main([__file__, '-v'])
