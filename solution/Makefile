LATEXMK ?= latexmk
PANDOC ?= pandoc
RM ?= rm -f
SED ?= sed

all: solution.pdf

clean:
	$(RM) solution.pdf
	$(RM) *.out.tex
	$(LATEXMK) -C

solution.pdf: solution.tex appendices.out.tex solution_body.out.tex
	$(LATEXMK) -pdf $< < /dev/null

%.out.tex: %.md Makefile
	@# make some blocks shaded verbatim before running pandoc
	$(SED) '/^```tibasic/,/^```$$/{s/^```tibasic/\\begin{Shaded}\\begin{verbatim}/;s/^```$$/\\end{verbatim}\n\\end{Shaded}/}' $< > $<.tmp.md
	$(PANDOC) $<.tmp.md -o $@.tmp.tex
	@# remove spaces before footnote
	$(SED) 's/\s\+\(\\footnote\)/\1/g' $@.tmp.tex > $@
	$(RM) $<.tmp.md $@.tmp.tex

.PHONY: clean all
