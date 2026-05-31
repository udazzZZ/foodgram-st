#!/bin/bash

helm upgrade --install foodgram-locust ./ \
    -n foodgram \
    -f values.yaml
