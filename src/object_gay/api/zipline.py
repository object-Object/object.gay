import logging
from typing import Annotated, Any, Literal, Mapping

from fastapi import Form, Header, HTTPException, UploadFile

from object_gay.utils import AppConfigDependency, AsyncClientDependency, create_app

logger = logging.getLogger(__name__)

app = create_app()


@app.post("/upload")
async def post_upload(
    *,
    files: Annotated[list[UploadFile], Form(alias="file")],
    name_format: Literal["UUID", "DATE", "RANDOM", "NAME"] | None = None,
    expires_at: str | None = None,
    password: str | None = None,
    embed: bool = True,
    folder: int | str | None = None,
    authorization: Annotated[str, Header()],
    config: AppConfigDependency,
    client: AsyncClientDependency,
):
    """Uploads a file, optionally to a specific pre-existing folder."""

    auth_header = {"Authorization": authorization}

    # check folder validity before uploading

    # no idea why this is necessary.
    if isinstance(folder, str) and folder.isnumeric():
        folder = int(folder)

    match folder:
        case int():
            # ensure folder exists
            folders_response = await client.get(
                config.zipline_route(f"/api/user/folders/{folder}"),
                headers=auth_header,
            )
            folders_response.raise_for_status()
        case str():
            # get folder by name
            folders_response = await client.get(
                config.zipline_route("/api/user/folders"),
                headers=auth_header,
            )
            folders_response.raise_for_status()

            for folder_info in folders_response.json():
                if folder_info["name"] == folder:
                    folder = folder_info["id"]
                    break
            else:
                raise HTTPException(404, f"Folder not found: {folder}")
        case None:
            pass

    # upload file

    upload_response = await client.post(
        config.zipline_route("/api/upload"),
        headers=prepare_headers(
            {
                **auth_header,
                "Format": name_format,
                "Expires-At": expires_at,
                "Password": password,
                "Embed": embed,
            }
        ),
        files=[
            ("file", (file.filename, file.file, file.content_type, file.headers))
            for file in files
        ],
    )
    upload_response.raise_for_status()

    response: dict[str, Any] = upload_response.json()
    if folder is None:
        return response

    # get file id

    files_response = await client.get(
        config.zipline_route("/api/user/recent"),
        headers=auth_header,
        params={
            "take": 1,
        },
    )
    files_response.raise_for_status()

    file_id: int = files_response.json()[0]["id"]

    # add file to folder

    add_response = await client.post(
        config.zipline_route(f"/api/user/folders/{folder}"),
        headers=auth_header,
        json={
            "file": file_id,
        },
    )
    add_response.raise_for_status()

    return response | {
        "folder": config.zipline_route(f"/folder/{folder}"),
    }


def prepare_headers(headers: Mapping[str, str | float | None]) -> dict[str, str]:
    result = dict[str, str]()
    for key, value in headers.items():
        match value:
            case None:
                pass
            case str():
                result[key] = value
            case bool():
                result[key] = str(value).lower()
            case _:
                result[key] = str(value)
    return result
