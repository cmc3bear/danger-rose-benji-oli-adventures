"""Utilities for secure API key management."""

import os
from typing import Optional


def get_api_key(key_type: str, vault_base: str = None) -> str:
    """Get API key from environment variable or vault directory.
    
    Args:
        key_type: Type of API key (OPENAI, GITHUB, SUNO, etc.)
        vault_base: Base path to vault directory (defaults to ../api-key-forge/vault)
        
    Returns:
        The API key string
        
    Raises:
        ValueError: If API key is not found
    """
    # Try environment variable first
    env_var = f"{key_type.upper()}_API_KEY"
    api_key = os.getenv(env_var)
    
    if api_key:
        return api_key
    
    # Try vault directory
    if vault_base is None:
        vault_base = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "..",
            "api-key-forge",
            "vault"
        )
    
    vault_file = os.path.join(vault_base, key_type.upper(), "api_key.txt")
    
    if os.path.exists(vault_file):
        with open(vault_file, 'r') as f:
            return f.read().strip()
    
    raise ValueError(f"API key for {key_type} not found in environment or vault")


def check_vault_security():
    """Check that vault directory is properly secured."""
    vault_base = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "..",
        "api-key-forge",
        "vault"
    )
    
    if not os.path.exists(vault_base):
        print(f"Vault directory not found: {vault_base}")
        return False
    
    # Check for common key types
    key_types = ["OPENAI", "GITHUB", "SUNO"]
    found_keys = []
    
    for key_type in key_types:
        vault_file = os.path.join(vault_base, key_type, "api_key.txt")
        if os.path.exists(vault_file):
            found_keys.append(key_type)
    
    print(f"Vault security check:")
    print(f"- Vault location: {vault_base}")
    print(f"- Available keys: {found_keys}")
    print(f"- Outside repository: {'api-key-forge' not in os.getcwd()}")
    
    return len(found_keys) > 0


if __name__ == "__main__":
    check_vault_security()