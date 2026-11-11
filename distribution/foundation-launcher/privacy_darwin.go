package main

import (
	"errors"
	"os"
	"syscall"
)

func privateFile(path string, info os.FileInfo) error {
	native, ok := info.Sys().(*syscall.Stat_t)
	if !ok || native.Uid != uint32(os.Getuid()) || native.Nlink != 1 || info.Mode().Perm()&0022 != 0 {
		return errors.New("runtime-file-not-private")
	}
	return nil
}
func privateRoot(path string) error {
	info, err := os.Lstat(path)
	if err != nil {
		return err
	}
	native, ok := info.Sys().(*syscall.Stat_t)
	if !ok || !info.IsDir() || native.Uid != uint32(os.Getuid()) || info.Mode().Perm()&0077 != 0 {
		return errors.New("runtime-root-not-private")
	}
	return nil
}
