# pyright: reportUnusedFunction=none

import os
from contextlib import asynccontextmanager
from typing import Callable, ParamSpec

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from httpx import HTTPStatusError

from .http_client import GlobalAsyncClient
from .logging import setup_logging

_P = ParamSpec("_P")


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    await GlobalAsyncClient.start()
    yield
    await GlobalAsyncClient.stop()


def _create_app(fastapi: Callable[_P, FastAPI]) -> Callable[_P, FastAPI]:
    assert isinstance(fastapi, type) and issubclass(fastapi, FastAPI)

    def fn(*args: _P.args, **kwargs: _P.kwargs):
        app = fastapi(
            *args,
            **kwargs,
        )

        @app.exception_handler(HTTPStatusError)
        async def httpx_exception_handler(request: Request, exc: HTTPStatusError):
            try:
                message = exc.response.json()
            except ValueError:
                message = exc.response.text

            return JSONResponse(
                status_code=exc.response.status_code,
                content={
                    "detail": "Internal HTTP response failed",
                    "message": message,
                },
            )

        return app

    return fn


create_app = _create_app(FastAPI)


def _create_root_app(fastapi: Callable[_P, FastAPI]) -> Callable[_P, FastAPI]:
    assert isinstance(fastapi, type) and issubclass(fastapi, FastAPI)

    def fn(*args: _P.args, **kwargs: _P.kwargs):
        app = create_app(
            openapi_url=None,
            lifespan=lifespan,
            *args,
            **kwargs,
        )

        @app.get("/health")
        async def get_health():
            return {"status": "OK"}

        return app

    return fn


create_root_app = _create_root_app(FastAPI)


def serve(app: FastAPI):
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=int(os.getenv("PORT", "5000")),
    )
