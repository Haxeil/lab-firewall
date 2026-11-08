#!/bin/sh
# Si reglas.nft tiene un error, no se toca nada y se mantienen las reglas anteriores.
tr -d '\r' < /reglas/reglas.nft > /tmp/reglas.nft
if ! nft -c -f /tmp/reglas.nft; then
    echo "ERROR en reglas.nft: se mantienen las reglas anteriores."
    exit 1
fi
{ echo "flush ruleset"; cat /tmp/reglas.nft; } | nft -f - && nft list ruleset
