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
        # Iterate over a snapshot: `handler()` can remove a client from
        # `connected_clients` concurrently on disconnect, which raises
        # "Set changed size during iteration" if we iterate the live set.
        for client in list(connected_clients):
            try:
                await client.send(message)
            except websockets.exceptions.ConnectionClosed:
                pass

async def handler(websocket):
    logger.info("Client connected to Omniverse Sync Bridge.")
    connected_clients.add(websocket)
    try:
        async for message in websocket:
            try:
                data = json.loads(message)
            except json.JSONDecodeError:
                logger.warning("Received non-JSON frame, ignoring.")
                continue

            if data.get("type") == "AGENT_TRANSFORMS":
                # Sent by OASIS PRIME's UsdSyncBridge.cs -- merge into shared
                # state and fan out to every OTHER connected client (e.g. a
                # monitoring dashboard) so the digital twin actually updates
                # for observers, not just for whoever sent it.
                swarm_state["agents"] = data.get("agents", [])
                rebroadcast = json.dumps({
                    "type": "AGENT_TRANSFORMS_SYNC",
                    "time": swarm_state["time"],
                    "agents": swarm_state["agents"],
                })
                for client in list(connected_clients):
                    if client is websocket:
                        continue
                    try:
                        await client.send(rebroadcast)
                    except websockets.exceptions.ConnectionClosed:
                        pass
            else:
                logger.info(f"Received unrecognized frame type: {data.get('type')}")
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
