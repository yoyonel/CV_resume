BUILD = build

USER_ID = $(shell id -u ${USER})
GROUP_ID = $(shell id -g ${USER})

CURRENT_YEAR = $(shell date +"%Y")

ROOT_TARGET_PDF = data/pdf/${CURRENT_YEAR}/${CURRENT_YEAR}
TARGET_PDF = ${ROOT_TARGET_PDF}_ATTY_Resume.pdf
TYPST_TARGET_PDF = ${ROOT_TARGET_PDF}_ATTY_Resume_Typst.pdf

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
	rm -rf ${TARGET_PDF} ${ROOT_TARGET_PDF}_ATTY_References.pdf ${TYPST_TARGET_PDF}
	rm -f pandoc_resume/resume.pdf pandoc_resume/references.pdf typst_resume/resume.typ
	$(call DOCKER_RUN,clean)

RENDER_CMD = $(shell which uv >/dev/null 2>&1 && echo "uv run scripts/render_resume.py" || echo "python3 scripts/render_resume.py")
TYPST_CMD = $(shell which uv >/dev/null 2>&1 && echo "uv run scripts/compile_typst.py" || echo "python3 scripts/compile_typst.py")
TYPST_WATCH_CMD = $(shell which uv >/dev/null 2>&1 && echo "uv run scripts/watch_typst.py" || echo "python3 scripts/watch_typst.py")

pandoc_resume/resume.md: pandoc_resume/resume.md.j2 $(wildcard pandoc_resume/sections/*) data/profile.json scripts/render_resume.py
	$(RENDER_CMD)

pdf: ${TARGET_PDF}

typst: ${TYPST_TARGET_PDF}

typst-watch:
	$(TYPST_WATCH_CMD)

${TYPST_TARGET_PDF}: typst_resume/resume.typ.j2 data/profile.json scripts/compile_typst.py $(wildcard typst_resume/icons/*)
	mkdir -p data/pdf/${CURRENT_YEAR}
	$(TYPST_CMD)

${TARGET_PDF}: pandoc_resume/resume.md pandoc_resume/references.md pandoc_resume/style_chmduquesne.tex
	mkdir -p data/pdf/${CURRENT_YEAR}
	$(call DOCKER_RUN,pdf)
	cp pandoc_resume/resume.pdf ${TARGET_PDF}
	cp pandoc_resume/references.pdf ${ROOT_TARGET_PDF}_ATTY_References.pdf

.PHONY: all cv_resume clean pdf typst typst-watch
