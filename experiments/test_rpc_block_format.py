"""
Experiment script to test real RPC block data format.
This will help identify any format mismatches in transaction detection.
"""

import asyncio
import aiohttp
import json

RPC_URL = "https://eth.llamarpc.com"

async def get_latest_block_with_txs():
    """Get a recent block that contains transactions."""
    async with aiohttp.ClientSession() as session:
        # First get current block number
        payload = {
            "jsonrpc": "2.0",
            "method": "eth_blockNumber",
            "params": [],
            "id": 1
        }
        async with session.post(RPC_URL, json=payload) as resp:
            result = await resp.json()
            current_block = int(result.get("result", "0x0"), 16)
            print(f"Current block: {current_block}")

        # Get a block with full transaction details
        # Try a few blocks back to ensure we get one with transactions
        for offset in range(0, 20):
            block_num = current_block - offset
            payload = {
                "jsonrpc": "2.0",
                "method": "eth_getBlockByNumber",
                "params": [hex(block_num), True],  # True = full transactions
                "id": 2
            }
            async with session.post(RPC_URL, json=payload) as resp:
                result = await resp.json()
                block = result.get("result")

                if block and block.get("transactions"):
                    txs = block["transactions"]
                    print(f"\nBlock {block_num} has {len(txs)} transactions")

                    # Show first few transactions to understand format
                    print("\nSample transactions:")
                    for i, tx in enumerate(txs[:3]):
                        print(f"\n--- Transaction {i+1} ---")
                        if isinstance(tx, dict):
                            print(f"  Type of tx: dict")
                            print(f"  hash: {tx.get('hash', 'N/A')}")
                            print(f"  from: {tx.get('from', 'N/A')}")
                            print(f"  to: {tx.get('to', 'N/A')}")
                            print(f"  value: {tx.get('value', 'N/A')}")
                            print(f"  Available keys: {list(tx.keys())}")
                        else:
                            print(f"  Type of tx: {type(tx)}")
                            print(f"  Value: {tx}")

                    return block

        print("Could not find a block with transactions")
        return None


async def simulate_detection(wallet_address: str = "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"):
    """Simulate the transaction detection for a known active wallet (vitalik.eth)."""
    print(f"\n{'='*70}")
    print(f"Simulating detection for wallet: {wallet_address[:20]}...")
    print(f"{'='*70}")

    addr_lower = wallet_address.lower()

    async with aiohttp.ClientSession() as session:
        # Get current block
        payload = {
            "jsonrpc": "2.0",
            "method": "eth_blockNumber",
            "params": [],
            "id": 1
        }
        async with session.post(RPC_URL, json=payload) as resp:
            result = await resp.json()
            current_block = int(result.get("result", "0x0"), 16)

        # Check last 50 blocks for any transactions involving this wallet
        found_in = 0
        found_out = 0

        for block_num in range(current_block - 50, current_block + 1):
            payload = {
                "jsonrpc": "2.0",
                "method": "eth_getBlockByNumber",
                "params": [hex(block_num), True],
                "id": 2
            }
            async with session.post(RPC_URL, json=payload) as resp:
                result = await resp.json()
                block = result.get("result")

                if not block or 'transactions' not in block:
                    continue

                for tx in block['transactions']:
                    if isinstance(tx, dict):
                        tx_from = tx.get('from', '').lower()
                        tx_to = tx.get('to', '').lower() if tx.get('to') else ''

                        if tx_from == addr_lower:
                            found_out += 1
                            print(f"Found OUTGOING tx in block {block_num}: {tx.get('hash', 'N/A')[:20]}...")
                        elif tx_to == addr_lower:
                            found_in += 1
                            print(f"Found INCOMING tx in block {block_num}: {tx.get('hash', 'N/A')[:20]}...")

        print(f"\nTotal found in last 50 blocks: {found_in} incoming, {found_out} outgoing")


async def main():
    print("Testing RPC block data format...")
    print("=" * 70)

    block = await get_latest_block_with_txs()

    if block:
        # Check if we can iterate transactions correctly
        print("\n" + "=" * 70)
        print("Testing iteration logic")
        print("=" * 70)

        txs = block.get('transactions', [])
        for i, tx in enumerate(txs[:5]):
            print(f"\nTransaction {i+1}:")
            if isinstance(tx, dict):
                tx_from = tx.get('from', '').lower()
                tx_to = tx.get('to', '').lower() if tx.get('to') else ''
                value_hex = tx.get('value', '0x0')
                value = int(value_hex, 16) / 1e18
                print(f"  isinstance(tx, dict) = True")
                print(f"  from: {tx_from}")
                print(f"  to: {tx_to}")
                print(f"  value: {value} ETH")
            else:
                print(f"  isinstance(tx, dict) = False")
                print(f"  Type: {type(tx)}")
                print("  ⚠️ This would be SKIPPED by current code!")

    # Also simulate actual detection
    await simulate_detection()


if __name__ == "__main__":
    asyncio.run(main())
