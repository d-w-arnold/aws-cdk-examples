#!/bin/bash

function main() {
  if [[ "$#" -ge 1 ]]; then
    export STACK_NAME="$1"
    pwd
    printf "\nFor CDK stack: %s\n...\n"  "${STACK_NAME}"
    # Source: https://stackoverflow.com/questions/68295094/get-a-list-of-stack-dependencies-using-cdk-cli
    cdk synth "${STACK_NAME}" | printf "CDK synth length (no. of lines): %s\n"  "$(wc -l)"
    l=$(jq ".artifacts.${STACK_NAME}.dependencies" cdk.out/manifest.json | python3 -c 'import json,sys;from pprint import pprint;obj=json.load(sys.stdin);pprint(sorted([i for i in obj if not (i.endswith(".assets"))]))')
    printf "CDK stack dependencies:\n%s\n\n"  "${l}"
  else
    echo 1>&2 "Provide CDK stack name as first arg, e.g. 'CdkProxyServerStack'"
    exit 1
  fi
}

main "$@"
