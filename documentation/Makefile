stylesheet = rocket-panda.css
styledir   = /usr/local/share/asciidoctor/stylesheets
remote     = h4:/home/maposmatic/maposmatic/www/static/documentation

all: html pdf

html: api-docs.html user-guide.html
pdf: api-docs.pdf user-guide.pdf

%.html: %.txt
	asciidoctor $<

%.pdf: %.txt 
	asciidoctor-pdf $<

clean:
	rm -f *.html *.pdf *~

install: all
	cp *.html ../www/maposmatic/templates

.PHONY = html clean all install
