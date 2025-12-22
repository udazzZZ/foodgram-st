#!/bin/bash

set -a
source .env
set +a

helm secrets --evaluate-templates --backend vals upgrade --install foodgram ./ \
    -n foodgram \
    -f values.yaml

# helm repo add heywood8-helm-charts https://heywood8.github.io/helm-charts/

# helm install redis-insight heywood8-helm-charts/redisinsight \
#     -n foodgram \
#     -f redis-insight.yaml \
#     --version 0.4.5
