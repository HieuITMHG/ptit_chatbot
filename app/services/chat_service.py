import asyncio
from fastapi import WebSocket
from core.redis_client import async_redis_client

# Bỏ tham số redis_client đi, chỉ giữ lại task_id và websocket
async def listen_to_redis(task_id: str, websocket: WebSocket):
    pubsub = async_redis_client.pubsub()
    await pubsub.subscribe(task_id)

    try:
        while True:
            message = await pubsub.get_message(ignore_subscribe_messages=True)

            if message:
                # Redis thường trả về bytes, cần decode ra string để JSON không bị lỗi
                raw_data = message["data"]
                data_str = raw_data.decode('utf-8') if isinstance(raw_data, bytes) else raw_data

                # Phản hồi lại cho frontend
                await websocket.send_json({
                    "status": "Completed",
                    "task_id": task_id,
                    "answer": data_str # Đổi key "data" thành "answer" để khớp với code React
                })

                break # Nhận được kết quả rồi thì thoát vòng lặp

            await asyncio.sleep(0.1)

    except Exception as e:
        print(f"Lỗi khi lắng nghe Redis: {e}")
    finally:
        await pubsub.unsubscribe(task_id)
        await pubsub.close()