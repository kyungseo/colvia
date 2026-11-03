// Native Windows user bootstrap. The release builder embeds only the product payload
// and its manifest. Python comes from the pinned upstream ZIP or an identical cache.
package main

import (
	"archive/zip"
	"bytes"
	"crypto/sha256"
	_ "embed"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"io/fs"
	"net/http"
	"os"
	"os/exec"
	"path/filepath"
	"runtime"
	"strings"
	"syscall"
	"time"
	"unsafe"
)

//go:embed catalog.json
var catalog []byte

//go:embed core.zip
var payload []byte

type manifest struct {
	Release, Fixture string
	Runtime, Payload map[string]string
}

func hash(data []byte) string { return fmt.Sprintf("%x", sha256.Sum256(data)) }

// Every existing component must be local and free of reparse points. The store
// is private to a cooperative account. This is not a hostile same-user sandbox.
func plain(path string, dir bool) error {
	parent := filepath.Dir(path)
	if path != parent {
		if err := plain(parent, true); err != nil {
			return err
		}
	}
	st, err := os.Lstat(path)
	if err != nil {
		return err
	}
	a := st.Sys().(*syscall.Win32FileAttributeData).FileAttributes
	if a&syscall.FILE_ATTRIBUTE_REPARSE_POINT != 0 || st.IsDir() != dir || (!dir && !st.Mode().IsRegular()) {
		return fmt.Errorf("unexpected file type: %s", path)
	}
	return nil
}
func read(path string, limit int64) ([]byte, error) {
	if err := plain(path, false); err != nil {
		return nil, err
	}
	f, err := os.Open(path)
	if err != nil {
		return nil, err
	}
	defer f.Close()
	var info syscall.ByHandleFileInformation
	if err = syscall.GetFileInformationByHandle(syscall.Handle(f.Fd()), &info); err != nil {
		return nil, err
	}
	if info.NumberOfLinks != 1 || info.FileAttributes&syscall.FILE_ATTRIBUTE_REPARSE_POINT != 0 {
		return nil, errors.New("shared or redirected file")
	}
	b, err := io.ReadAll(io.LimitReader(f, limit+1))
	if err == nil && int64(len(b)) > limit {
		err = errors.New("size limit exceeded")
	}
	return b, err
}
func makeDir(path string) error {
	if err := plain(filepath.Dir(path), true); err != nil {
		return err
	}
	if err := os.Mkdir(path, 0700); err != nil && !errors.Is(err, fs.ErrExist) {
		return err
	}
	return plain(path, true)
}
func verify(root string, expected map[string]string) error {
	requiredDirs := map[string]bool{".": true}
	for n := range expected {
		for p := filepath.Dir(n); p != "."; p = filepath.Dir(p) {
			requiredDirs[filepath.ToSlash(p)] = true
		}
	}
	seen := 0
	err := filepath.WalkDir(root, func(p string, d fs.DirEntry, e error) error {
		if e != nil {
			return e
		}
		rel, e := filepath.Rel(root, p)
		if e != nil {
			return e
		}
		rel = filepath.ToSlash(rel)
		if d.IsDir() {
			if !requiredDirs[rel] {
				return fmt.Errorf("unexpected directory %s", rel)
			}
			return plain(p, true)
		}
		want, ok := expected[rel]
		if !ok {
			return fmt.Errorf("unexpected member %s", rel)
		}
		b, e := read(p, 64<<20)
		if e != nil {
			return e
		}
		if hash(b) != want {
			return fmt.Errorf("changed file %s", rel)
		}
		seen++
		return nil
	})
	if err == nil && seen != len(expected) {
		err = errors.New("missing files")
	}
	return err
}
func writeNew(path string, b []byte) error {
	f, e := os.OpenFile(path, os.O_CREATE|os.O_EXCL|os.O_WRONLY, 0600)
	if e != nil {
		return e
	}
	_, e = f.Write(b)
	if e == nil {
		e = f.Sync()
	}
	closeErr := f.Close()
	if e == nil {
		e = closeErr
	}
	return e
}
func publishSlot(parent, name string, raw []byte, expected map[string]string) error {
	final := filepath.Join(parent, name)
	if _, e := os.Lstat(final); !errors.Is(e, fs.ErrNotExist) {
		if e != nil {
			return e
		}
		return verify(final, expected)
	}
	stage, e := os.MkdirTemp(parent, ".pending-")
	if e != nil {
		return e
	}
	z, e := zip.NewReader(bytes.NewReader(raw), int64(len(raw)))
	if e != nil {
		return e
	}
	for _, member := range z.File {
		n := member.Name
		want, ok := expected[n]
		if !ok || !fs.ValidPath(n) || !filepath.IsLocal(filepath.FromSlash(n)) || strings.ContainsAny(n, "\\:") {
			return errors.New("undeclared ZIP member")
		}
		in, e := member.Open()
		if e != nil {
			return e
		}
		b, e := io.ReadAll(io.LimitReader(in, (64<<20)+1))
		in.Close()
		if e != nil {
			return e
		}
		if hash(b) != want {
			return fmt.Errorf("archive digest mismatch: %s", n)
		}
		p := filepath.Join(stage, filepath.FromSlash(n))
		if e = os.MkdirAll(filepath.Dir(p), 0700); e != nil {
			return e
		}
		if e = writeNew(p, b); e != nil {
			return e
		}
	}
	if e = verify(stage, expected); e != nil {
		return e
	}
	// Windows MoveFile without REPLACE_EXISTING never displaces another slot.
	from, e := syscall.UTF16PtrFromString(stage)
	if e != nil {
		return e
	}
	to, e := syscall.UTF16PtrFromString(final)
	if e != nil {
		return e
	}
	return syscall.MoveFile(from, to)
}
func loadPython(cache string) ([]byte, error) {
	var b []byte
	var err error
	if cache != "" {
		path, e := filepath.Abs(cache)
		if e != nil {
			return nil, e
		}
		b, err = read(path, pythonSize)
	} else {
		client := http.Client{Timeout: 90 * time.Second, CheckRedirect: func(*http.Request, []*http.Request) error { return http.ErrUseLastResponse }}
		response, e := client.Get(upstream)
		if e != nil {
			return nil, e
		}
		defer response.Body.Close()
		if response.StatusCode != http.StatusOK {
			return nil, fmt.Errorf("upstream HTTP %d", response.StatusCode)
		}
		b, err = io.ReadAll(io.LimitReader(response.Body, pythonSize+1))
	}
	if err != nil {
		return nil, err
	}
	if len(b) != pythonSize || hash(b) != pythonSHA {
		return nil, errors.New("CPython upstream digest mismatch")
	}
	return b, nil
}
func storeRoot(m manifest) (string, error) {
	// kernel32 is a Windows KnownDLL. GetSystemDirectory locates shell32 explicitly.
	kernel := syscall.NewLazyDLL("kernel32.dll")
	var processMachine, nativeMachine uint16
	proc, e := syscall.GetCurrentProcess()
	if e != nil {
		return "", e
	}
	ok, _, e := kernel.NewProc("IsWow64Process2").Call(uintptr(proc), uintptr(unsafe.Pointer(&processMachine)), uintptr(unsafe.Pointer(&nativeMachine)))
	if ok == 0 {
		return "", e
	}
	if runtime.GOARCH != pythonArch || processMachine != 0 || nativeMachine != pythonMachine {
		return "", fmt.Errorf("native Windows %s required", pythonArch)
	}
	token, e := syscall.OpenCurrentProcessToken()
	if e != nil {
		return "", e
	}
	defer token.Close()
	var elevated, used uint32
	if e = syscall.GetTokenInformation(token, 20, (*byte)(unsafe.Pointer(&elevated)), 4, &used); e != nil {
		return "", e
	}
	if used != 4 || elevated != 0 {
		return "", errors.New("use a non-elevated account")
	}
	root := m.Fixture
	if root == "" {
		var sysdir, local [260]uint16
		count, _, e := kernel.NewProc("GetSystemDirectoryW").Call(uintptr(unsafe.Pointer(&sysdir[0])), 260)
		if count == 0 || count >= 260 {
			return "", fmt.Errorf("system directory unavailable: %v", e)
		}
		shell := syscall.NewLazyDLL(filepath.Join(syscall.UTF16ToString(sysdir[:]), "shell32.dll"))
		hr, _, _ := shell.NewProc("SHGetFolderPathW").Call(0, 0x1c, 0, 0, uintptr(unsafe.Pointer(&local[0])))
		if hr != 0 {
			return "", fmt.Errorf("local application data unavailable: %x", hr)
		}
		root = filepath.Join(syscall.UTF16ToString(local[:]), "Colvia")
	}
	vol := filepath.VolumeName(root)
	if len(vol) != 2 || vol[1] != ':' || !filepath.IsAbs(root) {
		return "", errors.New("local absolute path required")
	}
	drive, e := syscall.UTF16PtrFromString(vol + "\\")
	if e != nil {
		return "", e
	}
	kind, _, _ := kernel.NewProc("GetDriveTypeW").Call(uintptr(unsafe.Pointer(drive)))
	var filesystem [32]uint16
	ok, _, e = kernel.NewProc("GetVolumeInformationW").Call(uintptr(unsafe.Pointer(drive)), 0, 0, 0, 0, 0, uintptr(unsafe.Pointer(&filesystem[0])), 32)
	if ok == 0 {
		return "", e
	}
	if kind != 3 || syscall.UTF16ToString(filesystem[:]) != "NTFS" {
		return "", errors.New("fixed local NTFS required")
	}
	return root, plain(filepath.Dir(root), true)
}
func run(args []string) error {
	var m manifest
	if e := json.Unmarshal(catalog, &m); e != nil {
		return e
	}
	if len(args) == 0 || args[0] == "--help" {
		fmt.Println("colvia-manage prepare [--runtime-zip FILE] | install | update | rollback | repair | remove | status | start | view | resume | project | notice-enable | notice-disable")
		return nil
	}
	root, e := storeRoot(m)
	if e != nil {
		return e
	}
	runtimeID := "python-" + pythonSHA[:24]
	slotID := "tool-" + hash(catalog)[:24]
	runtimePath, slot := filepath.Join(root, runtimeID), filepath.Join(root, slotID)
	if args[0] == "prepare" {
		cache := ""
		if len(args) == 3 && args[1] == "--runtime-zip" && args[2] != "" {
			cache = args[2]
		} else if len(args) != 1 {
			return errors.New("prepare [--runtime-zip FILE]")
		}
		if e = makeDir(root); e != nil {
			return e
		}
		lock := filepath.Join(root, "prepare.lock")
		if e = os.Mkdir(lock, 0700); e != nil {
			return fmt.Errorf("check previous preparation and its lock: %w", e)
		}
		defer os.Remove(lock)
		if _, e = os.Lstat(runtimePath); errors.Is(e, fs.ErrNotExist) || cache != "" {
			b, err := loadPython(cache)
			if err != nil {
				return err
			}
			if e = publishSlot(root, runtimeID, b, m.Runtime); e != nil {
				return e
			}
		} else if e != nil {
			return e
		} else if e = verify(runtimePath, m.Runtime); e != nil {
			return e
		}
		if e = publishSlot(root, slotID, payload, m.Payload); e != nil {
			return e
		}
		if e = makeDir(filepath.Join(root, "requests")); e != nil {
			return e
		}
		fmt.Println("전용 Python과 Colvia를 준비했습니다. 프로젝트 폴더에서 colvia-manage install로 연결할 범위를 확인하세요.")
		return nil
	}
	if e = verify(runtimePath, m.Runtime); e != nil {
		return fmt.Errorf("check the dedicated runtime before continuing: %w", e)
	}
	if e = verify(slot, m.Payload); e != nil {
		return fmt.Errorf("check the prepared release before continuing: %w", e)
	}
	self, e := os.Executable()
	if e != nil {
		return e
	}
	if args[0] == "notice-activate" {
		return noticeWindow(self)
	}
	cmd := exec.Command(filepath.Join(runtimePath, "python.exe"), append([]string{"-I", "-B", filepath.Join(slot, "manage.py"), root, self}, args...)...)
	if strings.HasPrefix(args[0], "notice-") {
		cmd.SysProcAttr = &syscall.SysProcAttr{HideWindow: true, CreationFlags: 0x08000000}
	}
	cmd.Stdin = os.Stdin
	cmd.Stdout = os.Stdout
	cmd.Stderr = os.Stderr
	return cmd.Run()
}
func main() {
	err := run(os.Args[1:])
	if err == nil {
		return
	}
	var status *exec.ExitError
	if errors.As(err, &status) {
		os.Exit(status.ExitCode())
	}
	fmt.Fprintln(os.Stderr, "진행을 중단했습니다. 기존 파일과 요청을 보존하고 원인을 확인하세요.", err)
	os.Exit(65)
}
