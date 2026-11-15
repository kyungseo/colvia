package main

import (
	"encoding/json"
	"fmt"
	"os"
	"os/exec"
	"path/filepath"
	"strconv"
	"strings"
	"syscall"
	"testing"
	"time"
	"unsafe"
)

func TestNoticeHelperProcess(t *testing.T) {
	for i, a := range os.Args {
		if a != "--notice-helper" || i+1 >= len(os.Args) {
			continue
		}
		switch os.Args[i+1] {
		case "ok":
			fmt.Print("synthetic detail")
			os.Exit(0)
		case "slow":
			time.Sleep(21 * time.Second)
			fmt.Print("delayed detail")
			os.Exit(0)
		case "error":
			fmt.Fprint(os.Stderr, "synthetic failure")
			os.Exit(17)
		case "overflow":
			fmt.Print(strings.Repeat("x", 8192))
			os.Exit(0)
		case "stderr-overflow":
			fmt.Fprint(os.Stderr, strings.Repeat("x", 8193))
			os.Exit(0)
		case "empty":
			os.Exit(0)
		case "hang":
			time.Sleep(time.Minute)
			os.Exit(0)
		case "tree":
			c := exec.Command(os.Args[0], "-test.run=^TestNoticeHelperProcess$", "--", "--notice-helper", "hang")
			c.Stdout = os.Stdout
			c.Stderr = os.Stderr
			if c.Start() != nil {
				os.Exit(97)
			}
			fmt.Printf("descendant=%d", c.Process.Pid)
			os.Exit(0)
		}
		os.Exit(98)
	}
}
func TestNoticeOwnedReadBoundaries(t *testing.T) {
	cwd, err := os.Getwd()
	if err != nil {
		t.Fatal(err)
	}
	cases := []struct {
		mode, code string
		seconds    time.Duration
		limit      int
	}{
		{"ok", "ok", 3 * time.Second, 4096},
		{"error", "child-failed", 3 * time.Second, 4096},
		{"overflow", "output-limit", 3 * time.Second, 128},
		{"empty", "ok", 3 * time.Second, 4096},
		{"stderr-overflow", "output-limit", 3 * time.Second, 4096},
		{"hang", "timeout", 500 * time.Millisecond, 4096},
		{"tree", "timeout", 500 * time.Millisecond, 4096},
		{"slow", "ok", noticeReadLimit, 4096},
	}
	for _, c := range cases {
		t.Run(c.mode, func(t *testing.T) {
			r := runNoticeProcess([]string{os.Args[0], "-test.run=^TestNoticeHelperProcess$", "--", "--notice-helper", c.mode}, cwd, c.seconds, c.limit)
			t.Logf("mode=%s code=%s exit=%d active=%d closed=%t ms=%d stderr=%.128q", c.mode, r.Code, r.Exit, r.Active, r.Closed, r.Elapsed, r.Stderr)
			if r.Code != c.code || !r.Closed || r.Active != 0 {
				t.Fatalf("unexpected outcome: %+v", r)
			}
			if c.mode == "error" && (r.Exit != 17 || r.Stderr != "synthetic failure") {
				t.Fatal(r)
			}
			if c.mode == "tree" && !strings.Contains(r.Stdout, "descendant=") {
				t.Fatal("descendant did not start", r)
			}
			if c.mode == "tree" {
				pid, err := strconv.ParseUint(strings.TrimPrefix(r.Stdout, "descendant="), 10, 32)
				if err != nil {
					t.Fatal(err)
				}
				h, err := syscall.OpenProcess(0x100000, false, uint32(pid))
				if err == nil {
					defer syscall.CloseHandle(h)
					v, e := syscall.WaitForSingleObject(h, 0)
					if e != nil || v != 0 {
						t.Fatal("descendant still alive", pid, e)
					}
				} else if err != syscall.Errno(87) {
					t.Fatal("descendant closure unavailable", err)
				}
			}
			if c.mode == "slow" && (r.Elapsed < 20000 || r.Stdout != "delayed detail") {
				t.Fatal(r)
			}
			if r.Elapsed > c.seconds.Milliseconds()+9500 {
				t.Fatal("not bounded", r.Elapsed)
			}
		})
	}
}
func TestNoticeReadInputsAndUserErrors(t *testing.T) {
	for _, s := range []string{"", strings.Repeat("A", 32), strings.Repeat("g", 32), "../x"} {
		if validNoticeKey(s) {
			t.Fatal(s)
		}
	}
	if !validNoticeKey(strings.Repeat("a", 32)) {
		t.Fatal("valid event refused")
	}
	if noticeReadLimit != 60*time.Second {
		t.Fatal(noticeReadLimit)
	}
	if text, err := noticeRead("unused", "notice-detail", "--event", "bad"); err == nil || text != "" {
		t.Fatal("invalid arguments accepted")
	}
}

func init() {
	noticeReadTestEntry = func() {
		if os.Getenv("COLVIA_NOTICE_READ_TEST") != "1" || len(os.Args) < 4 || os.Args[1] != "manage" {
			return
		}
		root := os.Args[3]
		if privateRoot(root) != nil {
			os.Exit(91)
		}
		// Prove the pinned parent permits the same protected child file access.
		f, err := createNoticeLog(filepath.Join(root, "synthetic-child.json"))
		if err != nil {
			os.Exit(92)
		}
		f.WriteString("synthetic")
		f.Close()
		fmt.Print("synthetic identity")
		os.Exit(0)
	}
}
func TestNoticePrivateAudit(t *testing.T) {
	root := filepath.Join(t.TempDir(), "owner-only")
	sa, free, err := noticeSecurity()
	if err != nil {
		t.Fatal(err)
	}
	defer free()
	proc := noticeKernel.NewProc("CreateDirectoryW")
	if err = noticeResult(proc.Call(uintptr(unsafe.Pointer(utf(root))), uintptr(unsafe.Pointer(sa)))); err != nil {
		t.Fatal(err)
	}
	if err = privateRoot(root); err != nil {
		t.Fatal(err)
	}
	old := noticeRoot
	noticeRoot = root
	defer func() { noticeRoot = old }()
	t.Setenv("COLVIA_NOTICE_READ_TEST", "1")
	text, err := noticeRead(os.Args[0], "notice-identity")
	if err != nil || text != "synthetic identity" {
		t.Fatal(text, err)
	}
	files, err := filepath.Glob(filepath.Join(root, "notice-read-*.jsonl"))
	if err != nil || len(files) != 1 {
		t.Fatal(files, err)
	}
	info, err := os.Stat(files[0])
	if err != nil {
		t.Fatal(err)
	}
	if err = privateFile(files[0], info); err != nil {
		t.Fatal(err)
	}
	raw, err := os.ReadFile(files[0])
	if err != nil {
		t.Fatal(err)
	}
	lines := strings.Split(strings.TrimSpace(string(raw)), "\n")
	if len(lines) != 2 {
		t.Fatal(string(raw))
	}
	var value map[string]any
	if err = json.Unmarshal([]byte(lines[1]), &value); err != nil {
		t.Fatal(err)
	}
	result := value["result"].(map[string]any)
	if value["stage"] != "finished" || result["code"] != "ok" || result["closure_confirmed"] != true {
		t.Fatal(value)
	}
	if strings.Contains(string(raw), "synthetic identity") {
		t.Fatal("body copied to audit")
	}
	t.Log("explicit private log, pinned parent child access, two audit records passed")
}
