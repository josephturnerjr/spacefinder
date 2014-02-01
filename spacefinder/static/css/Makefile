LESSC = lessc

all: $(patsubst %.less, %.css, $(wildcard *.less))

clean:
	-rm $(patsubst %.less, %.css, $(wildcard *.less))

%.css: %.less
	$(LESSC) $< > $@
