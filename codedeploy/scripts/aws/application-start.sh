#!/bin/bash
set -euox pipefail

run_pm2() {
    sudo su object -c "pm2 --no-color --mini-list $*"
}

cd /var/lib/codedeploy-apps/object.gay

run_pm2 start pm2.config.js
run_pm2 save

sudo a2ensite object.gay.conf
sudo apachectl graceful
