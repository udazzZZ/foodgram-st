#!/usr/bin/env bash
set -euo pipefail

: "${GITHUB_CONFIG_URL:?Set GITHUB_CONFIG_URL to https://github.com/<owner>/<repo>}"
: "${GITHUB_PAT:?Set GITHUB_PAT to a GitHub token with access to register runners}"

CONTROLLER_NAMESPACE="${CONTROLLER_NAMESPACE:-arc-systems}"
RUNNERS_NAMESPACE="${RUNNERS_NAMESPACE:-arc-runners}"
RUNNER_SECRET_NAME="${RUNNER_SECRET_NAME:-github-runner-secret}"
RUNNER_RELEASE_NAME="${RUNNER_RELEASE_NAME:-foodgram-runner-set}"

helm upgrade --install arc \
  oci://ghcr.io/actions/actions-runner-controller-charts/gha-runner-scale-set-controller \
  --namespace "${CONTROLLER_NAMESPACE}" \
  --create-namespace

kubectl create namespace "${RUNNERS_NAMESPACE}" --dry-run=client -o yaml | kubectl apply -f -

kubectl create secret generic "${RUNNER_SECRET_NAME}" \
  --namespace "${RUNNERS_NAMESPACE}" \
  --from-literal=github_token="${GITHUB_PAT}" \
  --dry-run=client \
  -o yaml | kubectl apply -f -

helm upgrade --install "${RUNNER_RELEASE_NAME}" \
  oci://ghcr.io/actions/actions-runner-controller-charts/gha-runner-scale-set \
  --namespace "${RUNNERS_NAMESPACE}" \
  --create-namespace \
  -f values.yaml \
  --set githubConfigUrl="${GITHUB_CONFIG_URL}" \
  --set githubConfigSecret="${RUNNER_SECRET_NAME}"
