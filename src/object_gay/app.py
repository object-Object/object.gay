from fastapi import status
from fastapi.responses import HTMLResponse, RedirectResponse

from .api.app import app as api_app
from .utils import create_root_app, serve

app = create_root_app()
app.mount("/api", api_app)


@app.get("/", response_class=HTMLResponse)
async def get_root():
    return RedirectResponse("https://github.com/object-Object", status.HTTP_302_FOUND)


if __name__ == "__main__":
    serve(app)
