all: html pdf docx rtf

pdf: resume.pdf references.pdf

PANDOC_PDF_FLAGS = --standalone --template style_chmduquesne.tex --from markdown --to context -V papersize=A4

resume.pdf: PANDOC_EXTRA_FLAGS = --biblio ../data/bib/bibtex.bib

%.pdf: %.md
	pandoc $(PANDOC_PDF_FLAGS) $(PANDOC_EXTRA_FLAGS) -o $*.tex $<
	context $*.tex

html: resume.html
resume.html: resume.md style_chmduquesne.css
	pandoc --standalone -H style_chmduquesne.css --from markdown --to html -o $@ $<

docx: resume.docx
%.docx: %.md
	pandoc -s -o $@ $<

rtf: resume.rtf
%.rtf: %.md
	pandoc -s -o $@ $<

TARGETS_BASE = resume references
clean:
	rm -f $(foreach ext,html tex tuc log pdf docx rtf,$(addsuffix .$(ext),$(TARGETS_BASE)))

.PHONY: all pdf html docx rtf clean
