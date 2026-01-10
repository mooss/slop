BINARY=jsonlexer
SOURCE=main.go
BUILD_DIR=.

build:
	go build -o $(BUILD_DIR)/$(BINARY) $(SOURCE)

clean:
	rm -f $(BUILD_DIR)/$(BINARY)

.PHONY: build clean
