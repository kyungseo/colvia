package main

import (
	"errors"
	"os"
	"os/exec"
	"syscall"
)

func platformNotice(root string, manager bool, args []string) (bool, error) {
	if !manager || len(args) == 0 || args[0] != "notice-activate" {
		return false, nil
	}
	if len(args) > 2 || (len(args) == 2 && args[1] != "-Embedding" && args[1] != "/Embedding") {
		return true, errors.New("notice-activation-arguments")
	}
	self, err := os.Executable()
	if err != nil {
		return true, err
	}
	return true, noticeWindow(self, root)
}

func configureNoticeChild(child *exec.Cmd, command []string) {
	for _, arg := range command {
		if arg == "--receiver-source" {
			child.SysProcAttr = &syscall.SysProcAttr{CreationFlags: 0x08000000, HideWindow: true}
			return
		}
	}
}
