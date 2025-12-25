import aiohttp
import asyncio
import sqlite3
import time
from datetime import datetime

# --- CONFIGURATION ---
TARGET_URL = "http://127.0.0.1:8000/heavy"
TOTAL_REQUESTS = 3000
CONCURRENCY = 100

# --- DATABASE SETUP ---
def init_db():
    conn = sqlite3.connect('simulation.db')
    c = conn.cursor()
    c.execute('DROP TABLE IF EXISTS attack_logs') # Clear old logs
    c.execute('''CREATE TABLE attack_logs 
                 (id INTEGER PRIMARY KEY, timestamp REAL, status_code INTEGER)''')
    conn.commit()
    conn.close()

async def log_result(status):
    """Writes result to DB (Optimized)"""
    # In a real heavy production tool, we would batch these inserts.
    # For 3000 requests, direct insert is fine for this demo.
    conn = sqlite3.connect('simulation.db')
    c = conn.cursor()
    c.execute("INSERT INTO attack_logs (timestamp, status_code) VALUES (?, ?)", 
              (time.time(), status))
    conn.commit()
    conn.close()

async def attack(session):
    try:
        async with session.get(TARGET_URL) as response:
            await log_result(response.status)
    except:
        await log_result(500) # Server Error/Death

async def start_flood():
    init_db()
    print(f"🌊 Tsunami initialized. Logging to 'simulation.db'...")
    
    connector = aiohttp.TCPConnector(limit=CONCURRENCY)
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = []
        for i in range(TOTAL_REQUESTS):
            tasks.append(asyncio.ensure_future(attack(session)))
            # Small delay to spread out the graph visuals
            if i % 50 == 0:
                await asyncio.sleep(0.1) 
        
        await asyncio.gather(*tasks)
    print("🏁 Attack Complete.")

if __name__ == '__main__':
    try:
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    except:
        pass
    asyncio.run(start_flood())