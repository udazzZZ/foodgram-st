#!/bin/bash

set -a
source .env
set +a

echo "POSTGRES_USER: ref+vault://secrets/db#/POSTGRES_USER" | /c/Program\ Files/vals/vals.exe eval -f -
