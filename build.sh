#!/bin/bash -e

TAG=${1:-latest}

docker build -t altipeak/testing-web-console:$TAG . 