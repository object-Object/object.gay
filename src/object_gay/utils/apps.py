import os

import uvicorn
from fastapi import FastAPI


def add_health_endpoint(app: FastAPI):
    async def get_health():
        return {"status": "OK"}

    return app.get("/health")(get_health)


def serve(app: FastAPI):
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=int(os.getenv("PORT", "5000")),
    )
