from fastapi import HTTPException, status
from fastapi.responses import RedirectResponse

from object_gay.utils.apps import create_root_app, serve

ROUTES = {
    "pronouns": "https://en.pronouns.page/@object_Object",
    "discord-banner": "https://www.tumblr.com/blakyoo/738372544130924545",
}

app = create_root_app()


@app.get("/{route}")
async def get_route(route: str):
    if url := ROUTES.get(route):
        return RedirectResponse(url, status.HTTP_302_FOUND)
    raise HTTPException(status.HTTP_404_NOT_FOUND)


if __name__ == "__main__":
    serve(app)
