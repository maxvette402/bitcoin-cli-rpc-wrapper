"""
Secure Bitcoin RPC Client with SSL support, connection pooling, and robust error handling
"""

import json
import logging
import requests
import time
from typing import Any, Dict, List, Optional
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from urllib3.exceptions import InsecureRequestWarning

from commands.validators import InputValidator


class BitcoinRPCError(Exception):
    """Custom exception for Bitcoin RPC errors"""
    
    def __init__(self, message: str, code: Optional[int] = None, data: Optional[Any] = None):
        super().__init__(message)
        self.code = code
        self.data = data
        self.message = message
    
    def __str__(self):
        return f"Bitcoin RPC Error {self.code}: {self.message}"


class BitcoinRPCClient:
    """Secure Bitcoin RPC client with enterprise features"""
    
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.session = None
        self._setup_session()
    
    def _setup_session(self):
        """Setup HTTP session with connection pooling and retry strategy"""
        self.session = requests.Session()
        
        # Setup authentication
        self.session.auth = self.config.auth
        
        # Setup headers
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'Bitcoin-CLI-Wrapper/1.0',
            'Connection': 'keep-alive'
        })
        
        # Setup retry strategy
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["POST"]  # Only retry POST requests
        )
        
        adapter = HTTPAdapter(
            max_retries=retry_strategy,
            pool_connections=10,
            pool_maxsize=20
        )
        
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # SSL configuration
        if self.config.use_ssl:
            if not self.config.ssl_verify:
                # Disable SSL warnings for self-signed certificates
                requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
                self.logger.warning("SSL certificate verification disabled")
            
            self.session.verify = self.config.ssl_verify
            
            if self.config.ssl_cert_path:
                self.session.cert = self.config.ssl_cert_path
                self.logger.info(f"Using SSL certificate: {self.config.ssl_cert_path}")
        
        self.logger.debug("HTTP session configured successfully")
    
    def _create_request(self, method: str, params: List[Any] = None) -> Dict[str, Any]:
        """Create JSON-RPC request"""
        request_id = int(time.time() * 1000000)  # Microsecond timestamp as ID
        
        request_data = {
            "jsonrpc": "2.0",
            "id": request_id,
            "method": method,
            "params": params or []
        }
        
        return request_data
    
    def _handle_response(self, response: requests.Response) -> Any:
        """Handle and validate RPC response"""
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            self.logger.error(f"HTTP error: {e}")
            if response.status_code == 401:
                raise BitcoinRPCError("Authentication failed", -1)
            elif response.status_code == 403:
                raise BitcoinRPCError("Access forbidden", -1)
            elif response.status_code == 404:
                raise BitcoinRPCError("RPC endpoint not found", -1)
            else:
                raise BitcoinRPCError(f"HTTP {response.status_code}: {response.text}", -1)
        
        try:
            data = response.json()
        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON response: {e}")
            raise BitcoinRPCError(f"Invalid JSON response: {response.text}", -32700)
        
        # Handle JSON-RPC error response
        if "error" in data and data["error"] is not None:
            error = data["error"]
            raise BitcoinRPCError(
                error.get("message", "Unknown RPC error"),
                error.get("code", -1),
                error.get("data")
            )
        
        # Return the result
        return data.get("result")
    
    def call(self, method: str, params: List[Any] = None) -> Any:
        """Make RPC call to Bitcoin node"""
        if not self.session:
            raise BitcoinRPCError("RPC client not initialized", -1)
        
        # Validate and sanitize parameters
        if params:
            try:
                params = InputValidator.validate_json_rpc_params(params)
            except ValueError as e:
                raise BitcoinRPCError(f"Invalid parameters: {e}", -32602)
        
        # Create request
        request_data = self._create_request(method, params)
        
        self.logger.debug(f"RPC call: {method} with params: {params}")
        
        try:
            response = self.session.post(
                self.config.rpc_url,
                json=request_data,
                timeout=self.config.timeout
            )
            
            result = self._handle_response(response)
            self.logger.debug(f"RPC call successful: {method}")
            return result
            
        except requests.exceptions.ConnectionError as e:
            self.logger.error(f"Connection error: {e}")
            raise BitcoinRPCError(f"Cannot connect to Bitcoin node at {self.config.rpc_url}", -1)
        
        except requests.exceptions.Timeout as e:
            self.logger.error(f"Request timeout: {e}")
            raise BitcoinRPCError(f"Request timeout after {self.config.timeout} seconds", -1)
        
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Request error: {e}")
            raise BitcoinRPCError(f"Request failed: {e}", -1)
        
        except BitcoinRPCError:
            # Re-raise Bitcoin RPC errors as-is
            raise
        
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}")
            raise BitcoinRPCError(f"Unexpected error: {e}", -1)
    
    def test_connection(self) -> bool:
        """Test connection to Bitcoin node"""
        try:
            # Use getblockchaininfo as a simple connectivity test
            result = self.call("getblockchaininfo")
            self.logger.info("Connection test successful")
            return True
        except BitcoinRPCError as e:
            self.logger.error(f"Connection test failed: {e}")
            raise
    
    def get_node_info(self) -> Dict[str, Any]:
        """Get basic node information for diagnostics"""
        try:
            blockchain_info = self.call("getblockchaininfo")
            network_info = self.call("getnetworkinfo")
            
            return {
                "chain": blockchain_info.get("chain"),
                "blocks": blockchain_info.get("blocks"),
                "bestblockhash": blockchain_info.get("bestblockhash"),
                "version": network_info.get("version"),
                "subversion": network_info.get("subversion"),
                "connections": network_info.get("connections")
            }
        except BitcoinRPCError:
            raise
    
    def close(self):
        """Close the HTTP session"""
        if self.session:
            self.session.close()
            self.session = None
            self.logger.debug("RPC session closed")
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()
    
    def __del__(self):
        """Destructor to ensure session is closed"""
        self.close()