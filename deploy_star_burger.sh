#!/bin/bash
set -e
cd /opt/star-burger
source star-burger-env/bin/activate
git pull
python3 manage.py migrate --noinput
python3 manage.py collectstatic --noinput
systemctl daemon-reload
systemctl reload nginx
REVISION=$(git rev-parse --short HEAD)
ROLLBAR_POST_SERVER_TOKEN=$(bash -c 'set -a; source .env; printenv ROLLBAR_POST_SERVER_TOKEN')
curl -H "X-Rollbar-Access-Token: $ROLLBAR_POST_SERVER_TOKEN" -H "Content-Type: application/json" -X POST 'https://api.rollbar.com/api/1/deploy' -d '{"environment": "deployed", "revision": "'"$REVISION"'", "rollbar_name": "stx", "local_username": "root", "comment": "Starburger deployment", "status": "succeeded"}'

echo 'Deploy successfully done.'
