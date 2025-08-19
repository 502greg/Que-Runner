from fastapi import FastAPI
from pydantic import BaseModel
import httpx, os

app = FastAPI()
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

class Item(BaseModel):
    id: str
    prompt: str
    seed: int | None = None
    variations: int = 1

class Queue(BaseModel):
    queue_id: str
    global_prompt: str
    items: list[Item]

@app.post("/run-queue")
async def run_queue(queue: Queue):
    results = []
    async with httpx.AsyncClient(timeout=60.0) as client:
        for item in queue.items:
            merged_prompt = f"{queue.global_prompt} {item.prompt}"
            try:
                resp = await client.post(
                    "https://api.openai.com/v1/images/generations",
                    headers={"Authorization": f"Bearer {OPENAI_API_KEY}"},
                    json={
                        "model": "gpt-image-1",
                        "prompt": merged_prompt,
                        "size": "1024x1024",
                        "n": item.variations,
                        "seed": item.seed,
                    },
                )
                data = resp.json()
                if "data" not in data:
                    raise Exception(data)
                results.append({
                    "item_id": item.id,
                    "status": "SUCCESS",
                    "prompt": merged_prompt,
                    "seed": item.seed,
                    "files": [f"{queue.queue_id}/{item.id}-v{i+1}.png" for i in range(item.variations)]
                })
            except Exception as e:
                results.append({
                    "item_id": item.id,
                    "status": "FAILED",
                    "error": str(e)
                })
    return {"queue_id": queue.queue_id, "results": results}
