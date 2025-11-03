#!/bin/bash

set -a
source .env
set +a

echo $VAULT_TOKEN

echo "POSTGRES_USER: ref+vault://secrets/db#/POSTGRES_USER" | /c/Program\ Files/vals/vals.exe eval -f -
echo "password: ref+vault://secrets/rabbitmq#/password" | /c/Program\ Files/vals/vals.exe eval -f -