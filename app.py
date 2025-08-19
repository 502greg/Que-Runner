from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import httpx
import os

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

app = FastAPI()

class Item(BaseModel):
    id: str
    prompt: str
    variations: int = 1
    seed: Optional[int] = None

class QueueRequest(BaseModel):
    global_prompt: str
    items: List[Item]

@app.post("/run-queue")
async def run_queue(req: QueueRequest):
    results = []
    async with httpx.AsyncClient() as client:
        for item in req.items:
            merged_prompt = req.global_prompt + " " + item.prompt

            payload = {
                "model": "gpt-image-1",
                "prompt": merged_prompt,
                "size": "1024x1024",
                "n": item.variations,
            }
            # seed is tracked but not sent to API

            try:
                resp = await client.post(
                    "https://api.openai.com/v1/images/generations",
                    headers={"Authorization": f"Bearer {OPENAI_API_KEY}"},
                    json=payload,
                    timeout=60.0,
                )
                if resp.status_code != 200:
                    raise HTTPException(status_code=resp.status_code, detail=resp.text)
                data = resp.json()
                results.append({
                    "id": item.id,
                    "prompt": merged_prompt,
                    "seed": item.seed,
                    "status": "SUCCESS",
                    "images": [d.get("url") for d in data.get("data", [])]
                })
            except Exception as e:
                results.append({
                    "id": item.id,
                    "prompt": merged_prompt,
                    "seed": item.seed,
                    "status": f"FAILED: {str(e)}",
                    "images": []
                })

    return {"results": results}
