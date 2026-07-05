import asyncio
import time
import httpx

async def fetch(client, url):
    try:
        response = await client.get(url)
        return response.status_code
    except Exception as e:
        return str(e)

async def main():
    url = "http://localhost:8080/health/telemetry"
    start_time = time.time()
    
    async with httpx.AsyncClient() as client:
        tasks = [fetch(client, url) for _ in range(100)]
        results = await asyncio.gather(*tasks)
        
    end_time = time.time()
    print(f"Executed 100 requests in {end_time - start_time:.2f} seconds.")
    
    success = sum(1 for r in results if r == 200)
    print(f"Success rate: {success}/100")
    
if __name__ == "__main__":
    asyncio.run(main())
