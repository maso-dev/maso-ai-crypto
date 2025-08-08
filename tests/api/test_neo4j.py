#!/usr/bin/env python3
"""Test Neo4j connection directly"""

import asyncio
import os
from neo4j import AsyncGraphDatabase

async def test_neo4j():
    """Test Neo4j connection"""
    uri = os.getenv('NEO4J_URI')
    username = os.getenv('NEO4J_USERNAME')
    password = os.getenv('NEO4J_PASSWORD')
    
    print(f"URI: {uri}")
    print(f"Username: {username}")
    print(f"Password: {'SET' if password else 'NOT SET'}")
    
    if not all([uri, username, password]):
        print("❌ Missing Neo4j credentials")
        return
    
    try:
        driver = AsyncGraphDatabase.driver(uri or "", auth=(username or "", password or ""))
        
        # Test connection
        async with driver.session() as session:
            result = await session.run("RETURN 1 as test")
            record = await result.single()
            if record:
                print(f"✅ Neo4j connection successful! Test result: {record['test']}")
            else:
                print("⚠️ Neo4j connection successful but no result returned")
            
        await driver.close()
        
    except Exception as e:
        print(f"❌ Neo4j connection failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_neo4j())
