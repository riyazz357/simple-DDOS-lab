import asyncio
import aiohttp
import time
from rich.live import Live
from rich.layout import Layout
from rich.panel import Panel
from rich.align import Align
from rich.text import Text
from rich.table import Table
from rich import box

# --- CONFIGURATION ---
TARGET_URL = "http://127.0.0.1:8000/heavy"
TOTAL_REQUESTS = 5000  # Increased for longer show
CONCURRENCY = 200

# --- GLOBAL STATS ---
stats = {
    "sent": 0,
    "success": 0,   # Status 200
    "blocked": 0,   # Status 429
    "failed": 0,    # Status 500 or Error
    "errors": []    # Log last 5 errors
}

def generate_dashboard():
    """Constructs the UI layout"""
    layout = Layout()
    layout.split_column(
        Layout(name="header", size=3),
        Layout(name="body"),
        Layout(name="footer", size=3)
    )
    
    # 1. HEADER
    layout["header"].update(Panel(Align.center(Text("🌊 PROJECT TSUNAMI: DDoS SIMULATOR", style="bold white on blue")), style="blue"))
    
    # 2. BODY (Split into Stats and Logs)
    layout["body"].split_row(
        Layout(name="stats", ratio=1),
        Layout(name="logs", ratio=1)
    )
    
    # Left Side: Statistics Table
    table = Table(box=box.SIMPLE)
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="bold white")
    table.add_row("🚀 Total Requests Sent", str(stats["sent"]))
    table.add_row("✅ Server Success (200)", f"[green]{stats['success']}[/green]")
    table.add_row("🛡️ Rate Limited (429)", f"[yellow]{stats['blocked']}[/yellow]")
    table.add_row("💀 Server Crashed (500)", f"[red]{stats['failed']}[/red]")
    
    # Calculate Impact (Are we winning?)
    total_responses = stats['success'] + stats['blocked'] + stats['failed']
    if total_responses > 0:
        blocked_pct = (stats['blocked'] / total_responses) * 100
        impact_color = "green" if blocked_pct < 50 else "red"
        impact_msg = f"[{impact_color}]{blocked_pct:.1f}% BLOCKED[/]"
    else:
        impact_msg = "Waiting..."
        
    table.add_row("🔥 Attack Effectiveness", impact_msg)
    
    layout["stats"].update(Panel(table, title="Live Telemetry", border_style="cyan"))

    # Right Side: Live Log
    log_text = "\n".join(stats["errors"][-10:]) # Show last 10 logs
    layout["logs"].update(Panel(Text(log_text), title="Real-Time Event Log", border_style="red"))

    # 3. FOOTER (Progress Bar)
    progress_pct = (stats["sent"] / TOTAL_REQUESTS) * 100
    layout["footer"].update(Panel(Align.center(f"Attack Progress: {progress_pct:.1f}%"), style="green"))

    return layout

async def attack(session):
    try:
        async with session.get(TARGET_URL) as response:
            stats["sent"] += 1
            status = response.status
            
            if status == 200:
                stats["success"] += 1
                stats["errors"].append(f"[green]✔ Request Accepted ({stats['sent']})[/]")
            elif status == 429:
                stats["blocked"] += 1
                stats["errors"].append(f"[yellow]🛡️ BLOCKED by Firewall ({stats['sent']})[/]")
            else:
                stats["failed"] += 1
                stats["errors"].append(f"[red]❌ Server Error {status}[/]")
    except:
        stats["sent"] += 1
        stats["failed"] += 1
        stats["errors"].append("[red]💀 Connection Died[/]")

async def start_flood():
    # Setup Connection
    connector = aiohttp.TCPConnector(limit=CONCURRENCY)
    async with aiohttp.ClientSession(connector=connector) as session:
        
        # Start the UI
        with Live(generate_dashboard(), refresh_per_second=4) as live:
            tasks = []
            
            # Fire requests in batches so we can see the UI update
            for i in range(TOTAL_REQUESTS):
                task = asyncio.ensure_future(attack(session))
                tasks.append(task)
                
                # Update UI every 50 requests to keep it smooth
                if i % 50 == 0:
                    live.update(generate_dashboard())
                    await asyncio.sleep(0.01) # Tiny pause to let UI breathe
            
            await asyncio.gather(*tasks)
            
            # Final Update
            live.update(generate_dashboard())

if __name__ == '__main__':
    try:
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    except:
        pass
    asyncio.run(start_flood())