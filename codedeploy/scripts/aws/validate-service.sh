#!/bin/bash
set -euox pipefail

check_domain() {
    curl "https://$1/health" --write-out "\n" --fail
}

# sleep 10s
check_domain object.gay
check_domain get.object.gay
