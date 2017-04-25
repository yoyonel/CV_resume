#!/usr/bin/env sh

DOCKER_IMAGE_NAME=pandoc

echo "build image with tag: $DOCKER_ID_USER/$DOCKER_IMAGE_NAME ..."

docker build \
	-t $DOCKER_ID_USER/$DOCKER_IMAGE_NAME \
	.

echo "push image ..."
docker push $DOCKER_ID_USER/$DOCKER_IMAGE_NAME