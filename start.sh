#!/bin/bash
set -e

docker stop burpsite || true
docker rm -f burpsite || true
docker rmi burpsite-images || true
# docker container prune

docker build -t burpsite-images .

docker run -d -p 8080:8080 -p 8000:5000 --name burpsite burpsite-images