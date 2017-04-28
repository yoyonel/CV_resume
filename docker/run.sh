#!/usr/bin/env sh

# $1: chemin vers le repertoire des sources du projet
# $@: option de la commande make

# ex: ./run.sh $(realpath ../.) pdf

PATH_TO_SOURCE=$1
shift

DOCKER_IMAGE=$DOCKER_ID_USER/pandoc

USER_ID=$(id -u $USER)
GROUP_ID=$(id -g $USER)

docker run \
	-it --rm \
	-v $(realpath $PATH_TO_SOURCE):/source \
	-v /etc/group:/etc/group:ro \
	-v /etc/passwd:/etc/passwd:ro \
	-u $USER_ID:$GROUP_ID \
	$DOCKER_IMAGE \
	bash -c "\
		cd /source/pandoc_resume; \
		make $@"