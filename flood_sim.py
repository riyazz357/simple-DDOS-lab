import aiohttp
import asyncio
import time

# --- CONFIGURATION ---
TARGET_URL = "http://127.0.0.1:8000/heavy_task"
TOTAL_REQUESTS = 2000  # Total 'packets' to send
CONCURRENCY = 500      # How many at the exact same time

async def send_request(session, i):
    try:
        async with session.get(TARGET_URL) as response:
            # We don't care about the content, just the status code
            status = response.status
            if status == 200:
                print(f"[{i}] ✅ Request Processed")
            else:
                print(f"[{i}] ⚠️ Server Struggling (Status: {status})")
    except Exception as e:
        # This usually happens when the server crashes or times out
        print(f"[{i}] ❌ Connection Failed (Server Down?)")

async def flood():
    print(f"🌊 Starting Tsunami: {TOTAL_REQUESTS} requests targeting {TARGET_URL}")
    
    # Create a connection pool
    connector = aiohttp.TCPConnector(limit=CONCURRENCY)
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = []
        start_time = time.time()
        
        for i in range(TOTAL_REQUESTS):
            task = asyncio.ensure_future(send_request(session, i))
            tasks.append(task)
        
        # Fire everything!
        await asyncio.gather(*tasks)
        
        duration = time.time() - start_time
        print(f"\n🏁 Simulation Over.")
        print(f"⚡ Speed: {TOTAL_REQUESTS / duration:.2f} requests/second")

if __name__ == '__main__':
    # Windows requires a specific loop policy for asyncio
    try:
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    except:
        pass
        
    asyncio.run(flood())