from functools import cache
from typing import Annotated

from fastapi import Depends
from pydantic import AnyHttpUrl
from pydantic_settings import BaseSettings


class AppConfig(BaseSettings):
    model_config = {
        "extra": "ignore",
        "env_prefix": "APP_",
    }

    zipline_url: AnyHttpUrl

    @staticmethod
    @cache
    def get():
        return AppConfig.model_validate({})

    def zipline_route(self, route: str):
        return str(self.zipline_url).rstrip("/") + route


AppConfigDependency = Annotated[AppConfig, Depends(AppConfig.get)]
