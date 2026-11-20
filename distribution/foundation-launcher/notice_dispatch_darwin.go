package main

import "os/exec"

func platformNotice(root string, manager bool, args []string) (bool, error) { return false, nil }

func configureNoticeChild(child *exec.Cmd, command []string) {}
