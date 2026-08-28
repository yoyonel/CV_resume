BUILD = build

USER_ID = $(shell id -u ${USER})
GROUP_ID = $(shell id -g ${USER})

CURRENT_YEAR = $(shell date +"%Y")

ROOT_TARGET_PDF = data/pdf/${CURRENT_YEAR}/${CURRENT_YEAR}
TARGET_PDF = ${ROOT_TARGET_PDF}_ATTY_Resume.pdf

DOCKER_ID_USER ?= yoyonel

DIR := $(shell realpath .)

DOCKER_RUN = docker run \
	-it --rm \
	-v ${DIR}:/source \
	-v /etc/group:/etc/group:ro \
	-v /etc/passwd:/etc/passwd:ro \
	${DOCKER_ID_USER}/pandoc \
	bash -c "cd /source/pandoc_resume && make $(1)"

all: cv_resume

cv_resume: pdf

clean:
	rm -rf ${TARGET_PDF} ${ROOT_TARGET_PDF}_ATTY_References.pdf
	rm -f pandoc_resume/resume.pdf
	rm -f pandoc_resume/references.pdf
	$(call DOCKER_RUN,clean)

RENDER_CMD = $(shell which uv >/dev/null 2>&1 && echo "uv run scripts/render_resume.py" || echo "python3 scripts/render_resume.py")

pandoc_resume/resume.md: pandoc_resume/resume.md.j2 $(wildcard pandoc_resume/sections/*) data/profile.json scripts/render_resume.py
	$(RENDER_CMD)

pdf: ${TARGET_PDF}

${TARGET_PDF}: pandoc_resume/resume.md pandoc_resume/references.md
	mkdir -p data/pdf/${CURRENT_YEAR}
	$(call DOCKER_RUN,pdf)
	cp pandoc_resume/resume.pdf ${TARGET_PDF}
	cp pandoc_resume/references.pdf ${ROOT_TARGET_PDF}_ATTY_References.pdf

.PHONY: all cv_resume clean pdf
