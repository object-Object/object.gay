import logging

import aws_cdk as cdk

from ..logging import setup_logging
from .stack import CommonArgs, Stack

logger = logging.getLogger(__name__)


def main():
    setup_logging()

    logger.info("Ready.")
    app = cdk.App()

    common = CommonArgs(
        base_stack_name="object-gay",
        oidc_owner="object-Object",
        oidc_repo="object.gay",
    )

    Stack(
        app,
        "prod",
        common=common,
        env=cdk.Environment(
            account="511603859520",
            region="us-east-1",
        ),
        oidc_environment="prod-aws-cdk",
        artifacts_bucket_name="prod-objectobject-ca-codedeploy-artifacts",
        on_premise_instance_tag="prod-objectobject-ca",
    )

    logger.info("Synthesizing.")
    app.synth()


if __name__ == "__main__":
    main()
