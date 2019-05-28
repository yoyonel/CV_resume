BUILD = build

USER_ID = $(shell id -u ${USER})
GROUP_ID = $(shell id -g ${USER})

CURRENT_YEAR = $(shell date +"%Y")

TARGET_PDF = data/pdf/${CURRENT_YEAR}/${CURRENT_YEAR}_ATTY_Resume.pdf

DOCKER_ID_USER ?= yoyonel

all: cv_resume

cv_resume: pdf

clean:
	rm -rf ${TARGET_PDF}
	rm pandoc_resume/resume.pdf


pdf: ${TARGET_PDF}

${TARGET_PDF}: pandoc_resume/resume.md
	# url: http://aty.sdsu.edu/bibliog/latex/LaTeXtoPDF.html


	mkdir -p data/pdf/${CURRENT_YEAR}

	# -u $(USER_ID):$(GROUP_ID) \
	# Probleme avec font latex => https://github.com/sharelatex/sharelatex/issues/450
	# utilisation d'un workaround, comme on connait la cible, on peut effectuer manuellement
	# et directement le changement d'owner.

	# chown ${USER}:${USER} resume.pdf; \

	docker run \
		-it --rm \
		-v `pwd`:/source \
		-v /etc/group:/etc/group:ro \
		-v /etc/passwd:/etc/passwd:ro \
		${DOCKER_ID_USER}/pandoc \
		bash -c "\
			cd /source/pandoc_resume; \
			make pdf; \
			"

	cp pandoc_resume/resume.pdf ${TARGET_PDF}


.PHONY: all cv_resume clean pdf
