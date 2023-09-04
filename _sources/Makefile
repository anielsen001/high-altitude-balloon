PNGS = \
	horizon.png \
	test.png

.PHONY: all clean

all: $(PNGS)

# rules for pdf from tex - for standalone tikz images to pdf
%.pdf: %.tex
	pdflatex $<

# rules for pdf to png
%.png: %.pdf
	convert -density 300 $< $@

# rules for pdf to svg
%.svg: %.pdf
	inkscape -l $@ $<

# rules for svg to pdf
%.pdf: %.svg
	inkscape --export-pdf="$@" $<

clean: 
	rm -f *.aux *.log 