BUILD = build

USER_ID = $(shell id -u ${USER})
GROUP_ID = $(shell id -g ${USER})

CURRENT_YEAR = $(shell date +"%Y")

ROOT_TARGET_PDF = data/pdf/${CURRENT_YEAR}/${CURRENT_YEAR}
TARGET_PDF = ${ROOT_TARGET_PDF}_ATTY_Resume.pdf

DOCKER_ID_USER ?= yoyonel

DIR := $(shell realpath .)

all: cv_resume

cv_resume: pdf

clean:
	rm -rf ${TARGET_PDF}
	rm pandoc_resume/resume.pdf


pdf: ${TARGET_PDF}

${TARGET_PDF}: pandoc_resume/resume.md pandoc_resume/references.md
	# url: http://aty.sdsu.edu/bibliog/latex/LaTeXtoPDF.html


	mkdir -p data/pdf/${CURRENT_YEAR}

	# -u $(USER_ID):$(GROUP_ID) \
	# Probleme avec font latex => https://github.com/sharelatex/sharelatex/issues/450
	# utilisation d'un workaround, comme on connait la cible, on peut effectuer manuellement
	# et directement le changement d'owner.

	# chown ${USER}:${USER} resume.pdf; \

	docker run \
		-it --rm \
		-v ${DIR}:/source \
		-v /etc/group:/etc/group:ro \
		-v /etc/passwd:/etc/passwd:ro \
		${DOCKER_ID_USER}/pandoc \
		bash -c "\
			cd /source/pandoc_resume; \
			make pdf; \
			"

	cp pandoc_resume/resume.pdf ${TARGET_PDF}
	cp pandoc_resume/references.pdf ${ROOT_TARGET_PDF}_ATTY_References.pdf


.PHONY: all cv_resume clean pdf
