import asyncio
import websockets
import json
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("OmniverseBridge")

import math

connected_clients = set()
swarm_state = {"time": 0.0}

async def physics_simulator():
    """Generates a massive 5000-agent vortex pattern and broadcasts it"""
    logger.info("Started Physics Simulator broadcasting to WebSocket.")
    while True:
        await asyncio.sleep(0.05) # 20 FPS broadcast
        swarm_state["time"] += 0.05
        
        if not connected_clients:
            continue
            
        payload = {
            "type": "SWARM_FRAME",
            "time": swarm_state["time"],
            "global_offset": [math.sin(swarm_state["time"])*5, 0, math.cos(swarm_state["time"])*5]
        }
        
        message = json.dumps(payload)
        for client in connected_clients:
            try:
                await client.send(message)
            except websockets.exceptions.ConnectionClosed:
                pass

async def handler(websocket):
    logger.info("Client connected to Omniverse Sync Bridge.")
    connected_clients.add(websocket)
    try:
        async for message in websocket:
            data = json.loads(message)
            # Route client messages if needed
    except websockets.exceptions.ConnectionClosed:
        logger.info("Client disconnected.")
    finally:
        connected_clients.remove(websocket)

async def main():
    logger.info("Starting NVIDIA Omniverse Nucleus Mock Bridge on ws://0.0.0.0:8765")
    asyncio.create_task(physics_simulator())
    async with websockets.serve(handler, "0.0.0.0", 8765):
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(main())
