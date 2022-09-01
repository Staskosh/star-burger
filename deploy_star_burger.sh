#!/bin/bash
set -e
cd /opt/star-burger
source star-burger-env/bin/activate
git pull
systemctl daemon-reload
systemctl reload nginx
REVISION=$(git rev-parse --short HEAD)
ROLLBAR_POST_SERVER_TOKEN=$(bash -c 'set -a; source .env; printenv ROLLBAR_POST_SERVER_TOKEN')
curl -H "X-Rollbar-Access-Token: $ROLLBAR_POST_SERVER_TOKEN" -H "Content-Type: application/json" -X POST 'https://api.rollbar.com/api/1/deploy' -d '{"environment": "deploy>
echo 'Deploy successfully done.'
