#!/bin/sh
set -eu

channel=${1:-beta}
case "$channel" in
    stable|beta) ;;
    *) echo "Unsupported Katu channel: $channel" >&2; exit 2 ;;
esac

keyring=/tmp/katu-archive-keyring.asc
source_list=/tmp/katu-public.list
lists=/tmp/katu-public-apt-lists
install -m 0644 config/katu-archive-keyring.asc "$keyring"
mkdir -p "$lists/partial"
printf 'deb [arch=amd64 signed-by=%s] https://repo.katuos.com.br %s main\n' \
    "$keyring" "$channel" > "$source_list"

apt-get -o Dir::Etc::sourcelist="$source_list" \
    -o Dir::Etc::sourceparts=- -o Dir::State::lists="$lists" \
    -o Acquire::Retries=2 -o APT::Update::Error-Mode=any update

if [ "$channel" = beta ]; then
    apt-get -o Dir::Etc::sourcelist="$source_list" \
        -o Dir::Etc::sourceparts=- -o Dir::State::lists="$lists" \
        download katu-update=1.1.1
    package=$(find . -maxdepth 1 -name 'katu-update_1.1.1_*.deb' -print -quit)
    [ -n "$package" ]
    [ "$(dpkg-deb -f "$package" Package)" = katu-update ]
    [ "$(dpkg-deb -f "$package" Version)" = 1.1.1 ]
fi

echo "Public Katu APT channel verified: $channel"
