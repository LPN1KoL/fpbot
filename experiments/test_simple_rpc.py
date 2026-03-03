"""
Simple test to verify RPC data format for transactions.
"""

import requests
import json

# Using a simple synchronous request for quick testing
RPC_URL = "https://eth.llamarpc.com"

def get_block(block_num):
    """Get a block with full transaction details."""
    payload = {
        "jsonrpc": "2.0",
        "method": "eth_getBlockByNumber",
        "params": [hex(block_num), True],  # True = full transactions
        "id": 1
    }
    response = requests.post(RPC_URL, json=payload, timeout=30)
    result = response.json()
    return result.get("result")

def main():
    # Get current block
    payload = {
        "jsonrpc": "2.0",
        "method": "eth_blockNumber",
        "params": [],
        "id": 1
    }
    response = requests.post(RPC_URL, json=payload, timeout=30)
    current_block = int(response.json().get("result", "0x0"), 16)
    print(f"Current block: {current_block}")

    # Get a recent block
    block = get_block(current_block - 5)
    if not block:
        print("Failed to get block")
        return

    txs = block.get('transactions', [])
    print(f"Block has {len(txs)} transactions")

    if not txs:
        print("No transactions in block")
        return

    # Check first transaction structure
    tx = txs[0]
    print(f"\nFirst transaction type: {type(tx)}")

    if isinstance(tx, dict):
        print("Transaction fields:")
        for key in ['hash', 'from', 'to', 'value']:
            value = tx.get(key)
            print(f"  {key}: {type(value).__name__} = {str(value)[:40]}...")
    else:
        print(f"Transaction is not a dict: {tx}")

if __name__ == "__main__":
    main()
