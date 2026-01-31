"""
Wallet-related Bitcoin RPC commands
"""

import logging
from typing import Any, Dict, List, Optional, Union
from src.commands.validators import validate_bitcoin_address, validate_transaction_id


class WalletCommands:
    """Handler for wallet-related RPC commands"""
    
    def __init__(self, rpc_client):
        self.rpc_client = rpc_client
        self.logger = logging.getLogger(__name__)
    
    def get_wallet_info(self) -> Dict[str, Any]:
        """Get wallet information"""
        self.logger.debug("Executing getwalletinfo")
        return self.rpc_client.call("getwalletinfo")
    
    def get_balance(self, account: str = "*", min_conf: int = 1, include_watchonly: bool = False) -> float:
        """
        Get wallet balance
        
        Args:
            account: Account name (deprecated in newer versions)
            min_conf: Minimum confirmations
            include_watchonly: Include watchonly addresses
        """
        self.logger.debug(f"Executing getbalance for account: {account}")
        
        # For newer Bitcoin Core versions, use simpler call
        try:
            return self.rpc_client.call("getbalance")
        except Exception:
            # Fallback for older versions
            return self.rpc_client.call("getbalance", [account, min_conf, include_watchonly])
    
    def get_new_address(self, label: str = "", address_type: Optional[str] = None) -> str:
        """
        Get a new address
        
        Args:
            label: Label for the address
            address_type: Address type (legacy, p2sh-segwit, bech32)
        """
        self.logger.debug(f"Executing getnewaddress with label: {label}")
        
        params = []
        if label:
            params.append(label)
        if address_type:
            if len(params) == 0:
                params.append("")  # Empty label
            params.append(address_type)
        
        return self.rpc_client.call("getnewaddress", params if params else None)
    
    def get_address_info(self, address: str) -> Dict[str, Any]:
        """Get information about an address"""
        validated_address = validate_bitcoin_address(address)
        
        self.logger.debug(f"Executing getaddressinfo for: {validated_address}")
        return self.rpc_client.call("getaddressinfo", [validated_address])
    
    def list_addresses(self) -> List[Dict[str, Any]]:
        """List all addresses in the wallet"""
        self.logger.debug("Executing listaddresses")
        return self.rpc_client.call("listaddresses")
    
    def get_received_by_address(self, address: str, min_conf: int = 1) -> float:
        """
        Get amount received by address
        
        Args:
            address: Bitcoin address
            min_conf: Minimum confirmations
        """
        validated_address = validate_bitcoin_address(address)
        
        self.logger.debug(f"Executing getreceivedbyaddress for: {validated_address}")
        return self.rpc_client.call("getreceivedbyaddress", [validated_address, min_conf])
    
    def list_transactions(self, account: str = "*", count: int = 10, skip: int = 0, include_watchonly: bool = False) -> List[Dict[str, Any]]:
        """
        List wallet transactions
        
        Args:
            account: Account name (deprecated)
            count: Number of transactions to return
            skip: Number of transactions to skip
            include_watchonly: Include watchonly addresses
        """
        self.logger.debug(f"Executing listtransactions, count: {count}, skip: {skip}")
        
        # For newer Bitcoin Core versions
        try:
            return self.rpc_client.call("listtransactions", ["*", count, skip, include_watchonly])
        except Exception:
            # Fallback for older versions
            return self.rpc_client.call("listtransactions", [account, count, skip, include_watchonly])
    
    def get_transaction(self, txid: str, include_watchonly: bool = False) -> Dict[str, Any]:
        """
        Get transaction details
        
        Args:
            txid: Transaction ID
            include_watchonly: Include watchonly addresses
        """
        validated_txid = validate_transaction_id(txid)
        
        self.logger.debug(f"Executing gettransaction for: {validated_txid}")
        return self.rpc_client.call("gettransaction", [validated_txid, include_watchonly])
    
    def send_to_address(self, address: str, amount: float, comment: str = "", comment_to: str = "", subtract_fee: bool = False) -> str:
        """
        Send amount to address
        
        Args:
            address: Destination address
            amount: Amount to send
            comment: Comment for transaction
            comment_to: Comment for recipient
            subtract_fee: Subtract fee from amount
        """
        validated_address = validate_bitcoin_address(address)
        
        if amount <= 0:
            raise ValueError("Amount must be positive")
        
        self.logger.debug(f"Executing sendtoaddress to: {validated_address}, amount: {amount}")
        
        params = [validated_address, amount]
        if comment:
            params.append(comment)
        if comment_to:
            if len(params) == 2:
                params.append("")  # Empty comment
            params.append(comment_to)
        if subtract_fee:
            while len(params) < 4:
                params.append("")
            params.append(subtract_fee)
        
        return self.rpc_client.call("sendtoaddress", params)
    
    def list_unspent(self, min_conf: int = 1, max_conf: int = 9999999, addresses: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        List unspent transaction outputs
        
        Args:
            min_conf: Minimum confirmations
            max_conf: Maximum confirmations
            addresses: Filter by addresses
        """
        self.logger.debug(f"Executing listunspent, min_conf: {min_conf}, max_conf: {max_conf}")
        
        params = [min_conf, max_conf]
        if addresses:
            # Validate addresses
            validated_addresses = [validate_bitcoin_address(addr) for addr in addresses]
            params.append(validated_addresses)
        
        return self.rpc_client.call("listunspent", params)
    
    def lock_unspent(self, unlock: bool, transactions: Optional[List[Dict[str, Any]]] = None) -> bool:
        """
        Lock or unlock unspent outputs
        
        Args:
            unlock: True to unlock, False to lock
            transactions: List of transaction outputs to lock/unlock
        """
        self.logger.debug(f"Executing lockunspent, unlock: {unlock}")
        
        params = [unlock]
        if transactions:
            params.append(transactions)
        
        return self.rpc_client.call("lockunspent", params)
    
    def list_lock_unspent(self) -> List[Dict[str, Any]]:
        """List locked unspent outputs"""
        self.logger.debug("Executing listlockunspent")
        return self.rpc_client.call("listlockunspent")
    
    def backup_wallet(self, destination: str) -> None:
        """
        Backup wallet to file
        
        Args:
            destination: Backup file path
        """
        self.logger.debug(f"Executing backupwallet to: {destination}")
        return self.rpc_client.call("backupwallet", [destination])
    
    def encrypt_wallet(self, passphrase: str) -> str:
        """
        Encrypt wallet with passphrase
        
        Args:
            passphrase: Wallet passphrase
        """
        if not passphrase or len(passphrase) < 8:
            raise ValueError("Passphrase must be at least 8 characters")
        
        self.logger.debug("Executing encryptwallet")
        return self.rpc_client.call("encryptwallet", [passphrase])
    
    def wallet_passphrase(self, passphrase: str, timeout: int = 60) -> None:
        """
        Unlock wallet for a period of time
        
        Args:
            passphrase: Wallet passphrase
            timeout: Timeout in seconds
        """
        self.logger.debug(f"Executing walletpassphrase, timeout: {timeout}")
        return self.rpc_client.call("walletpassphrase", [passphrase, timeout])
    
    def wallet_lock(self) -> None:
        """Lock the wallet"""
        self.logger.debug("Executing walletlock")
        return self.rpc_client.call("walletlock")
