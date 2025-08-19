# Queue Runner Starter

This repo provides a FastAPI service for running queued image generations with OpenAI's API.

## Run locally
```
pip install -r requirements.txt
uvicorn app:app --reload
```

## Deploy to Render
- Create a new Web Service on Render
- Point to this repo
- Add env var `OPENAI_API_KEY`
- Done!
