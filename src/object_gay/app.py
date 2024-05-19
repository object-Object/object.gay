from fastapi import FastAPI, status
from fastapi.responses import HTMLResponse, RedirectResponse

from .utils.apps import add_health_endpoint, serve

app = FastAPI(
    openapi_url=None,
)
add_health_endpoint(app)


@app.get("/", response_class=HTMLResponse)
async def get_root():
    return RedirectResponse("https://github.com/object-Object", status.HTTP_302_FOUND)


if __name__ == "__main__":
    serve(app)
