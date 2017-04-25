#!/usr/bin/env sh

# $1: chemin vers le repertoire des sources du projet
# $@: option de la commande make

# ex: ./run.sh $(realpath ../.) pdf

PATH_TO_SOURCE=$1
shift

DOCKER_IMAGE=$DOCKER_ID_USER/pandoc

docker run \
	-it --rm \
	-v $(realpath $PATH_TO_SOURCE):/source \
	$DOCKER_IMAGE \
	bash -c "\
		cd /source/pandoc_resume; \
		make $@"