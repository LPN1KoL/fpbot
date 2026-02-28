"""
Test the exact transaction detection flow from main.py
"""

import asyncio
import aiohttp
import json

# Simulate the exact code from main.py

async def simulate_get_transactions():
    """Simulate the get_transactions function logic."""

    # Use a well-known wallet address that has recent transactions
    # Vitalik's address: 0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045
    test_wallet = "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"
    addr_lower = test_wallet.lower()

    RPC_URL = "https://eth.llamarpc.com"

    async with aiohttp.ClientSession() as session:
        # Get current block
        payload = {"jsonrpc": "2.0", "method": "eth_blockNumber", "params": [], "id": 1}
        async with session.post(RPC_URL, json=payload, timeout=30) as resp:
            result = await resp.json()
            current_block = int(result.get("result", "0x0"), 16)

        print(f"Current block: {current_block}")
        print(f"Checking wallet: {test_wallet}")
        print(f"addr_lower: {addr_lower}")
        print()

        # Simulate checking 10 recent blocks
        txs = []
        blocks_to_check = 10

        for i in range(blocks_to_check):
            block_num = current_block - i
            payload = {
                "jsonrpc": "2.0",
                "method": "eth_getBlockByNumber",
                "params": [hex(block_num), True],
                "id": 2
            }

            try:
                async with session.post(RPC_URL, json=payload, timeout=30) as resp:
                    result = await resp.json()
                    block = result.get("result")

                if not block or 'transactions' not in block:
                    print(f"Block {block_num}: No transactions or block not found")
                    continue

                block_txs = block['transactions']
                print(f"Block {block_num}: {len(block_txs)} transactions")

                # Exact logic from main.py lines 363-378
                for tx in block_txs:
                    if isinstance(tx, dict):
                        tx_hash = tx.get('hash', '')
                        tx_from = tx.get('from', '').lower()
                        tx_to = tx.get('to', '').lower() if tx.get('to') else ''

                        # Debug: Check if this transaction involves our wallet
                        if tx_from == addr_lower or tx_to == addr_lower:
                            value = int(tx.get('value', '0x0'), 16) / 1e18
                            tx_type = 'out' if tx_from == addr_lower else 'in'

                            print(f"  MATCH! {tx_type.upper()}: {value:.6f} ETH")
                            print(f"    from: {tx_from}")
                            print(f"    to:   {tx_to}")
                            print(f"    hash: {tx_hash}")

                            txs.append({
                                'hash': tx_hash,
                                'from': tx_from,
                                'to': tx_to,
                                'value': value,
                                'block': block_num,
                                'type': tx_type
                            })

            except Exception as e:
                print(f"Block {block_num}: Error - {e}")

        print()
        print("=" * 60)
        print(f"Summary: Found {len(txs)} transactions")
        in_count = sum(1 for tx in txs if tx['type'] == 'in')
        out_count = sum(1 for tx in txs if tx['type'] == 'out')
        print(f"  Incoming: {in_count}")
        print(f"  Outgoing: {out_count}")

        return txs


if __name__ == "__main__":
    asyncio.run(simulate_get_transactions())
