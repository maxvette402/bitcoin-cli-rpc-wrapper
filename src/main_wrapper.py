#!/usr/bin/env python3
"""
Bitcoin CLI Wrapper - Main Entry Point
Secure Bitcoin RPC client with CLI interface
"""

import argparse
import json
import sys
import logging
from pathlib import Path

# Add lib directory to path
sys.path.insert(0, str(Path(__file__).parent / 'lib'))

from config import Config
from rpc_client import BitcoinRPCClient
from src.commands.blockchain import BlockchainCommands
from src.commands.wallet import WalletCommands
from src.commands.network import NetworkCommands

# Command mapping - easily extensible
COMMAND_MAP = {
    # Blockchain commands
    'getblockchaininfo': ('blockchain', 'get_blockchain_info'),
    'getblockcount': ('blockchain', 'get_block_count'),
    'getblock': ('blockchain', 'get_block'),
    'getblockhash': ('blockchain', 'get_block_hash'),
    'getbestblockhash': ('blockchain', 'get_best_block_hash'),
    
    # Network commands
    'getnetworkinfo': ('network', 'get_network_info'),
    'getpeerinfo': ('network', 'get_peer_info'),
    'getconnectioncount': ('network', 'get_connection_count'),
    
    # Wallet commands
    'getwalletinfo': ('wallet', 'get_wallet_info'),
    'getbalance': ('wallet', 'get_balance'),
    'getnewaddress': ('wallet', 'get_new_address'),
}

COMMAND_MODULES = {
    'blockchain': BlockchainCommands,
    'wallet': WalletCommands,
    'network': NetworkCommands,
}


def setup_logging(config):
    """Setup logging based on configuration"""
    log_level = getattr(logging, config.log_level.upper())
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Setup root logger
    logger = logging.getLogger()
    logger.setLevel(log_level)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler if specified
    if config.log_file:
        file_handler = logging.FileHandler(config.log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)


def create_parser():
    """Create argument parser"""
    parser = argparse.ArgumentParser(
        description='Bitcoin CLI Wrapper - Secure RPC client',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Available commands:
  getblockchaininfo          Get blockchain information
  getblockcount             Get current block count
  getblock <hash>           Get block by hash
  getblockhash <height>     Get block hash by height
  getbestblockhash          Get best block hash
  getnetworkinfo            Get network information
  getpeerinfo               Get peer information
  getconnectioncount        Get connection count
  getwalletinfo             Get wallet information
  getbalance                Get wallet balance
  getnewaddress             Get new address

Examples:
  python3 bitcoin_cli_wrapper.py getblockchaininfo
  python3 bitcoin_cli_wrapper.py getblock 000000000019d6689c085ae165831e934ff763ae46a2a6c172b3f1b60a8ce26f
  python3 bitcoin_cli_wrapper.py getblockhash 100
        """
    )
    
    parser.add_argument(
        'command',
        help='Bitcoin RPC command to execute'
    )
    
    parser.add_argument(
        'params',
        nargs='*',
        help='Parameters for the command'
    )
    
    parser.add_argument(
        '--config',
        default='.env',
        help='Configuration file path (default: .env)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    
    return parser


def execute_command(rpc_client, command, params):
    """Execute a Bitcoin RPC command"""
    logger = logging.getLogger(__name__)
    
    if command not in COMMAND_MAP:
        available_commands = ', '.join(sorted(COMMAND_MAP.keys()))
        return {
            "success": False,
            "error": f"Unknown command: {command}. Available commands: {available_commands}",
            "error_code": "UNKNOWN_COMMAND"
        }
    
    module_name, method_name = COMMAND_MAP[command]
    
    try:
        # Get the command module
        module_class = COMMAND_MODULES[module_name]
        command_handler = module_class(rpc_client)
        
        # Get the method
        method = getattr(command_handler, method_name)
        
        # Execute the command
        logger.info(f"Executing command: {command} with params: {params}")
        result = method(*params)
        
        logger.info(f"Command executed successfully: {command}")
        return {
            "success": True,
            "data": result,
            "command": command,
            "params": params
        }
        
    except AttributeError as e:
        logger.error(f"Command method not found: {e}")
        return {
            "success": False,
            "error": f"Command implementation not found: {command}",
            "error_code": "IMPLEMENTATION_ERROR"
        }
    
    except Exception as e:
        logger.error(f"Command execution failed: {e}")
        # Return original Bitcoin Core error for transparency
        return {
            "success": False,
            "error": str(e),
            "error_code": "RPC_ERROR",
            "command": command,
            "params": params
        }


def main():
    """Main entry point"""
    parser = create_parser()
    args = parser.parse_args()
    
    try:
        # Load configuration
        config = Config(args.config)
        
        # Override log level if verbose
        if args.verbose:
            config.log_level = 'DEBUG'
        
        # Setup logging
        setup_logging(config)
        logger = logging.getLogger(__name__)
        
        logger.info("Bitcoin CLI Wrapper starting...")
        logger.debug(f"Configuration loaded from: {args.config}")
        
        # Create RPC client
        rpc_client = BitcoinRPCClient(config)
        
        # Test connection
        logger.debug("Testing RPC connection...")
        rpc_client.test_connection()
        logger.info("RPC connection successful")
        
        # Execute command
        result = execute_command(rpc_client, args.command, args.params)
        
        # Output result as JSON
        print(json.dumps(result, indent=2, sort_keys=True))
        
        # Exit with appropriate code
        sys.exit(0 if result.get("success", False) else 1)
        
    except Exception as e:
        # Handle fatal errors
        error_result = {
            "success": False,
            "error": str(e),
            "error_code": "FATAL_ERROR"
        }
        print(json.dumps(error_result, indent=2))
        sys.exit(1)


if __name__ == "__main__":
    main()
