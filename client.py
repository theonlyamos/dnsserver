import asyncio
from async_dns.core import types, Address
from async_dns.resolver import DNSClient

async def query():
    client = DNSClient()
    res = await client.query('howcode.org', types.A,
                             Address.parse('127.0.0.1'))
    print(res)
    print(res.aa)

asyncio.run(query())
