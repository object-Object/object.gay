import logging
from typing import TypedDict

import cdktf

from ..logging import setup_logging
from .stack import Stack

logger = logging.getLogger(__name__)


class CommonKwargs(TypedDict):
    organization: str
    workspace: str


def main():
    setup_logging()

    logger.info("Ready.")
    app = cdktf.App()

    common = CommonKwargs(
        organization="object-Object",
        workspace="object-gay",
    )

    Stack(
        app,
        "prod",
        zone_id="bee6d73be404fa54896eb0a73f2184c4",
        vultr_vps="155.138.139.1",
        **common,
    )

    logger.info("Synthesizing.")
    app.synth()


if __name__ == "__main__":
    main()
