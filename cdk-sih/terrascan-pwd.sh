#!/bin/bash

function main() {
  export CDK_TEMPLATES="cdk-templates"
  mkdir -p "${CDK_TEMPLATES}"
  cp -a cdk.out/*.template.json "${CDK_TEMPLATES}"
  terrascan scan -d "${CDK_TEMPLATES}" -i cft -t aws -c .terrascan.toml
  rm -rf "${CDK_TEMPLATES}"
}

main "$@"
