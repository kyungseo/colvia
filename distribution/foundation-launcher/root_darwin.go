package main

import (
	"os"
	"path/filepath"
)

func defaultRoot() (string, error) {
	home, err := os.UserHomeDir()
	if err != nil {
		return "", err
	}
	return filepath.Join(home, "Library", "Application Support", "Colvia"), nil
}
