from typing import Annotated

from fastapi import Depends
from httpx import AsyncClient


class GlobalAsyncClient:
    instance: AsyncClient

    @classmethod
    async def start(cls):
        cls.instance = AsyncClient()

    @classmethod
    def get(cls):
        return cls.instance

    @classmethod
    async def stop(cls):
        await cls.instance.aclose()


AsyncClientDependency = Annotated[AsyncClient, Depends(GlobalAsyncClient.get)]
