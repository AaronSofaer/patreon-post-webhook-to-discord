#!/usr/bin/bash
# https://gist.github.com/mihow/9c7f559807069a03e302605691f85572

set -euo pipefail

if [ ! -f .env ]
then
  export $(cat .env | xargs)
fi