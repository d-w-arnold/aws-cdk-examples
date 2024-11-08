#!/bin/bash

function main() {
  if [[ "$#" -ge 2 ]]; then
    export CDK_DEPLOY_ACCOUNT="$1"
    export CDK_DEPLOY_REGION="$2"
    shift
    shift
    pwd
    cdk deploy --outputs-file ./cdk-outputs.json --verbose "$@"
    python3 cdk-custom-outputs.py
    exit $?
  else
    echo 1>&2 "Provide AWS account and region as first two args."
    echo 1>&2 "Additional args are passed through to: \`cdk deploy\`."
    exit 1
  fi
}

main "$@"
