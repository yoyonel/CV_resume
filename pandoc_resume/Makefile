all: html pdf docx rtf

# --biblio ../data/bib/bibtex.bib \
# --csl ../data/csl/ieee.csl \

pdf: resume.pdf
resume.pdf: resume.md
	pandoc 	--standalone --template style_chmduquesne.tex \
			--from markdown --to context \
			-V papersize=A4 \
			--biblio ../data/bib/bibtex.bib \
			-o resume.tex resume.md; \
			context resume.tex
#

html: resume.html
resume.html: style_chmduquesne.css resume.md
	pandoc --standalone -H style_chmduquesne.css \
        --from markdown \
        --to html \
        -o resume.html \
        resume.md

docx: resume.docx
resume.docx: resume.md
	pandoc \
		-s -S \
		resume.md \
		-o resume.docx

rtf: resume.rtf
resume.rtf: resume.md
	pandoc \
		-s -S \
		resume.md \
		-o resume.rtf

clean:
	rm -f 	resume.html \
			resume.tex \
			resume.tuc \
			resume.log \
			resume.pdf \
			resume.docx \
			resume.rtf
