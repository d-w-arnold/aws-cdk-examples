#!/bin/bash

function main() {
  ./cdk-deploy-to-sih.sh 123456789123 eu-central-1 "$@"
}

main "$@"
