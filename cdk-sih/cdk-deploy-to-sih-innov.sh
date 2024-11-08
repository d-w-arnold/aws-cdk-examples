#!/bin/bash

function main() {
  if [[ "$#" -ge 2 ]]; then
    export CDK_DEPLOY_ACCOUNT="$1"
    export CDK_DEPLOY_REGION="$2"
    shift
    shift
    pwd
    export EMAIL_NOTIFICATION_RECIPIENT="cloud.innovation@foobar.co.uk"
    export INFRASTRUCTURE_DOMAIN_NAME="sihdyefqna.com"
    export PROFILE="Innovation"
    export SSH_KEY="aws_foobar_innovation_default_key"
    cdk deploy --outputs-file ./cdk-outputs.json --verbose --profile innovation "$@"
    python3 cdk-custom-outputs.py
    exit $?
  else
    echo 1>&2 "Provide AWS account and region as first two args."
    echo 1>&2 "Additional args are passed through to: \`cdk deploy\`."
    exit 1
  fi
}

main "$@"
