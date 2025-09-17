#!/bin/bash
set -euox pipefail

mkdir -p /mnt/blockstorage/codedeploy-apps/object-gay

cd /var/lib/codedeploy-apps/object-gay

docker login ghcr.io --username object-Object --password-stdin < /var/lib/codedeploy-apps/.cr_pat

docker compose pull
