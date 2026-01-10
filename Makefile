.PHONY: build clean

build:
	go build -o json-lexer main.go

run: build
	./json-lexer data/noisy-savefile.json

clean:
	rm json-lexer
