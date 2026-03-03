"""
Test if aiohttp accepts timeout as integer.
"""

import asyncio
import aiohttp

async def test():
    async with aiohttp.ClientSession() as session:
        # Test with integer timeout (like main.py does)
        try:
            async with session.get("https://httpbin.org/delay/1", timeout=10) as resp:
                print(f"Integer timeout: Response status {resp.status}")
        except Exception as e:
            print(f"Integer timeout failed: {e}")

        # Test with ClientTimeout
        try:
            timeout = aiohttp.ClientTimeout(total=10)
            async with session.get("https://httpbin.org/delay/1", timeout=timeout) as resp:
                print(f"ClientTimeout: Response status {resp.status}")
        except Exception as e:
            print(f"ClientTimeout failed: {e}")

asyncio.run(test())
