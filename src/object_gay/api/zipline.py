import logging
from typing import Annotated, Any, Literal, Mapping

from fastapi import Header, HTTPException, UploadFile

from object_gay.utils import AppConfigDependency, AsyncClientDependency, create_app
from object_gay.utils.types import AnyHttpUrlStr

logger = logging.getLogger(__name__)

app = create_app()


@app.post("/upload")
async def post_upload(
    *,
    file: list[UploadFile],
    endpoint: AnyHttpUrlStr | None = None,
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

    if endpoint is None:
        endpoint = config.zipline_url

    auth_header = {"Authorization": authorization}

    # check folder validity before uploading

    # no idea why this is necessary.
    if isinstance(folder, str) and folder.isnumeric():
        folder = int(folder)

    match folder:
        case int():
            # ensure folder exists
            folders_response = await client.get(
                f"{endpoint}/api/user/folders/{folder}",
                headers=auth_header,
            )
            folders_response.raise_for_status()
        case str():
            # get folder by name
            folders_response = await client.get(
                f"{endpoint}/api/user/folders",
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
        f"{endpoint}/api/upload",
        headers=prepare_headers(
            {
                **auth_header,
                "Format": name_format,
                "Expires-At": expires_at,
                "Password": password,
                "Embed": embed,
            }
        ),
        files=[("file", (f.filename, f.file, f.content_type, f.headers)) for f in file],
    )
    upload_response.raise_for_status()

    response: dict[str, Any] = upload_response.json()
    if folder is None:
        return response

    # get file id

    files_response = await client.get(
        f"{endpoint}/api/user/recent",
        headers=auth_header,
        params={
            "take": 1,
        },
    )
    files_response.raise_for_status()

    file_id: int = files_response.json()[0]["id"]

    # add file to folder

    add_response = await client.post(
        f"{endpoint}/api/user/folders/{folder}",
        headers=auth_header,
        json={
            "file": file_id,
        },
    )
    add_response.raise_for_status()

    return response | {
        "folder": f"{endpoint}/folder/{folder}",
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
