// The entry router needs no user Python, PATH lookup, network or writable project.
// It verifies the selected immutable slot before invoking its dedicated Python.
// This source candidate is not an installed or platform-qualified release.
package main

import (
	"bytes"
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"io/fs"
	"os"
	"os/exec"
	"path/filepath"
	"regexp"
	"runtime"
	"sort"
	"strings"
)

type Pointer struct {
	Slot   string `json:"slot"`
	Digest string `json:"manifest_sha256"`
}
type Selection struct {
	Version  int      `json:"version"`
	Selected Pointer  `json:"selected"`
	Recovery *Pointer `json:"recovery"`
	High     uint64   `json:"high_sequence"`
}
type Entry struct {
	Path string `json:"path"`
	Kind string `json:"kind"`
	Mode string `json:"mode"`
	Size int64  `json:"size"`
	SHA  string `json:"sha256"`
}
type Manifest struct {
	Version       int      `json:"version"`
	Release       string   `json:"release"`
	Sequence      uint64   `json:"sequence"`
	OS            string   `json:"os"`
	Arch          string   `json:"architecture"`
	PythonVersion string   `json:"python_version"`
	SQLiteVersion string   `json:"sqlite_version"`
	Python        string   `json:"python"`
	Manager       string   `json:"manager"`
	Product       string   `json:"product"`
	Read          []string `json:"read_capabilities"`
	Write         []string `json:"write_capabilities"`
	Features      []string `json:"features"`
	Inventory     []Entry  `json:"inventory"`
}

var token = regexp.MustCompile(`^[A-Za-z0-9][A-Za-z0-9._-]{0,159}$`)
var digestPattern = regexp.MustCompile(`^[0-9a-f]{64}$`)

func require(ok bool, code string) error {
	if !ok {
		return errors.New(code)
	}
	return nil
}
func sha(raw []byte) string { sum := sha256.Sum256(raw); return hex.EncodeToString(sum[:]) }
func noLinks(path string) error {
	path = filepath.Clean(path)
	if !filepath.IsAbs(path) {
		return errors.New("absolute-management-root-required")
	}
	for current := path; ; current = filepath.Dir(current) {
		info, err := os.Lstat(current)
		if err != nil {
			return err
		}
		if info.Mode()&os.ModeSymlink != 0 {
			return errors.New("linked-runtime-path")
		}
		if current == filepath.Dir(current) {
			break
		}
	}
	return nil
}
func read(path string, limit int64) ([]byte, error) {
	if err := noLinks(path); err != nil {
		return nil, err
	}
	before, err := os.Lstat(path)
	if err != nil {
		return nil, err
	}
	if err := privateFile(path, before); err != nil {
		return nil, err
	}
	if !before.Mode().IsRegular() || before.Size() > limit {
		return nil, errors.New("runtime-file-unavailable")
	}
	f, err := os.Open(path)
	if err != nil {
		return nil, err
	}
	defer f.Close()
	opened, err := f.Stat()
	if err != nil {
		return nil, err
	}
	if !os.SameFile(before, opened) {
		return nil, errors.New("runtime-file-changed")
	}
	raw, err := io.ReadAll(io.LimitReader(f, limit+1))
	if err != nil {
		return nil, err
	}
	after, err := os.Lstat(path)
	if err != nil {
		return nil, err
	}
	if int64(len(raw)) != before.Size() || !os.SameFile(before, after) || !before.ModTime().Equal(after.ModTime()) {
		return nil, errors.New("runtime-file-changed")
	}
	return raw, nil
}

// Reject duplicate names before decoding typed values. Last-name-wins JSON
// must never select a different slot from the manager's canonical reader.
func jsonValue(d *json.Decoder, depth int) error {
	if depth > 64 {
		return errors.New("runtime-json-depth")
	}
	t, err := d.Token()
	if err != nil {
		return err
	}
	delim, container := t.(json.Delim)
	if !container {
		return nil
	}
	switch delim {
	case '{':
		names := map[string]bool{}
		for d.More() {
			key, err := d.Token()
			if err != nil {
				return err
			}
			name, ok := key.(string)
			if !ok || names[name] {
				return errors.New("runtime-json-duplicate-name")
			}
			names[name] = true
			if err := jsonValue(d, depth+1); err != nil {
				return err
			}
		}
		end, err := d.Token()
		if err != nil {
			return err
		}
		if end != json.Delim('}') {
			return errors.New("runtime-json-object")
		}
	case '[':
		for d.More() {
			if err := jsonValue(d, depth+1); err != nil {
				return err
			}
		}
		end, err := d.Token()
		if err != nil {
			return err
		}
		if end != json.Delim(']') {
			return errors.New("runtime-json-array")
		}
	default:
		return errors.New("runtime-json-delimiter")
	}
	return nil
}
func decode(raw []byte, target any) error {
	shape := json.NewDecoder(bytes.NewReader(raw))
	shape.UseNumber()
	if err := jsonValue(shape, 0); err != nil {
		return err
	}
	if _, err := shape.Token(); err != io.EOF {
		return errors.New("runtime-json-trailing-data")
	}
	d := json.NewDecoder(bytes.NewReader(raw))
	d.DisallowUnknownFields()
	if err := d.Decode(target); err != nil {
		return err
	}
	var rest any
	if d.Decode(&rest) != io.EOF {
		return errors.New("runtime-json-trailing-data")
	}
	return nil
}
func portable(path string) bool {
	if path == "" || strings.ContainsAny(path, "\\\x00\r\n\t:") || strings.HasPrefix(path, "/") {
		return false
	}
	for _, p := range strings.Split(path, "/") {
		if p == "" || p == "." || p == ".." || strings.HasSuffix(p, ".") || strings.HasSuffix(p, " ") {
			return false
		}
	}
	return true
}
func localPlatform() (string, string, error) {
	if runtime.GOOS == "darwin" && runtime.GOARCH == "arm64" {
		return "macos", "arm64", nil
	}
	if runtime.GOOS == "windows" && (runtime.GOARCH == "arm64" || runtime.GOARCH == "amd64") {
		arch := runtime.GOARCH
		if arch == "amd64" {
			arch = "x64"
		}
		return "windows", arch, nil
	}
	return "", "", errors.New("runtime-platform-unavailable")
}

// Keep the exact platform/version matrix aligned with updates/slots.py.
// Both implementations consume the shared boundary fixture in their tests.
func supportedPython(platform, arch, version string) bool {
	supportedPlatform := (platform == "macos" && arch == "arm64") ||
		(platform == "windows" && (arch == "arm64" || arch == "x64"))
	return supportedPlatform && (version == "3.14.6" || version == "3.14.7" ||
		(platform == "macos" && arch == "arm64" && version == "3.14.10"))
}

func verifiedCommand(root string, manager, repair bool) ([]string, error) {
	platform, arch, err := localPlatform()
	if err != nil {
		return nil, err
	}
	if err = noLinks(root); err != nil {
		return nil, err
	}
	if err := privateRoot(root); err != nil {
		return nil, err
	}
	runtimeRoot := filepath.Join(root, "runtime")
	if err := privateRoot(runtimeRoot); err != nil {
		return nil, err
	}
	selectionFile := filepath.Join(runtimeRoot, "runtime.json")
	original, err := read(selectionFile, 16384)
	if err != nil {
		return nil, err
	}
	var selection Selection
	if err = decode(original, &selection); err != nil {
		return nil, err
	}
	if selection.Version != 1 || selection.High < 1 {
		return nil, errors.New("runtime-selection-invalid")
	}
	pointer := selection.Selected
	if repair {
		if !manager || selection.Recovery == nil {
			return nil, errors.New("verified-recovery-manager-unavailable")
		}
		pointer = *selection.Recovery
	}
	if !token.MatchString(pointer.Slot) || !digestPattern.MatchString(pointer.Digest) {
		return nil, errors.New("runtime-selection-invalid")
	}
	slot := filepath.Join(runtimeRoot, "slots", pointer.Slot)
	raw, err := read(filepath.Join(slot, "manifest.json"), 4*1024*1024)
	if err != nil {
		return nil, err
	}
	if sha(raw) != pointer.Digest {
		return nil, errors.New("runtime-manifest-mismatch")
	}
	var manifest Manifest
	if err = decode(raw, &manifest); err != nil {
		return nil, err
	}
	if manifest.Version != 1 || manifest.Sequence < 1 || manifest.Sequence > selection.High || manifest.OS != platform || manifest.Arch != arch ||
		!supportedPython(manifest.OS, manifest.Arch, manifest.PythonVersion) || len(manifest.Inventory) == 0 || len(manifest.Inventory) > 100000 {
		return nil, errors.New("runtime-manifest-unsupported")
	}
	expected := map[string]Entry{}
	aliases := map[string]bool{}
	var total int64
	for _, entry := range manifest.Inventory {
		if !portable(entry.Path) || entry.Path == "manifest.json" || entry.Kind != "regular" || !digestPattern.MatchString(entry.SHA) || entry.Size < 0 || entry.Size > 4*1024*1024*1024 ||
			(entry.Mode != "100644" && entry.Mode != "100755") || aliases[strings.ToLower(entry.Path)] {
			return nil, errors.New("runtime-inventory-invalid")
		}
		aliases[strings.ToLower(entry.Path)] = true
		expected[entry.Path] = entry
		total += entry.Size
		if total > 4*1024*1024*1024 {
			return nil, errors.New("runtime-size-limit")
		}
	}
	for _, name := range []string{manifest.Python, manifest.Manager, manifest.Product} {
		if _, ok := expected[name]; !ok {
			return nil, errors.New("runtime-entry-missing")
		}
	}
	if expected[manifest.Python].Mode != "100755" {
		return nil, errors.New("runtime-python-not-executable")
	}
	seen := map[string]bool{}
	err = filepath.WalkDir(slot, func(path string, d fs.DirEntry, walkErr error) error {
		if walkErr != nil {
			return walkErr
		}
		if d.Type()&os.ModeSymlink != 0 {
			return errors.New("linked-runtime-path")
		}
		if d.IsDir() {
			return nil
		}
		relative, e := filepath.Rel(slot, path)
		if e != nil {
			return e
		}
		name := filepath.ToSlash(relative)
		if name == "manifest.json" {
			return nil
		}
		entry, ok := expected[name]
		if !ok {
			return errors.New("runtime-extra-file")
		}
		info, e := d.Info()
		if e != nil {
			return e
		}
		if e = privateFile(path, info); e != nil {
			return e
		}
		if !info.Mode().IsRegular() || info.Size() != entry.Size {
			return errors.New("runtime-file-mismatch")
		}
		f, e := os.Open(path)
		if e != nil {
			return e
		}
		opened, e := f.Stat()
		if e != nil {
			f.Close()
			return e
		}
		if !os.SameFile(info, opened) {
			f.Close()
			return errors.New("runtime-file-changed")
		}
		h := sha256.New()
		n, e := io.Copy(h, io.LimitReader(f, entry.Size+1))
		f.Close()
		if e != nil {
			return e
		}
		after, e := os.Lstat(path)
		if e != nil {
			return e
		}
		if n != entry.Size || hex.EncodeToString(h.Sum(nil)) != entry.SHA || !os.SameFile(info, after) || !info.ModTime().Equal(after.ModTime()) {
			return errors.New("runtime-file-mismatch")
		}
		if runtime.GOOS != "windows" {
			mode := "100644"
			if info.Mode().Perm()&0111 != 0 {
				mode = "100755"
			}
			if mode != entry.Mode {
				return errors.New("runtime-mode-mismatch")
			}
		}
		seen[name] = true
		return nil
	})
	if err != nil {
		return nil, err
	}
	if len(seen) != len(expected) {
		return nil, errors.New("runtime-file-missing")
	}
	final, err := read(selectionFile, 16384)
	if err != nil {
		return nil, err
	}
	if !bytes.Equal(final, original) {
		return nil, errors.New("runtime-selection-changed")
	}
	final, err = read(filepath.Join(slot, "manifest.json"), 4*1024*1024)
	if err != nil {
		return nil, err
	}
	if sha(final) != pointer.Digest {
		return nil, errors.New("runtime-manifest-changed")
	}
	entry := manifest.Product
	if manager {
		entry = manifest.Manager
	}
	result := []string{filepath.Join(slot, filepath.FromSlash(manifest.Python)), "-I", "-B", filepath.Join(slot, filepath.FromSlash(entry)),
		"--management-root", root, "--runtime-slot", pointer.Slot, "--runtime-manifest-sha256", pointer.Digest}
	if repair {
		result = append(result, "--repair")
	}
	return result, nil
}
func invocationArgs(executable string, args []string) []string {
	name := strings.ToLower(filepath.Base(executable))
	if name == "colvia-manage" || name == "colvia-manage.exe" {
		return append([]string{"manage"}, args...)
	}
	return args
}

func hostBoundary(goos string, getenv func(string) string) error {
	if goos == "windows" && (getenv("WSL_INTEROP") != "" || getenv("WSL_DISTRO_NAME") != "") {
		return errors.New("WSL interoperability is not qualified; open native Windows PowerShell or the native desktop app")
	}
	return nil
}

func run(args []string) error {
	if err := hostBoundary(runtime.GOOS, os.Getenv); err != nil {
		return err
	}

	root, err := defaultRoot()
	if err != nil {
		return err
	}
	manager, repair, inspect := false, false, false
	for len(args) > 0 {
		switch args[0] {
		case "--management-root":
			if len(args) < 2 {
				return errors.New("management-root-required")
			}
			root = args[1]
			args = args[2:]
		case "manage":
			manager = true
			args = args[1:]
		case "--repair":
			manager = true
			repair = true
			args = args[1:]
		case "--inspect-only":
			inspect = true
			args = args[1:]
		default:
			goto prepared
		}
	}
prepared:
	command, err := verifiedCommand(root, manager, repair)
	if err != nil {
		return err
	}
	command = append(command, args...)
	if inspect {
		return json.NewEncoder(os.Stdout).Encode(map[string]any{"source_inspection_only": true, "command": command})
	}
	if !repair {
		if handled, err := platformNotice(root, manager, args); handled {
			return err
		}
	}
	return runProduct(command)
}

// Only outcomes from the verified product child receive this classification.
// Other subprocesses (including notification handling) remain launcher errors.
type productEnded struct{ code int }

func (e *productEnded) Error() string { return fmt.Sprintf("product exited with status %d", e.code) }

func runProduct(command []string) error {
	child := exec.Command(command[0], command[1:]...)
	child.Stdin = os.Stdin
	child.Stdout = os.Stdout
	child.Stderr = os.Stderr
	child.Env = os.Environ()
	sort.Strings(child.Env)
	err := child.Run()
	var ended *exec.ExitError
	if errors.As(err, &ended) {
		return &productEnded{code: ended.ExitCode()}
	}
	return err
}

func outcome(err error) (int, string) {
	if err == nil {
		return 0, ""
	}
	var ended *productEnded
	if errors.As(err, &ended) {
		if ended.code < 0 {
			// Unix signal termination has ExitCode -1. Windows reports its
			// process exit code; Windows crash behavior is not qualified here.
			return 1, "Colvia's product process ended abnormally."
		}
		return ended.code, ""
	}
	return 1, "Colvia could not open its verified runtime: " + err.Error()
}

func main() {
	code, message := outcome(run(invocationArgs(os.Args[0], os.Args[1:])))
	if message != "" {
		fmt.Fprintln(os.Stderr, message)
	}
	os.Exit(code)
}
