#!/bin/bash
set -Eeuo pipefail
# Sign on the release host. Transfer ONLY a completed public generation.
[[ $# == 1 && -d $1/dists && -d $1/pool ]]
: "${KATU_DEPLOY_HOST:?SSH host alias with verified host key required}"
: "${KATU_DEPLOY_ROOT:?Private hosting directory outside existing website required}"
[[ $KATU_DEPLOY_HOST =~ ^[a-zA-Z0-9._@-]+$ ]]
[[ $KATU_DEPLOY_ROOT =~ ^/[a-zA-Z0-9/_.-]+$ && $KATU_DEPLOY_ROOT != / && $KATU_DEPLOY_ROOT != *..* ]]
PORT=${KATU_SSH_PORT:-1157}
[[ $PORT =~ ^[0-9]+$ ]]
STAMP=$(date -u +%Y%m%dT%H%M%SZ)
for channel in stable beta; do
    gpgv --keyring "${KATU_VERIFY_KEYRING:?Public verification keyring required}" "$1/dists/$channel/InRelease"
done
if find -L "$1" -type f \( -name '*.key' -o -name '*private*' -o -name '*secret*' \) | grep -q .; then
    echo 'Forbidden signing material in public tree' >&2
    exit 1
fi
ssh -p "$PORT" -o StrictHostKeyChecking=yes "$KATU_DEPLOY_HOST" "mkdir -p '$KATU_DEPLOY_ROOT/generations/$STAMP'"
rsync -rtL --delay-updates -e "ssh -p $PORT -o StrictHostKeyChecking=yes" "$1/" "$KATU_DEPLOY_HOST:$KATU_DEPLOY_ROOT/generations/$STAMP/"
ssh -p "$PORT" -o StrictHostKeyChecking=yes "$KATU_DEPLOY_HOST" "cd '$KATU_DEPLOY_ROOT' && ln -s 'generations/$STAMP' '.public-$STAMP' && mv -Tf '.public-$STAMP' public"
echo 'Public generation deployed. Verify HTTPS InRelease before announcing the release.'
