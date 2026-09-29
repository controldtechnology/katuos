#!/bin/sh
set -eu

channel=${1:-beta}
case "$channel" in
    stable|beta) ;;
    *) echo "Unsupported Katu channel: $channel" >&2; exit 2 ;;
esac

keyring=/etc/apt/keyrings/katu-archive-keyring.asc
install -D -m 0644 config/katu-archive-keyring.asc "$keyring"
printf 'deb [arch=amd64 signed-by=%s] https://repo.katuos.com.br %s main\n' \
    "$keyring" "$channel" > /etc/apt/sources.list.d/katu.list

apt-get -o Acquire::Retries=2 -o APT::Update::Error-Mode=any update

if [ "$channel" = beta ]; then
    apt-get download katu-update=1.1.1
    package=$(find . -maxdepth 1 -name 'katu-update_1.1.1_*.deb' -print -quit)
    [ -n "$package" ]
    [ "$(dpkg-deb -f "$package" Package)" = katu-update ]
    [ "$(dpkg-deb -f "$package" Version)" = 1.1.1 ]
fi

echo "Public Katu APT channel verified: $channel"
