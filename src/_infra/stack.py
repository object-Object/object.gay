import logging
from dataclasses import dataclass

import aws_cdk as cdk
import cdk_cloudformation_cloudflare_dns_record as cloudflare
from aws_cdk import (
    aws_codedeploy as codedeploy,
    aws_iam as iam,
    aws_s3 as s3,
)
from aws_cdk_github_oidc import GithubActionsIdentityProvider, GithubActionsRole
from cdk_cloudformation_cloudflare_dns_record import CfnRecordPropsType as RecordType
from constructs import Construct

logger = logging.getLogger(__name__)


@dataclass(frozen=True, kw_only=True)
class CommonArgs:
    base_stack_name: str
    oidc_owner: str
    oidc_repo: str


class Stack(cdk.Stack):
    def __init__(
        self,
        scope: Construct,
        stage: str,
        *,
        common: CommonArgs,
        env: cdk.Environment,
        oidc_environment: str,
        artifacts_bucket_name: str,
        on_premise_instance_tag: str,
        cf_zone_id: str,
        vps_ip: str,
    ):
        stack_name = f"{stage}-{common.base_stack_name}"

        logger.info(f"Initializing stack: {stack_name}")
        super().__init__(
            scope,
            stage,
            stack_name=stack_name,
            env=env,
        )

        # external resources

        oidc_proxy = GithubActionsIdentityProvider.from_account(
            self,
            "GitHubOIDCProviderProxy",
        )

        artifacts_bucket_proxy = s3.Bucket.from_bucket_name(
            self,
            "ArtifactsBucketProxy",
            artifacts_bucket_name,
        )

        # CodeDeploy

        application = codedeploy.ServerApplication(
            self,
            "Application",
        )

        deployment_config: codedeploy.ServerDeploymentConfig = (
            codedeploy.ServerDeploymentConfig.ONE_AT_A_TIME
        )

        group = codedeploy.ServerDeploymentGroup(
            self,
            "DeploymentGroup",
            application=application,
            deployment_config=deployment_config,
            auto_rollback=codedeploy.AutoRollbackConfig(
                failed_deployment=True,
            ),
            on_premise_instance_tags=codedeploy.InstanceTagSet(
                {"instance": [on_premise_instance_tag]}
            ),
        )

        # GitHub Actions

        actions_role = GithubActionsRole(
            self,
            "ActionsCodeDeployRole",
            provider=oidc_proxy,
            owner=common.oidc_owner,
            repo=common.oidc_repo,
            filter=f"environment:{oidc_environment}",
        )
        artifacts_bucket_proxy.grant_read_write(actions_role)
        actions_role.add_to_policy(
            iam.PolicyStatement(
                actions=["codedeploy:*"],
                resources=[
                    application.application_arn,
                    group.deployment_group_arn,
                    deployment_config.deployment_config_arn,
                ],
            )
        )

        # Cloudflare

        for record_type, records in {
            RecordType.A: {
                "@": (vps_ip, True),
                "get": (vps_ip, True),
            },
        }.items():
            for name, (value, proxied) in records.items():
                create_record(
                    self,
                    zone_id=cf_zone_id,
                    type=record_type,
                    name=name,
                    value=value,
                    proxied=proxied,
                )

        # outputs
        cdk.CfnOutput(self, "ApplicationName", value=application.application_name)
        cdk.CfnOutput(self, "DeploymentGroupName", value=group.deployment_group_name)
        cdk.CfnOutput(self, "ActionsCodeDeployRoleARN", value=actions_role.role_arn)
        cdk.CfnOutput(self, "ArtifactsBucketName", value=artifacts_bucket_name)


def create_record(
    scope: Construct,
    *,
    zone_id: str,
    type: RecordType,
    name: str | None,
    value: str,
    proxied: bool = False,
    ttl: int | None = None,
):
    id_parts: tuple[str, ...]
    match name:
        case "@":
            id_parts = (type.value, "ROOT", value)
        case "*":
            id_parts = (type.value, "WILDCARD", value)
        case str():
            id_parts = (type.value, name, value)
        case None:
            id_parts = (type.value, value)
            name = "@"

    return cloudflare.CfnRecord(
        scope,
        "_".join(id_parts).replace(".", "-"),
        zone_id=zone_id,
        type=type,
        name=name,
        content=value,
        proxied=proxied,
        ttl=ttl or 1,
    )
