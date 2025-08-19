#!/bin/bash
set -e
REPO_NAME=$1
if [ -z "$REPO_NAME" ]; then
  echo "Usage: ./bootstrap.sh <repo-name>"
  exit 1
fi
git init
git add .
git commit -m "Initial commit"
gh repo create $REPO_NAME --public --source=. --push
