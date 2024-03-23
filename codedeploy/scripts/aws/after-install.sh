#!/bin/bash
set -euox pipefail

cd /var/lib/codedeploy-apps/object.gay

uv venv venv --python python3.11
source venv/bin/activate
uv pip install --find-links dist "object.gay[runtime]"
