#!/bin/bash

function main() {
  ./cdk-deploy-to-sih.sh 123456789123 eu-west-2 "$@"
}

main "$@"
