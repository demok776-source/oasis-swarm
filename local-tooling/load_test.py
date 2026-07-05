import asyncio
import aiohttp
import time
import sys

# Test script to send events to app-tier /sync/publish endpoint
async def send_event(session, url, index):
    payload = {
        "module": "AEROSPACE DIVISION",
        "event": "TELEMETRY_LOAD_TEST",
        "payload": {"seq": index, "timestamp": time.time(), "status": "NOMINAL"}
    }
    try:
        async with session.post(url, json=payload, timeout=2.0) as response:
            return response.status
    except Exception:
        return 0

async def main():
    target_url = "http://127.0.0.1:8080/sync/publish"
    total_requests = 1000
    concurrent_connections = 50
    
    print(f"Starting load test targeting: {target_url}")
    print(f"Sending {total_requests} events with concurrency limit {concurrent_connections}...")
    
    sem = asyncio.Semaphore(concurrent_connections)
    start_time = time.time()
    
    async with aiohttp.ClientSession() as session:
        async def worker(i):
            async with sem:
                return await send_event(session, target_url, i)
        
        tasks = [worker(i) for i in range(total_requests)]
        results = await asyncio.gather(*tasks)
        
    duration = time.time() - start_time
    success_count = sum(1 for r in results if r == 200)
    
    print("\n--- Load Test Results ---")
    print(f"Duration: {duration:.2f} seconds")
    print(f"Success rate: {success_count}/{total_requests} ({success_count/total_requests*100:.1f}%)")
    print(f"Throughput: {total_requests/duration:.2f} requests/sec")

if __name__ == "__main__":
    asyncio.run(main())
