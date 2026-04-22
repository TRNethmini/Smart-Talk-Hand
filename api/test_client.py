import asyncio
import websockets
import json
import numpy as np
import random

async def test_client():
    uri = "ws://127.0.0.1:8000/ws/predict"
    print(f"Connecting to {uri}...")
    
    try:
        async with websockets.connect(uri) as websocket:
            print("Connected!")
            
            # Simulate a continuous stream of frames
            # Each frame is (33, 3) list
            for i in range(100):
                # Generate random dummy landmarks or load from file
                # Shape: (33, 3)
                landmarks = np.random.rand(33, 3).tolist()
                
                await websocket.send(json.dumps(landmarks))
                
                response = await websocket.recv()
                print(f"Sent frame {i}, received: {response}")
                
                # Simulate frame rate (e.g., 30 FPS -> ~0.033s)
                await asyncio.sleep(0.033)
                
    except Exception as e:
        print(f"Connection error details: {type(e).__name__}: {e}")
        print("Ensure the API is running: `uvicorn api.main:app`")

if __name__ == "__main__":
    if hasattr(asyncio, 'run'):
        asyncio.run(test_client())
    else:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(test_client())
