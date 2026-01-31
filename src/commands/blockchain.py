"""
Blockchain-related Bitcoin RPC commands
"""

import logging
from typing import Any, Dict, Optional, Union
from src.commands.validators import validate_block_hash, validate_block_height


class BlockchainCommands:
    """Handler for blockchain-related RPC commands"""
    
    def __init__(self, rpc_client):
        self.rpc_client = rpc_client
        self.logger = logging.getLogger(__name__)
    
    def get_blockchain_info(self) -> Dict[str, Any]:
        """Get blockchain information"""
        self.logger.debug("Executing getblockchaininfo")
        return self.rpc_client.call("getblockchaininfo")
    
    def get_block_count(self) -> int:
        """Get the current block count"""
        self.logger.debug("Executing getblockcount")
        return self.rpc_client.call("getblockcount")
    
    def get_block(self, block_hash: str, verbosity: int = 1) -> Union[str, Dict[str, Any]]:
        """
        Get block by hash
        
        Args:
            block_hash: The block hash
            verbosity: 0 = raw hex, 1 = block info, 2 = block info with transactions
        """
        # Validate block hash
        validated_hash = validate_block_hash(block_hash)
        
        self.logger.debug(f"Executing getblock for hash: {validated_hash}")
        return self.rpc_client.call("getblock", [validated_hash, verbosity])
    
    def get_block_hash(self, height: Union[int, str]) -> str:
        """Get block hash by height"""
        # Validate block height
        validated_height = validate_block_height(height)
        
        self.logger.debug(f"Executing getblockhash for height: {validated_height}")
        return self.rpc_client.call("getblockhash", [validated_height])
    
    def get_best_block_hash(self) -> str:
        """Get the hash of the best (tip) block"""
        self.logger.debug("Executing getbestblockhash")
        return self.rpc_client.call("getbestblockhash")
    
    def get_block_header(self, block_hash: str, verbose: bool = True) -> Union[str, Dict[str, Any]]:
        """
        Get block header by hash
        
        Args:
            block_hash: The block hash
            verbose: If false, return hex-encoded data
        """
        validated_hash = validate_block_hash(block_hash)
        
        self.logger.debug(f"Executing getblockheader for hash: {validated_hash}")
        return self.rpc_client.call("getblockheader", [validated_hash, verbose])
    
    def get_chain_tips(self) -> list:
        """Get information about all known tips in the block tree"""
        self.logger.debug("Executing getchaintips")
        return self.rpc_client.call("getchaintips")
    
    def get_difficulty(self) -> float:
        """Get the proof-of-work difficulty"""
        self.logger.debug("Executing getdifficulty")
        return self.rpc_client.call("getdifficulty")
    
    def get_mempool_info(self) -> Dict[str, Any]:
        """Get mempool information"""
        self.logger.debug("Executing getmempoolinfo")
        return self.rpc_client.call("getmempoolinfo")
    
    def get_raw_mempool(self, verbose: bool = False) -> Union[list, Dict[str, Any]]:
        """
        Get raw mempool
        
        Args:
            verbose: If true, return verbose information about each transaction
        """
        self.logger.debug("Executing getrawmempool")
        return self.rpc_client.call("getrawmempool", [verbose])
    
    def get_tx_out_set_info(self) -> Dict[str, Any]:
        """Get statistics about the unspent transaction output set"""
        self.logger.debug("Executing gettxoutsetinfo")
        return self.rpc_client.call("gettxoutsetinfo")
    
    def verify_chain(self, check_level: int = 3, num_blocks: int = 6) -> bool:
        """
        Verify blockchain database
        
        Args:
            check_level: How thorough the block verification is (0-4)
            num_blocks: The number of blocks to check
        """
        self.logger.debug(f"Executing verifychain with level {check_level}, blocks {num_blocks}")
        return self.rpc_client.call("verifychain", [check_level, num_blocks])
