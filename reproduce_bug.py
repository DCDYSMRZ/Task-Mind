
import asyncio
import os
import sys
from task-mind.server.services.terminal_service import TerminalSession

async def main():
    # Start a session that exits immediately
    print("Starting short-lived session...")
    session = TerminalSession("test-session", ["echo", "Hello World"])
    await session.start()
    
    print("Reading from session...")
    empty_reads = 0
    max_empty_reads = 5
    
    while True:
        data = await session.read()
        if data:
            print(f"Received data: {repr(data)}")
        else:
            print("Received None (No data/EOF)")
            empty_reads += 1
            if empty_reads >= max_empty_reads:
                print("Too many None reads. Bug confirmed: EOF is not distinguished from no data.")
                break
            await asyncio.sleep(0.1)

    await session.stop()

if __name__ == "__main__":
    asyncio.run(main())
