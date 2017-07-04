#!/usr/bin/env bash

set -e

[[ -z "$DEBUG" ]] || set -x

PIPELINE_NAME=${1:-vs-wbw}
REPO="$HOME/workspace/weight-but-why"

lpass \
  show "Personal/wbw-pipeline-secrets" \
  --notes \
  > "$REPO/ci/private.yml"

fly \
  -t zumba \
  set-pipeline \
    -p "$PIPELINE_NAME" \
    -c "$REPO/ci/pipeline.yml" \
    -l "$REPO/ci/private.yml"
