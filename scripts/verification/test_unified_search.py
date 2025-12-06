#!/usr/bin/env python3
"""Test script for unified search service."""
import httpx
import asyncio
import json

async def test_unified_search():
    """Test unified search endpoint."""
    async with httpx.AsyncClient(timeout=10.0) as client:
        # Test 1: Search for Los Angeles
        print("=== Test 1: Unified Search for Los Angeles ===")
        response = await client.get(
            "http://localhost:8007/search",
            params={
                "city": "Los Angeles",
                "page": 1,
                "page_size": 10
            }
        )
        print(f"Status: {response.status_code}")
        data = response.json()
        print(f"Flights: {len(data.get('flights', []))}")
        print(f"Hotels: {len(data.get('hotels', []))}")
        print(f"Cars: {len(data.get('cars', []))}")
        print(f"Total Results: {data.get('total_results', 0)}")
        print(f"Response keys: {list(data.keys())}")
        print()
        
        # Test 2: Check cache
        print("=== Test 2: Second Request (Should Hit Cache) ===")
        response2 = await client.get(
            "http://localhost:8007/search",
            params={
                "city": "Los Angeles",
                "page": 1,
                "page_size": 10
            }
        )
        print(f"Status: {response2.status_code}")
        data2 = response2.json()
        print(f"Flights: {len(data2.get('flights', []))}")
        print(f"Hotels: {len(data2.get('hotels', []))}")
        print(f"Cars: {len(data2.get('cars', []))}")
        print()
        
        # Test 3: Search with San Francisco
        print("=== Test 3: Unified Search for San Francisco ===")
        response3 = await client.get(
            "http://localhost:8007/search",
            params={
                "city": "San Francisco",
                "page": 1,
                "page_size": 10
            }
        )
        print(f"Status: {response3.status_code}")
        data3 = response3.json()
        print(f"Flights: {len(data3.get('flights', []))}")
        print(f"Hotels: {len(data3.get('hotels', []))}")
        print(f"Cars: {len(data3.get('cars', []))}")
        print(f"Total Results: {data3.get('total_results', 0)}")
        print()

if __name__ == "__main__":
    asyncio.run(test_unified_search())

