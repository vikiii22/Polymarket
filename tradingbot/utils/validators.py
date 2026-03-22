"""Validation functions for configuration and inputs."""

import re
from typing import Tuple


def validate_private_key(private_key: str | None) -> Tuple[bool, str]:
    """
    Validate that a private key is a valid Ethereum private key (64 hexadecimal characters).
    
    Args:
        private_key: The private key string to validate. Can be None.
        
    Returns:
        Tuple of (is_valid, message):
            - is_valid: True if the key is valid, False otherwise
            - message: Description of validation result
            
    Examples:
        >>> validate_private_key("a" * 64)
        (True, "Valid private key")
        
        >>> validate_private_key("0x" + "a" * 64)
        (True, "Valid private key")
        
        >>> validate_private_key("not-a-hex-key")
        (False, "Private key must be 64 hexadecimal characters (optionally prefixed with 0x)")
        
        >>> validate_private_key(None)
        (False, "Private key is empty or not provided")
    """
    if not private_key:
        return False, "Private key is empty or not provided"
    
    # Remove 0x prefix if present
    key = private_key.strip()
    if key.startswith("0x") or key.startswith("0X"):
        key = key[2:]
    
    # Check if it's exactly 64 hexadecimal characters
    hex_pattern = re.compile(r"^[0-9a-fA-F]{64}$")
    
    if not hex_pattern.match(key):
        # Provide specific error messages for common mistakes
        if len(key) != 64:
            return False, f"Private key must be exactly 64 characters (found {len(key)} characters)"
        elif not all(c in "0123456789abcdefABCDEF" for c in key):
            # Check for common UUID format (contains hyphens)
            if "-" in key:
                return False, (
                    "Private key contains hyphens (-). "
                    "It looks like a UUID, but Ethereum private keys must be pure hexadecimal. "
                    "Remove all hyphens or use a valid Ethereum private key."
                )
            else:
                return False, "Private key must contain only hexadecimal characters (0-9, a-f, A-F)"
        else:
            return False, "Private key must be 64 hexadecimal characters (optionally prefixed with 0x)"
    
    return True, "Valid private key"


def validate_hex_address(address: str | None) -> Tuple[bool, str]:
    """
    Validate that an address is a valid Ethereum address (40 hex characters).
    
    Args:
        address: The address string to validate
        
    Returns:
        Tuple of (is_valid, message)
    """
    if not address:
        return False, "Address is empty"
    
    addr = address.strip()
    if addr.startswith("0x"):
        addr = addr[2:]
    
    if not re.match(r"^[0-9a-fA-F]{40}$", addr):
        return False, f"Invalid Ethereum address format (expected 40 hex chars, got {len(addr)})"
    
    return True, "Valid address"
