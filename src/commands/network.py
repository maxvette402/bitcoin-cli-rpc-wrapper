"""
Network-related Bitcoin RPC commands
"""

import logging
from typing import Any, Dict, List, Optional, Union


class NetworkCommands:
    """Handler for network-related RPC commands"""
    
    def __init__(self, rpc_client):
        self.rpc_client = rpc_client
        self.logger = logging.getLogger(__name__)
    
    def get_network_info(self) -> Dict[str, Any]:
        """Get network information"""
        self.logger.debug("Executing getnetworkinfo")
        return self.rpc_client.call("getnetworkinfo")
    
    def get_peer_info(self) -> List[Dict[str, Any]]:
        """Get information about connected peers"""
        self.logger.debug("Executing getpeerinfo")
        return self.rpc_client.call("getpeerinfo")
    
    def get_connection_count(self) -> int:
        """Get the number of connections to other nodes"""
        self.logger.debug("Executing getconnectioncount")
        return self.rpc_client.call("getconnectioncount")
    
    def add_node(self, node: str, command: str = "add") -> None:
        """
        Add, remove, or try a connection to a node
        
        Args:
            node: The node address (IP:port or hostname:port)
            command: 'add', 'remove', or 'onetry'
        """
        if command not in ["add", "remove", "onetry"]:
            raise ValueError("Command must be 'add', 'remove', or 'onetry'")
        
        self.logger.debug(f"Executing addnode: {node}, command: {command}")
        return self.rpc_client.call("addnode", [node, command])
    
    def disconnect_node(self, address: Optional[str] = None, node_id: Optional[int] = None) -> None:
        """
        Disconnect from a node
        
        Args:
            address: The IP address and port of the node
            node_id: The node ID (as shown in getpeerinfo)
        """
        if address is None and node_id is None:
            raise ValueError("Either address or node_id must be specified")
        
        if address is not None and node_id is not None:
            raise ValueError("Cannot specify both address and node_id")
        
        if address:
            self.logger.debug(f"Executing disconnectnode by address: {address}")
            return self.rpc_client.call("disconnectnode", [address])
        else:
            self.logger.debug(f"Executing disconnectnode by id: {node_id}")
            return self.rpc_client.call("disconnectnode", ["", node_id])
    
    def get_added_node_info(self, node: Optional[str] = None) -> Union[List[Dict[str, Any]], Dict[str, Any]]:
        """
        Get information about added nodes
        
        Args:
            node: If specified, return info for this node only
        """
        if node:
            self.logger.debug(f"Executing getaddednodeinfo for node: {node}")
            return self.rpc_client.call("getaddednodeinfo", [node])
        else:
            self.logger.debug("Executing getaddednodeinfo for all nodes")
            return self.rpc_client.call("getaddednodeinfo")
    
    def get_net_totals(self) -> Dict[str, Any]:
        """Get network traffic information"""
        self.logger.debug("Executing getnettotals")
        return self.rpc_client.call("getnettotals")
    
    def list_banned(self) -> List[Dict[str, Any]]:
        """List all banned IPs/subnets"""
        self.logger.debug("Executing listbanned")
        return self.rpc_client.call("listbanned")
    
    def set_ban(self, subnet: str, command: str = "add", ban_time: Optional[int] = None, absolute: bool = False) -> None:
        """
        Add or remove an IP/subnet from the banned list
        
        Args:
            subnet: The IP/subnet to ban (with optional netmask)
            command: 'add' or 'remove'
            ban_time: Time in seconds how long the ban should last
            absolute: If true, ban_time is an absolute timestamp
        """
        if command not in ["add", "remove"]:
            raise ValueError("Command must be 'add' or 'remove'")
        
        params = [subnet, command]
        if ban_time is not None:
            params.append(ban_time)
            if absolute:
                params.append(absolute)
        
        self.logger.debug(f"Executing setban: {subnet}, command: {command}")
        return self.rpc_client.call("setban", params)
    
    def clear_banned(self) -> None:
        """Clear all banned IPs"""
        self.logger.debug("Executing clearbanned")
        return self.rpc_client.call("clearbanned")
    
    def ping(self) -> None:
        """Send a ping to all connected nodes"""
        self.logger.debug("Executing ping")
        return self.rpc_client.call("ping")
    
    def get_node_addresses(self, count: int = 1) -> List[Dict[str, Any]]:
        """
        Get node addresses from the address manager
        
        Args:
            count: How many addresses to return
        """
        if count < 1:
            raise ValueError("Count must be at least 1")
        
        self.logger.debug(f"Executing getnodeaddresses, count: {count}")
        return self.rpc_client.call("getnodeaddresses", [count])
    
    def set_network_active(self, state: bool) -> bool:
        """
        Enable/disable all P2P network activity
        
        Args:
            state: True to enable networking, False to disable
        """
        self.logger.debug(f"Executing setnetworkactive: {state}")
        return self.rpc_client.call("setnetworkactive", [state])
    
    def submit_block(self, hex_data: str) -> Optional[str]:
        """
        Submit a new block to the network
        
        Args:
            hex_data: The hex-encoded block data
        """
        if not hex_data or not isinstance(hex_data, str):
            raise ValueError("hex_data must be a non-empty string")
        
        # Basic hex validation
        try:
            int(hex_data, 16)
        except ValueError:
            raise ValueError("hex_data must be valid hexadecimal")
        
        self.logger.debug("Executing submitblock")
        return self.rpc_client.call("submitblock", [hex_data])
    
    def get_mining_info(self) -> Dict[str, Any]:
        """Get mining-related information"""
        self.logger.debug("Executing getmininginfo")
        return self.rpc_client.call("getmininginfo")
    
    def get_block_template(self, template_request: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Get block template for mining
        
        Args:
            template_request: Template request parameters
        """
        params = [template_request] if template_request else []
        
        self.logger.debug("Executing getblocktemplate")
        return self.rpc_client.call("getblocktemplate", params)
    
    def submit_header(self, hex_data: str) -> Optional[str]:
        """
        Submit a block header
        
        Args:
            hex_data: The hex-encoded block header data
        """
        if not hex_data or not isinstance(hex_data, str):
            raise ValueError("hex_data must be a non-empty string")
        
        # Basic hex validation
        try:
            int(hex_data, 16)
        except ValueError:
            raise ValueError("hex_data must be valid hexadecimal")
        
        self.logger.debug("Executing submitheader")
        return self.rpc_client.call("submitheader", [hex_data])
