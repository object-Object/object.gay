from fastapi import FastAPI, HTTPException, status
from fastapi.responses import RedirectResponse

from object_gay.utils.apps import add_health_endpoint, serve

ROUTES = {
    "pronouns": "https://en.pronouns.page/@object_Object",
    "discord-banner": "https://www.tumblr.com/blakyoo/738372544130924545",
}

app = FastAPI(openapi_url="")
add_health_endpoint(app)


@app.get("/{route}")
async def get_route(route: str):
    if url := ROUTES.get(route):
        return RedirectResponse(url, status.HTTP_301_MOVED_PERMANENTLY)
    raise HTTPException(status.HTTP_404_NOT_FOUND)


if __name__ == "__main__":
    serve(app)
