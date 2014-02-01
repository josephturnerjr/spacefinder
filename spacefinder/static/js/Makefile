COFFEEC = coffee

all: $(patsubst %.coffee, %.js, $(wildcard *.coffee))

watch:
	coffee -w -c $(wildcard *.coffee)

clean:
	-rm $(patsubst %.coffee, %.js, $(wildcard *.coffee))

%.js: %.coffee
	$(COFFEEC) -c $<
