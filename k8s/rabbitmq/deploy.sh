#!/bin/bash

set -a
source .env
set +a

echo $VAULT_TOKEN

helm secrets --evaluate-templates --backend vals upgrade --install \
    my-rabbitmq oci://registry-1.docker.io/cloudpirates/rabbitmq \
    -n foodgram \
    -f values.yaml
