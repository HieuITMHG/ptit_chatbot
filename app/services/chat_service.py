import asyncio
from fastapi import WebSocket
from core.redis_client import async_redis_client

async def listen_to_redis(task_id: str, websocket: WebSocket):
    pubsub = async_redis_client.pubsub()
    await pubsub.subscribe(task_id)

    try:
        while True:
            message = await pubsub.get_message(ignore_subscribe_messages=True)

            if message:

                raw_data = message["data"]
                data_str = raw_data.decode('utf-8') if isinstance(raw_data, bytes) else raw_data

                await websocket.send_json({
                    "status": "Completed",
                    "task_id": task_id,
                    "answer": data_str 
                })

                break

            await asyncio.sleep(0.1)

    except Exception as e:
        print(f"Lỗi khi lắng nghe Redis: {e}")
    finally:
        await pubsub.unsubscribe(task_id)
        await pubsub.close()