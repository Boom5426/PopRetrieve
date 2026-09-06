TEX  = PopRetrieve_manuscript
SI   = PopRetrieve_SI
BIB  = references

.PHONY: all si clean

all: $(TEX).pdf

FIGS = $(wildcard figures/*.pdf)

$(TEX).pdf: $(TEX).tex $(BIB).bib $(FIGS)
	pdflatex -interaction=nonstopmode $(TEX)
	bibtex $(TEX)
	pdflatex -interaction=nonstopmode $(TEX)
	pdflatex -interaction=nonstopmode $(TEX)

# The SI now carries its own \bibliography{references}, so it needs the same bibtex pass the
# main text does. Without it a fresh clone builds an SI with undefined citations and no
# Supplementary References list, and pdflatex still exits 0.
si: $(SI).pdf
$(SI).pdf: $(SI).tex $(BIB).bib
	pdflatex -interaction=nonstopmode $(SI)
	bibtex $(SI)
	pdflatex -interaction=nonstopmode $(SI)
	pdflatex -interaction=nonstopmode $(SI)

clean:
	rm -f $(TEX).aux $(TEX).bbl $(TEX).blg $(TEX).log $(TEX).out $(TEX).toc \
	      $(SI).aux $(SI).bbl $(SI).blg $(SI).log $(SI).out
