#!/bin/bash

function main() {
  ./cdk-deploy-to-sih-innov.sh 123456789124 us-east-1 "$@"
}

main "$@"
