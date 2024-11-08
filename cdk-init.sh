#!/bin/bash

function cdk-init() {
  mkdir "$1"
  cd "$1" || exit
  cdk init app --language python
  rm -rf .venv README.md
  find ./ -type f -exec sed -i '' -e 's/\.venv/venv/g' {} \;
  python3 -m venv venv
  source venv/bin/activate
  python3 -m pip install --upgrade pip
  python3 -m pip install -r requirements.txt
}

function main() {
  if [ -z "$1" ]; then
      echo 1>&2 "Please provide a directory name for the CDK project to be created."
      exit 1
  fi

  if [ ! -d "$1" ]; then
    cdk-init "$@"
  else
      echo 1>&2 "Directory name already exists for another CDK project."
      exit 2
  fi
}

main "$@"
