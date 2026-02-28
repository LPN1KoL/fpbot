"""
Experiment script to test transaction detection logic.
This script simulates the transaction detection to identify why
incoming transactions might not be detected properly.
"""

# Simulating the transaction detection logic from main.py

def detect_transaction_type(tx_from: str, tx_to: str, wallet_address: str) -> str:
    """
    Detect if a transaction is incoming or outgoing for a given wallet.

    Args:
        tx_from: The sender address (lowercased)
        tx_to: The receiver address (lowercased)
        wallet_address: The wallet we're monitoring (lowercased)

    Returns:
        'in' for incoming, 'out' for outgoing, 'none' if not related
    """
    addr_lower = wallet_address.lower()
    tx_from_lower = tx_from.lower()
    tx_to_lower = tx_to.lower()

    # Current logic from main.py (line 377)
    if tx_from_lower == addr_lower or tx_to_lower == addr_lower:
        return 'out' if tx_from_lower == addr_lower else 'in'
    return 'none'


def test_detection():
    """Test various transaction scenarios."""
    wallet = "0x1234567890abcdef1234567890abcdef12345678"
    other_wallet = "0xaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"

    test_cases = [
        # (from, to, description, expected)
        (wallet, other_wallet, "Outgoing: wallet sends to other", "out"),
        (other_wallet, wallet, "Incoming: other sends to wallet", "in"),
        (wallet, wallet, "Self-transfer: wallet to itself", "out"),  # This is detected as 'out'
        (other_wallet, "0xbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb", "Unrelated: other to other", "none"),
    ]

    print("=" * 70)
    print("Testing transaction detection logic")
    print("=" * 70)
    print(f"Monitored wallet: {wallet}")
    print()

    all_passed = True
    for tx_from, tx_to, description, expected in test_cases:
        result = detect_transaction_type(tx_from, tx_to, wallet)
        status = "✅ PASS" if result == expected else "❌ FAIL"
        if result != expected:
            all_passed = False
        print(f"{status} | {description}")
        print(f"       From: {tx_from[:10]}... To: {tx_to[:10]}...")
        print(f"       Expected: {expected}, Got: {result}")
        print()

    return all_passed


def test_filter_logic():
    """Test the notification filter logic."""
    print("=" * 70)
    print("Testing notification filter logic")
    print("=" * 70)

    # Simulating the filter from main.py (lines 715-721)
    def filter_transactions(txs, notify_incoming, notify_outgoing):
        return [
            tx for tx in txs
            if (tx['type'] == 'in' and notify_incoming) or
               (tx['type'] == 'out' and notify_outgoing)
        ]

    # Test transactions
    txs = [
        {'hash': 'tx1', 'type': 'in', 'value': 1.0},
        {'hash': 'tx2', 'type': 'out', 'value': 2.0},
        {'hash': 'tx3', 'type': 'in', 'value': 3.0},
        {'hash': 'tx4', 'type': 'out', 'value': 4.0},
    ]

    test_cases = [
        # (notify_incoming, notify_outgoing, expected_types)
        (True, True, ['in', 'out', 'in', 'out']),
        (True, False, ['in', 'in']),
        (False, True, ['out', 'out']),
        (False, False, []),
    ]

    all_passed = True
    for notify_in, notify_out, expected_types in test_cases:
        result = filter_transactions(txs, notify_in, notify_out)
        result_types = [tx['type'] for tx in result]
        status = "✅ PASS" if result_types == expected_types else "❌ FAIL"
        if result_types != expected_types:
            all_passed = False
        print(f"{status} | notify_incoming={notify_in}, notify_outgoing={notify_out}")
        print(f"       Expected types: {expected_types}")
        print(f"       Got types:      {result_types}")
        print()

    return all_passed


if __name__ == "__main__":
    detection_passed = test_detection()
    filter_passed = test_filter_logic()

    print("=" * 70)
    print("Summary")
    print("=" * 70)
    print(f"Transaction detection: {'✅ All tests passed' if detection_passed else '❌ Some tests failed'}")
    print(f"Filter logic:          {'✅ All tests passed' if filter_passed else '❌ Some tests failed'}")
    print()

    if detection_passed and filter_passed:
        print("The basic logic appears correct. The issue might be elsewhere:")
        print("1. RPC data format mismatch")
        print("2. Address case sensitivity issues")
        print("3. Block data not containing expected fields")
        print("4. Timing/race condition issues")
