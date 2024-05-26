import logging
import os
from typing import Any

import cdktf
from cdktf_cdktf_provider_cloudflare import provider, record
from constructs import Construct


class Stack(cdktf.TerraformStack):
    def __init__(
        self,
        scope: Construct,
        id: str,
        *,
        organization: str,
        workspace: str,
        zone_id: str,
        vultr_vps: str,
    ):
        logging.getLogger(__name__).info(f"Initializing stack: {id}")
        super().__init__(scope, id)

        cdktf.CloudBackend(
            self,
            organization=organization,
            workspaces=cdktf.NamedCloudWorkspace(workspace),
        )

        provider.CloudflareProvider(
            self,
            "CloudflareProvider",
            api_token=os.getenv("CLOUDFLARE_API_TOKEN"),
        )

        # simple records
        for record_type, records in {
            "A": {
                # main server
                "@": (vultr_vps, True),
                "www": (vultr_vps, True),
                "get": (vultr_vps, True),
                "see": (vultr_vps, True),
            },
            "CNAME": {
                # email forwarding
                "_dmarc": ("dmarcforward.emailowl.com", False),
                "dkim._domainkey": ("dkim._domainkey.srs.emailowl.com", False),
            },
        }.items():
            for name, (value, proxied) in records.items():
                create_record(
                    self,
                    zone_id=zone_id,
                    type=record_type,
                    name=name,
                    value=value,
                    proxied=proxied,
                )

        # MX records (email forwarding)
        for value in [
            "mx4.emailowl.com",
            "mx5.emailowl.com",
            "mx6.emailowl.com",
        ]:
            create_record(
                self,
                zone_id=zone_id,
                type="MX",
                name=None,
                value=value,
                priority=10,
            )

        # root-level TXT records
        for value in [
            # SPF record (email forwarding)
            "v=spf1 a mx ~all",
        ]:
            create_record(
                self,
                zone_id=zone_id,
                type="TXT",
                name=None,
                value=value,
            )


def create_record(
    scope: Construct,
    *,
    zone_id: str,
    type: str,
    name: str | None,
    value: str,
    priority: int | None = None,
    proxied: bool = False,
    **kwargs: Any,
):
    match name:
        case "@":
            id_parts = [type, "ROOT", value]
        case "*":
            id_parts = [type, "WILDCARD", value]
        case str():
            id_parts = [type, name, value]
        case None:
            id_parts = [type, value]
            name = "@"

    return record.Record(
        scope,
        "_".join(id_parts).replace(".", "-"),
        zone_id=zone_id,
        type=type,
        name=name,
        value=value,
        priority=priority,
        proxied=proxied,
        **kwargs,
    )
