#!/bin/bash

function main() {
  export CLIENT_VPN_ENDPOINT_SERVER_CERTIFICATE_ID="db0b722b-7228-440c-be94-11aedbc2b383"
  ./cdk-deploy-to-sih-innov.sh 123456789124 eu-west-2 "$@"
}

main "$@"
