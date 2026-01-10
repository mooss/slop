package main

import (
	"fmt"
	"os"
	"strings"
	"unicode"
)

type JSONLexer struct {
	data  []byte
	pos   int
	stack []string
}

type KeyCallback func(key string)

func (lexer *JSONLexer) Lex(callback KeyCallback) error {
	lexer.skipWhitespace()
	if lexer.pos >= len(lexer.data) {
		return nil
	}

	// Start parsing based on the first character
	switch lexer.data[lexer.pos] {
	case '{':
		return lexer.parseObject(callback)
	case '[':
		return lexer.parseArray(callback)
	default:
		return fmt.Errorf("invalid JSON: expected object or array")
	}
}

func (lexer *JSONLexer) skipWhitespace() {
	for lexer.pos < len(lexer.data) && unicode.IsSpace(rune(lexer.data[lexer.pos])) {
		lexer.pos++
	}
}

func (lexer *JSONLexer) parseString() (string, error) {
	if lexer.pos >= len(lexer.data) || lexer.data[lexer.pos] != '"' {
		return "", fmt.Errorf("expected string")
	}

	lexer.pos++ // Skip opening quote
	start := lexer.pos

	for lexer.pos < len(lexer.data) {
		if lexer.data[lexer.pos] == '"' {
			// Check if it's escaped
			escaped := false
			for i := lexer.pos - 1; i >= start && lexer.data[i] == '\\'; i-- {
				escaped = !escaped
			}
			if !escaped {
				break
			}
		}
		lexer.pos++
	}

	if lexer.pos >= len(lexer.data) {
		return "", fmt.Errorf("unterminated string")
	}

	result := string(lexer.data[start:lexer.pos])
	lexer.pos++ // Skip closing quote
	return result, nil
}

func (lexer *JSONLexer) parseValue(callback KeyCallback) error {
	lexer.skipWhitespace()
	if lexer.pos >= len(lexer.data) {
		return fmt.Errorf("unexpected end of input")
	}

	switch lexer.data[lexer.pos] {
	case '{':
		return lexer.parseObject(callback)
	case '[':
		return lexer.parseArray(callback)
	case '"':
		// String value
		_, err := lexer.parseString()
		return err
	case 't':
		// true
		if lexer.pos+3 < len(lexer.data) && string(lexer.data[lexer.pos:lexer.pos+4]) == "true" {
			lexer.pos += 4
			return nil
		}
		return fmt.Errorf("invalid literal")
	case 'f':
		// false
		if lexer.pos+4 < len(lexer.data) && string(lexer.data[lexer.pos:lexer.pos+5]) == "false" {
			lexer.pos += 5
			return nil
		}
		return fmt.Errorf("invalid literal")
	case 'n':
		// null
		if lexer.pos+3 < len(lexer.data) && string(lexer.data[lexer.pos:lexer.pos+4]) == "null" {
			lexer.pos += 4
			return nil
		}
		return fmt.Errorf("invalid literal")
	default:
		// Number
		for lexer.pos < len(lexer.data) && (unicode.IsDigit(rune(lexer.data[lexer.pos])) ||
			lexer.data[lexer.pos] == '.' ||
			lexer.data[lexer.pos] == '-' ||
			lexer.data[lexer.pos] == '+' ||
			lexer.data[lexer.pos] == 'e' ||
			lexer.data[lexer.pos] == 'E') {
			lexer.pos++
		}
		return nil
	}
}

func (lexer *JSONLexer) parseObject(callback KeyCallback) error {
	if lexer.pos >= len(lexer.data) || lexer.data[lexer.pos] != '{' {
		return fmt.Errorf("expected '{'")
	}
	lexer.pos++ // Skip '{'

	lexer.skipWhitespace()
	if lexer.pos < len(lexer.data) && lexer.data[lexer.pos] == '}' {
		lexer.pos++ // Skip '}'
		return nil
	}

	for {
		lexer.skipWhitespace()
		if lexer.pos >= len(lexer.data) {
			return fmt.Errorf("unexpected end of input")
		}

		// Expect key
		if lexer.data[lexer.pos] != '"' {
			return fmt.Errorf("expected key string")
		}

		key, err := lexer.parseString()
		if err != nil {
			return err
		}

		// Add key to stack
		lexer.stack = append(lexer.stack, key)

		// Build full path
		fullPath := strings.Join(lexer.stack, ".")

		// Call callback with full path
		callback(fullPath)

		lexer.skipWhitespace()
		if lexer.pos >= len(lexer.data) || lexer.data[lexer.pos] != ':' {
			return fmt.Errorf("expected ':'")
		}
		lexer.pos++ // Skip ':'

		// Parse value
		err = lexer.parseValue(callback)
		if err != nil {
			return err
		}

		// Remove key from stack
		lexer.stack = lexer.stack[:len(lexer.stack)-1]

		lexer.skipWhitespace()
		if lexer.pos >= len(lexer.data) {
			return fmt.Errorf("unexpected end of input")
		}

		if lexer.data[lexer.pos] == '}' {
			lexer.pos++ // Skip '}'
			break
		}

		if lexer.data[lexer.pos] != ',' {
			return fmt.Errorf("expected ',' or '}'")
		}
		lexer.pos++ // Skip ','
	}

	return nil
}

func (lexer *JSONLexer) parseArray(callback KeyCallback) error {
	if lexer.pos >= len(lexer.data) || lexer.data[lexer.pos] != '[' {
		return fmt.Errorf("expected '['")
	}
	lexer.pos++ // Skip '['

	lexer.skipWhitespace()
	if lexer.pos < len(lexer.data) && lexer.data[lexer.pos] == ']' {
		lexer.pos++ // Skip ']'
		return nil
	}

	for {
		// Parse value
		err := lexer.parseValue(callback)
		if err != nil {
			return err
		}

		lexer.skipWhitespace()
		if lexer.pos >= len(lexer.data) {
			return fmt.Errorf("unexpected end of input")
		}

		if lexer.data[lexer.pos] == ']' {
			lexer.pos++ // Skip ']'
			break
		}

		if lexer.data[lexer.pos] != ',' {
			return fmt.Errorf("expected ',' or ']'")
		}
		lexer.pos++ // Skip ','
	}

	return nil
}

func main() {
	if len(os.Args) != 2 {
		fmt.Println("Usage: go run main.go <json-file>")
		os.Exit(1)
	}

	filename := os.Args[1]
	data, err := os.ReadFile(filename)
	if err != nil {
		fmt.Printf("Error reading file: %v\n", err)
		os.Exit(1)
	}

	lexer := &JSONLexer{
		data:  data,
		pos:   0,
		stack: make([]string, 0),
	}

	callback := func(key string) {
		fmt.Println(key)
	}

	err = lexer.Lex(callback)
	if err != nil {
		fmt.Printf("Error parsing JSON: %v\n", err)
		os.Exit(1)
	}
}
