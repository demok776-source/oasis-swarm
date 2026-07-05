import asyncio
import aiohttp
import time
import json
import random

TARGET_URL = "http://localhost:8080/sync/test_inject"
CONCURRENCY = 500
EVENTS_TO_SEND = 100000

async def send_event(session, i):
    payload = {
        "module": "oasis_prime",
        "event": "stress_tick",
        "payload": {"id": i, "x": random.random(), "y": random.random(), "timestamp": time.time()}
    }
    try:
        async with session.post(TARGET_URL, json=payload) as response:
            await response.text()
    except Exception:
        pass

async def worker(queue, session):
    while True:
        i = await queue.get()
        await send_event(session, i)
        queue.task_done()

async def main():
    print(f"Initializing OASIS SYSTEM CORE vMAX Stress Test...")
    print(f"Target: {EVENTS_TO_SEND} events | Concurrency: {CONCURRENCY}")
    
    queue = asyncio.Queue()
    for i in range(EVENTS_TO_SEND):
        queue.put_nowait(i)
        
    start_time = time.time()
    
    connector = aiohttp.TCPConnector(limit=CONCURRENCY)
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = []
        for _ in range(CONCURRENCY):
            task = asyncio.create_task(worker(queue, session))
            tasks.append(task)
            
        await queue.join()
        
        for task in tasks:
            task.cancel()
            
    duration = time.time() - start_time
    rps = EVENTS_TO_SEND / duration
    print(f"--- STRESS TEST COMPLETE ---")
    print(f"Sent {EVENTS_TO_SEND} events in {duration:.2f} seconds.")
    print(f"Throughput: {rps:.2f} Requests Per Second (RPS).")

if __name__ == "__main__":
    asyncio.run(main())
