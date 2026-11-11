package main

import (
	"errors"
	"path/filepath"
	"syscall"
	"unsafe"
)

type guid struct {
	a    uint32
	b, c uint16
	d    [8]byte
}

func defaultRoot() (string, error) {
	id := guid{0xF1B32785, 0x6FBA, 0x4FCF, [8]byte{0x9D, 0x55, 0x7B, 0x8E, 0x7F, 0x15, 0x70, 0x91}}
	var output *uint16
	proc := syscall.NewLazyDLL("shell32.dll").NewProc("SHGetKnownFolderPath")
	result, _, _ := proc.Call(uintptr(unsafe.Pointer(&id)), 0, 0, uintptr(unsafe.Pointer(&output)))
	if int32(result) != 0 || output == nil {
		return "", errors.New("local-user-data-unavailable")
	}
	defer syscall.NewLazyDLL("ole32.dll").NewProc("CoTaskMemFree").Call(uintptr(unsafe.Pointer(output)))
	values := unsafe.Slice(output, 32768)
	end := 0
	for end < len(values) && values[end] != 0 {
		end++
	}
	if end == len(values) {
		return "", errors.New("local-user-data-path-limit")
	}
	return filepath.Join(syscall.UTF16ToString(values[:end]), "Colvia"), nil
}
