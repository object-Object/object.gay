#!/bin/bash
set -euox pipefail

run_pm2() {
    sudo su object -c "pm2 --no-color --mini-list $*"
}

cd /var/lib/codedeploy-apps/object.gay || exit 0

if run_pm2 delete pm2.config.js; then
    run_pm2 save
fi

if sudo a2dissite object.gay.conf; then
    sudo apachectl graceful
fi
