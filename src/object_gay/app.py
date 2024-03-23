import random

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from .utils.apps import add_health_endpoint, serve

app = FastAPI(openapi_url="")
add_health_endpoint(app)


@app.get("/", response_class=HTMLResponse)
async def get_root():
    # TODO: make a placeholder page that isn't this
    if random.choice([True, False]):
        return "I can still hear her voice..."
    else:
        return "gay gay homosexual gay"


if __name__ == "__main__":
    serve(app)
