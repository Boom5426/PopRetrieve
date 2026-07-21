TEX  = DART_manuscript
SI   = DART_SI
BIB  = references

.PHONY: all si clean

all: $(TEX).pdf

$(TEX).pdf: $(TEX).tex $(BIB).bib
	pdflatex -interaction=nonstopmode $(TEX)
	bibtex $(TEX)
	pdflatex -interaction=nonstopmode $(TEX)
	pdflatex -interaction=nonstopmode $(TEX)

si: $(SI).pdf
$(SI).pdf: $(SI).tex
	pdflatex -interaction=nonstopmode $(SI)
	pdflatex -interaction=nonstopmode $(SI)

clean:
	rm -f $(TEX).aux $(TEX).bbl $(TEX).blg $(TEX).log $(TEX).out $(TEX).toc \
	      $(SI).aux $(SI).log $(SI).out
