"""
Test TRON API to verify address format in transactions.
"""

import requests
import json

TRON_API = "https://api.trongrid.io"

def test_tron_block():
    """Test TRON block data to verify address formats."""

    # Get current block
    response = requests.post(f"{TRON_API}/wallet/getnowblock", json={}, timeout=30)
    current_block = response.json()

    block_num = current_block['block_header']['raw_data']['number']
    print(f"Current TRON block: {block_num}")

    # Get block with visible=True (should return Base58 addresses)
    response = requests.post(
        f"{TRON_API}/wallet/getblockbynum",
        json={'num': block_num - 10, 'visible': True},  # A slightly older block for stability
        timeout=30
    )
    block = response.json()

    txs = block.get('transactions', [])
    print(f"Block has {len(txs)} transactions")

    # Look at TransferContract transactions
    transfer_count = 0
    for tx in txs:
        if 'raw_data' not in tx:
            continue

        for contract in tx['raw_data'].get('contract', []):
            if contract.get('type') == 'TransferContract':
                transfer_count += 1
                if transfer_count <= 3:  # Show first 3
                    value = contract['parameter']['value']
                    owner = value.get('owner_address', 'N/A')
                    to = value.get('to_address', 'N/A')
                    amount = value.get('amount', 0) / 1_000_000

                    print(f"\nTransfer #{transfer_count}:")
                    print(f"  owner_address: {owner}")
                    print(f"  to_address:    {to}")
                    print(f"  amount:        {amount} TRX")
                    print(f"  owner starts with 'T': {str(owner).startswith('T')}")
                    print(f"  to starts with 'T':    {str(to).startswith('T')}")

    print(f"\nTotal TransferContract transactions: {transfer_count}")

    # Also test without visible=True to see the difference
    print("\n" + "=" * 60)
    print("Testing WITHOUT visible=True:")

    response = requests.post(
        f"{TRON_API}/wallet/getblockbynum",
        json={'num': block_num - 10},  # Without visible
        timeout=30
    )
    block_no_visible = response.json()

    for tx in block_no_visible.get('transactions', [])[:1]:
        if 'raw_data' not in tx:
            continue
        for contract in tx['raw_data'].get('contract', []):
            if contract.get('type') == 'TransferContract':
                value = contract['parameter']['value']
                owner = value.get('owner_address', 'N/A')
                to = value.get('to_address', 'N/A')

                print(f"  owner_address (hex): {owner}")
                print(f"  to_address (hex):    {to}")
                break


if __name__ == "__main__":
    test_tron_block()
