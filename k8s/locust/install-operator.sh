#!/bin/bash

set -e

helm repo add locust-operator https://locustio.github.io/k8s-operator
helm repo update
helm upgrade --install locust-operator locust-operator/locust-operator \
    --namespace locust-operator \
    --create-namespace
kubectl rollout status deployment/locust-operator -n locust-operator
