from functools import cache
from typing import Annotated

from fastapi import Depends
from pydantic_settings import BaseSettings

from .types import AnyHttpUrlStr


class AppConfig(BaseSettings):
    model_config = {
        "extra": "ignore",
        "env_prefix": "APP_",
    }

    zipline_url: AnyHttpUrlStr

    @staticmethod
    @cache
    def get():
        return AppConfig.model_validate({})


AppConfigDependency = Annotated[AppConfig, Depends(AppConfig.get)]
