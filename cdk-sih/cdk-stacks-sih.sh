#!/bin/bash

function main() {
  if [[ "$#" -ge 1 ]]; then
    export CDK_DEPLOY_REGION="$1"
    pwd
    QUERY="Stacks[].StackName"
    if [[ "$#" -eq 2 ]]; then
      aws cloudformation describe-stacks --region "${CDK_DEPLOY_REGION}" --query "${QUERY}" --profile "$2" | \
      python3 cdk-stacks-sih.py
    else
      aws cloudformation describe-stacks --region "${CDK_DEPLOY_REGION}" --query "${QUERY}" | \
      python3 cdk-stacks-sih.py
    fi
    exit $?
  else
    echo 1>&2 "Provide AWS region as first arg, and an optional AWS account profile name (AWS CLI config) as second arg."
    exit 1
  fi
}

main "$@"
