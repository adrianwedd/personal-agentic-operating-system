from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import json
from .event_broker import broker

app = FastAPI()


@app.get("/graph-events")
async def graph_events() -> StreamingResponse:
    queue = broker.register()

    async def event_stream():
        try:
            while True:
                event = await queue.get()
                yield f"data: {json.dumps(event)}\n\n"
        finally:
            broker.unregister(queue)

    return StreamingResponse(event_stream(), media_type="text/event-stream")
