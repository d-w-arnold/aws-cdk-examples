#!/bin/bash

function main() {
  ./cdk-deploy-to-sih.sh 123456789123 us-east-1 "$@"
}

main "$@"
