#!/bin/bash

set -a
source .env
set +a

helm secrets --evaluate-templates --backend vals upgrade --install foodgram ./ \
    -n foodgram \
    -f values.yaml
