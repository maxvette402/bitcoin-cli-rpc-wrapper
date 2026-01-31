"""
Validators for configuration and user input
"""

import re
import ipaddress
import hashlib
from typing import Union


class ConfigValidator:
    """Validator for configuration values"""
    
    @staticmethod
    def is_valid_host(host: str) -> bool:
        """Validate host (IP address or hostname)"""
        if not host:
            return False
        
        # Check if it's a valid IP address
        try:
            ipaddress.ip_address(host)
            return True
        except ValueError:
            pass
        
        # Check if it's a valid hostname
        hostname_pattern = re.compile(
            r'^(?!-)[A-Z\d-]{1,63}(?<!-)$', re.IGNORECASE
        )
        
        # Split by dots and validate each part
        parts = host.split('.')
        if len(parts) > 1:  # FQDN
            return all(hostname_pattern.match(part) for part in parts)
        else:  # Single hostname
            return hostname_pattern.match(host) is not None
    
    @staticmethod
    def is_valid_port(port: Union[int, str]) -> bool:
        """Validate port number"""
        try:
            port_num = int(port)
            return 1 <= port_num <= 65535
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def is_valid_timeout(timeout: Union[int, str]) -> bool:
        """Validate timeout value"""
        try:
            timeout_num = int(timeout)
            return 1 <= timeout_num <= 300  # 1 second to 5 minutes
        except (ValueError, TypeError):
            return False


class InputValidator:
    """Validator for user input parameters"""
    
    @staticmethod
    def is_valid_block_hash(block_hash: str) -> bool:
        """Validate Bitcoin block hash (64 character hex string)"""
        if not isinstance(block_hash, str):
            return False
        
        # Bitcoin block hashes are 64 character hex strings
        hex_pattern = re.compile(r'^[0-9a-fA-F]{64}$')
        return hex_pattern.match(block_hash) is not None
    
    @staticmethod
    def is_valid_block_height(height: Union[int, str]) -> bool:
        """Validate block height (non-negative integer)"""
        try:
            height_num = int(height)
            return height_num >= 0
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def is_valid_bitcoin_address(address: str) -> bool:
        """Basic Bitcoin address validation (simplified)"""
        if not isinstance(address, str):
            return False
        
        # Basic patterns for different address types
        patterns = [
            r'^[13][a-km-zA-HJ-NP-Z1-9]{25,34}$',  # Legacy P2PKH and P2SH
            r'^bc1[a-z0-9]{39,59}$',               # Bech32 (P2WPKH and P2WSH)
            r'^tb1[a-z0-9]{39,59}$',               # Testnet Bech32
        ]
        
        return any(re.match(pattern, address) for pattern in patterns)
    
    @staticmethod
    def is_valid_transaction_id(txid: str) -> bool:
        """Validate Bitcoin transaction ID (64 character hex string)"""
        if not isinstance(txid, str):
            return False
        
        # Transaction IDs are 64 character hex strings (like block hashes)
        hex_pattern = re.compile(r'^[0-9a-fA-F]{64}$')
        return hex_pattern.match(txid) is not None
    
    @staticmethod
    def hash_with_sha512(data: str) -> str:
        """Hash data with SHA512 (as requested for commands that need hashing)"""
        if not isinstance(data, str):
            raise ValueError("Data must be a string")
        
        return hashlib.sha512(data.encode('utf-8')).hexdigest()
    
    @staticmethod
    def sanitize_rpc_param(param: str) -> str:
        """Sanitize RPC parameters to prevent injection"""
        if not isinstance(param, str):
            return str(param)
        
        # Remove potentially dangerous characters
        # Allow alphanumeric, common punctuation, but be restrictive
        allowed_chars = re.compile(r'^[a-zA-Z0-9\-_./:]+$')
        
        if not allowed_chars.match(param):
            raise ValueError(f"Invalid characters in parameter: {param}")
        
        return param
    
    @staticmethod
    def validate_json_rpc_params(params: list) -> list:
        """Validate and sanitize JSON-RPC parameters"""
        validated_params = []
        
        for param in params:
            if isinstance(param, str):
                # For string parameters, apply basic sanitization
                validated_params.append(InputValidator.sanitize_rpc_param(param))
            elif isinstance(param, (int, float, bool)):
                # Numeric and boolean parameters are safe
                validated_params.append(param)
            elif param is None:
                # None values are acceptable
                validated_params.append(param)
            elif isinstance(param, (list, dict)):
                # Complex types should be handled carefully
                # For now, we'll allow them but could add recursive validation
                validated_params.append(param)
            else:
                raise ValueError(f"Unsupported parameter type: {type(param)}")
        
        return validated_params


class CryptoValidator:
    """Cryptographic validators and utilities"""
    
    @staticmethod
    def verify_hash_algorithm(algorithm: str) -> bool:
        """Verify if hash algorithm is supported"""
        supported_algorithms = [
            'sha1', 'sha224', 'sha256', 'sha384', 'sha512',
            'md5', 'blake2b', 'blake2s'
        ]
        return algorithm.lower() in supported_algorithms
    
    @staticmethod
    def hash_data(data: str, algorithm: str = 'sha512') -> str:
        """Hash data with specified algorithm"""
        if not CryptoValidator.verify_hash_algorithm(algorithm):
            raise ValueError(f"Unsupported hash algorithm: {algorithm}")
        
        if not isinstance(data, str):
            data = str(data)
        
        hash_obj = hashlib.new(algorithm.lower())
        hash_obj.update(data.encode('utf-8'))
        return hash_obj.hexdigest()
    
    @staticmethod
    def verify_ssl_certificate_path(cert_path: str) -> bool:
        """Verify SSL certificate file exists and has correct extension"""
        if not cert_path:
            return False
        
        import os
        
        # Check if file exists
        if not os.path.exists(cert_path):
            return False
        
        # Check file extension
        valid_extensions = ['.pem', '.crt', '.cer', '.p12', '.pfx']
        return any(cert_path.lower().endswith(ext) for ext in valid_extensions)


# Convenience functions for common validations
def validate_block_hash(block_hash: str) -> str:
    """Validate and return block hash, raise exception if invalid"""
    if not InputValidator.is_valid_block_hash(block_hash):
        raise ValueError(f"Invalid block hash: {block_hash}")
    return block_hash


def validate_block_height(height: Union[int, str]) -> int:
    """Validate and return block height, raise exception if invalid"""
    if not InputValidator.is_valid_block_height(height):
        raise ValueError(f"Invalid block height: {height}")
    return int(height)


def validate_bitcoin_address(address: str) -> str:
    """Validate and return Bitcoin address, raise exception if invalid"""
    if not InputValidator.is_valid_bitcoin_address(address):
        raise ValueError(f"Invalid Bitcoin address: {address}")
    return address


def validate_transaction_id(txid: str) -> str:
    """Validate and return transaction ID, raise exception if invalid"""
    if not InputValidator.is_valid_transaction_id(txid):
        raise ValueError(f"Invalid transaction ID: {txid}")
    return txid
