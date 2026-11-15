package main

import (
	"bytes"
	"encoding/json"
	"errors"
	"fmt"
	"os"
	"os/exec"
	"path/filepath"
	"runtime"
	"strconv"
	"strings"
	"testing"
)

const helperMode = "COLVIA_LAUNCHER_TEST_MODE"
const helperCode = "COLVIA_LAUNCHER_TEST_CODE"
const childStdout = "{\"error\":\"synthetic-refusal\"}\n"
const childStderr = "synthetic diagnostic\n"

// Re-exec the test binary as both launcher main and the verified child, without
// depending on a shell or Python. Only the child kills its own PID in the
// abnormal-end case; the launcher remains alive to classify the outcome.
var noticeReadTestEntry func()

func TestMain(m *testing.M) {
	if noticeReadTestEntry != nil {
		noticeReadTestEntry()
	}
	switch os.Getenv(helperMode) {
	case "launcher":
		os.Setenv(helperMode, "child")
		main()
		os.Exit(98)
	case "child":
		fmt.Fprint(os.Stdout, childStdout)
		fmt.Fprint(os.Stderr, childStderr)
		if os.Getenv(helperCode) == "signal" {
			p, err := os.FindProcess(os.Getpid())
			if err != nil || p.Kill() != nil {
				os.Exit(97)
			}
			select {} // Only reached until the OS delivers the child-only termination.
		}
		code, err := strconv.Atoi(os.Getenv(helperCode))
		if err != nil {
			os.Exit(96)
		}
		os.Exit(code)
	}
	os.Exit(m.Run())
}

func executableFixture(t *testing.T) string {
	t.Helper()
	root, slot := fixture(t)
	binary, err := os.ReadFile(os.Args[0])
	if err != nil {
		t.Fatal(err)
	}
	if err = os.WriteFile(filepath.Join(slot, "python"), binary, 0700); err != nil {
		t.Fatal(err)
	}
	manifestPath := filepath.Join(slot, "manifest.json")
	raw, err := os.ReadFile(manifestPath)
	if err != nil {
		t.Fatal(err)
	}
	var manifest Manifest
	if err = json.Unmarshal(raw, &manifest); err != nil {
		t.Fatal(err)
	}
	for i := range manifest.Inventory {
		if manifest.Inventory[i].Path == "python" {
			manifest.Inventory[i].Size = int64(len(binary))
			manifest.Inventory[i].SHA = sha(binary)
		}
	}
	raw, err = json.Marshal(manifest)
	if err != nil {
		t.Fatal(err)
	}
	if err = os.WriteFile(manifestPath, raw, 0600); err != nil {
		t.Fatal(err)
	}
	selection := Selection{Version: 1, Selected: Pointer{Slot: "one", Digest: sha(raw)}, High: 1}
	raw, err = json.Marshal(selection)
	if err != nil {
		t.Fatal(err)
	}
	if err = os.WriteFile(filepath.Join(root, "runtime", "runtime.json"), raw, 0600); err != nil {
		t.Fatal(err)
	}
	return root
}

func launcherResult(t *testing.T, root, code string) (int, string, string) {
	t.Helper()
	child := exec.Command(os.Args[0], "--management-root", root, "ordinary", "view", "synthetic")
	child.Env = append(os.Environ(), helperMode+"=launcher", helperCode+"="+code)
	var stdout, stderr bytes.Buffer
	child.Stdout = &stdout
	child.Stderr = &stderr
	err := child.Run()
	if err == nil {
		return 0, stdout.String(), stderr.String()
	}
	var ended *exec.ExitError
	if !errors.As(err, &ended) {
		t.Fatal(err)
	}
	return ended.ExitCode(), stdout.String(), stderr.String()
}

func TestMainPreservesProductExitAndStreams(t *testing.T) {
	root := executableFixture(t)
	for _, code := range []int{0, 1, 2, 17} {
		t.Run(strconv.Itoa(code), func(t *testing.T) {
			actual, stdout, stderr := launcherResult(t, root, strconv.Itoa(code))
			if actual != code || stdout != childStdout || stderr != childStderr {
				t.Fatalf("code=%d stdout=%q stderr=%q", actual, stdout, stderr)
			}
		})
	}
}

func TestMainReportsAbnormalChildWithoutRuntimeFailure(t *testing.T) {
	if runtime.GOOS == "windows" {
		t.Skip("abnormal-end mapping not qualified on Windows")
	}
	code, stdout, stderr := launcherResult(t, executableFixture(t), "signal")
	if code != 1 || stdout != childStdout || stderr != childStderr+"Colvia's product process ended abnormally.\n" {
		t.Fatalf("code=%d stdout=%q stderr=%q", code, stdout, stderr)
	}
}

func TestMainVerificationAndStartFailuresRemainLauncherErrors(t *testing.T) {
	for _, mode := range []string{"start", "verification"} {
		t.Run(mode, func(t *testing.T) {
			root, slot := fixture(t) // Verified but unexecutable fixture bytes.
			if mode == "verification" {
				if err := os.WriteFile(filepath.Join(slot, "product.py"), []byte("tampered"), 0600); err != nil {
					t.Fatal(err)
				}
			}
			code, stdout, stderr := launcherResult(t, root, "2")
			if code != 1 || stdout != "" || !strings.HasPrefix(stderr, "Colvia could not open its verified runtime:") {
				t.Fatalf("code=%d stdout=%q stderr=%q", code, stdout, stderr)
			}
		})
	}
}

func TestUnwrappedSubprocessExitIsNotProductOutcome(t *testing.T) {
	child := exec.Command(os.Args[0])
	child.Env = append(os.Environ(), helperMode+"=child", helperCode+"=2")
	err := child.Run()
	var ended *exec.ExitError
	if !errors.As(err, &ended) || ended.ExitCode() != 2 {
		t.Fatalf("invalid helper exit: %v", err)
	}
	code, message := outcome(err) // Same shape as a platform-notice subprocess error.
	if code != 1 || !strings.HasPrefix(message, "Colvia could not open its verified runtime:") {
		t.Fatal(code, message)
	}
	if code, message = outcome(nil); code != 0 || message != "" {
		t.Fatal(code, message)
	}
}
