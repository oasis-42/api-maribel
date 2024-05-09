from fastapi import FastAPI
from .image_to_text.image_to_text_controller import router

app = FastAPI()

app.include_router(router)

@app.get("/api/v1/health")
async def health():
    return { "status": "OK" }

