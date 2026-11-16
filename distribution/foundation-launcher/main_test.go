package main

import (
	"encoding/json"
	"os"
	"path/filepath"
	"strings"
	"testing"
)

func fixture(t *testing.T) (string, string) {
	t.Helper()
	root := t.TempDir()
	if err := os.Chmod(root, 0700); err != nil {
		t.Fatal(err)
	}
	slot := filepath.Join(root, "runtime", "slots", "one")
	if err := os.MkdirAll(slot, 0700); err != nil {
		t.Fatal(err)
	}
	platform, arch, err := localPlatform()
	if err != nil {
		t.Skip(err)
	}
	manifest := Manifest{Version: 1, Release: "synthetic-one", Sequence: 1, OS: platform, Arch: arch, PythonVersion: "3.14.7", SQLiteVersion: "3.54.0", Python: "python", Manager: "manager.py", Product: "product.py", Read: []string{"foundation-v1"}, Write: []string{"foundation-v1"}, Features: []string{"ordinary"}}
	for _, name := range []string{"python", "manager.py", "product.py"} {
		raw := []byte("Synthetic unexecutable file " + name)
		mode := os.FileMode(0600)
		gm := "100644"
		if name == "python" {
			mode = 0700
			gm = "100755"
		}
		if err := os.WriteFile(filepath.Join(slot, name), raw, mode); err != nil {
			t.Fatal(err)
		}
		manifest.Inventory = append(manifest.Inventory, Entry{Path: name, Kind: "regular", Mode: gm, Size: int64(len(raw)), SHA: sha(raw)})
	}
	raw, _ := json.Marshal(manifest)
	if err := os.WriteFile(filepath.Join(slot, "manifest.json"), raw, 0600); err != nil {
		t.Fatal(err)
	}
	selection := Selection{Version: 1, Selected: Pointer{Slot: "one", Digest: sha(raw)}, High: 1}
	raw, _ = json.Marshal(selection)
	if err := os.WriteFile(filepath.Join(root, "runtime", "runtime.json"), raw, 0600); err != nil {
		t.Fatal(err)
	}
	if _, err := verifiedCommand(root, false, false); err != nil {
		t.Fatal("invalid baseline fixture", err)
	}
	return root, slot
}
func TestVerifiedCommandIgnoresUserPythonPath(t *testing.T) {
	root, slot := fixture(t)
	t.Setenv("PATH", "/not/a/python/path")
	t.Setenv("PYTHONHOME", "/not/a/python/home")
	for _, manager := range []bool{false, true} {
		command, err := verifiedCommand(root, manager, false)
		if err != nil {
			t.Fatal(err)
		}
		if command[0] != filepath.Join(slot, "python") || command[1] != "-I" || command[2] != "-B" {
			t.Fatal(command)
		}
	}
}
func TestCorruptedAndExtraFilesRefuse(t *testing.T) {
	for _, change := range []string{"changed", "extra", "missing", "symlink"} {
		t.Run(change, func(t *testing.T) {
			root, slot := fixture(t)
			path := filepath.Join(slot, "product.py")
			switch change {
			case "changed":
				os.WriteFile(path, []byte("different"), 0600)
			case "extra":
				os.WriteFile(filepath.Join(slot, "extra.py"), nil, 0600)
			case "missing":
				os.Remove(path)
			case "symlink":
				os.Remove(path)
				os.Symlink("manager.py", path)
			}
			if _, err := verifiedCommand(root, false, false); err == nil {
				t.Fatal("unsafe runtime accepted")
			}
		})
	}
}
func TestSelectionDoesNotEscapeSlot(t *testing.T) {
	root, _ := fixture(t)
	p := filepath.Join(root, "runtime", "runtime.json")
	raw, _ := os.ReadFile(p)
	raw = []byte(strings.Replace(string(raw), `"slot":"one"`, `"slot":"../one"`, 1))
	os.WriteFile(p, raw, 0600)
	if _, err := verifiedCommand(root, false, false); err == nil {
		t.Fatal("unsafe slot")
	}
}
func TestRecoveryIsExplicitAndRequiresRecordedVerifiedSlot(t *testing.T) {
	root, _ := fixture(t)
	if _, err := verifiedCommand(root, true, true); err == nil {
		t.Fatal("invented recovery")
	}
	if _, err := verifiedCommand(root, false, true); err == nil {
		t.Fatal("product repair launch")
	}
}
func TestManifestDigestIsRequiredBeforeExecution(t *testing.T) {
	root, slot := fixture(t)
	os.WriteFile(filepath.Join(slot, "manifest.json"), []byte("{}"), 0600)
	if _, err := verifiedCommand(root, false, false); err == nil {
		t.Fatal("unverified manifest")
	}
}

func TestDuplicateAndTrailingJSONRefused(t *testing.T) {
	for _, raw := range []string{`{"version":1,"version":2}`, `{"selected":{"slot":"one","slot":"two"}}`, `{} {}`, `null {}`} {
		var target Selection
		if err := decode([]byte(raw), &target); err == nil {
			t.Fatal("ambiguous JSON accepted", raw)
		}
	}
}
func TestSharedAndHardlinkedFileRefuses(t *testing.T) {
	for _, how := range []string{"shared", "hardlinked"} {
		t.Run(how, func(t *testing.T) {
			root, slot := fixture(t)
			p := filepath.Join(slot, "product.py")
			if how == "shared" {
				if err := os.Chmod(p, 0666); err != nil {
					t.Fatal(err)
				}
			} else {
				if err := os.Link(p, filepath.Join(t.TempDir(), "other")); err != nil {
					t.Fatal(err)
				}
			}
			if _, err := verifiedCommand(root, false, false); err == nil {
				t.Fatal("unsafe file accepted")
			}
		})
	}
}

func TestManagerAliasUsesSameVerifiedEntry(t *testing.T) {
	for _, name := range []string{"colvia-manage", "colvia-manage.exe", "COLVIA-MANAGE.EXE"} {
		args := invocationArgs(filepath.Join("fixture", name), []string{"notice-detail", "--event", "synthetic"})
		if strings.Join(args, " ") != "manage notice-detail --event synthetic" {
			t.Fatal(args)
		}
	}
	args := invocationArgs("colvia", []string{"ordinary", "list"})
	if strings.Join(args, " ") != "ordinary list" {
		t.Fatal(args)
	}
}

func TestVisibleWSLInteropRefusesBeforeAuthorityResolution(t *testing.T) {
	for _, key := range []string{"WSL_INTEROP", "WSL_DISTRO_NAME"} {
		env := func(name string) string {
			if name == key {
				return "synthetic"
			}
			return ""
		}
		if hostBoundary("windows", env) == nil {
			t.Fatal("interop admitted")
		}
		if hostBoundary("darwin", env) != nil {
			t.Fatal("unrelated platform changed")
		}
	}
	if hostBoundary("windows", func(string) string { return "" }) != nil {
		t.Fatal("native Windows refused")
	}
}

func TestSupportedPythonSharedBoundaryMatrix(t *testing.T) {
	raw, err := os.ReadFile("../../tests/fixtures/foundation-runtime-versions.json")
	if err != nil {
		t.Fatal(err)
	}
	var rows []struct {
		OS      string `json:"os"`
		Arch    string `json:"architecture"`
		Version string `json:"version"`
		Allowed bool   `json:"allowed"`
	}
	if err := json.Unmarshal(raw, &rows); err != nil {
		t.Fatal(err)
	}
	if len(rows) < 40 {
		t.Fatal("incomplete boundary table")
	}
	for _, row := range rows {
		if got := supportedPython(row.OS, row.Arch, row.Version); got != row.Allowed {
			t.Errorf("%s/%s/%q: got %v want %v", row.OS, row.Arch, row.Version, got, row.Allowed)
		}
	}
}
func TestVerifiedCommandExactRuntimeVersion(t *testing.T) {
	for _, version := range []string{"3.14.10", "3.14.11", "3.14.10-custom"} {
		t.Run(version, func(t *testing.T) {
			root, slot := fixture(t)
			path := filepath.Join(slot, "manifest.json")
			raw, err := os.ReadFile(path)
			if err != nil {
				t.Fatal(err)
			}
			var manifest Manifest
			if err := json.Unmarshal(raw, &manifest); err != nil {
				t.Fatal(err)
			}
			manifest.PythonVersion = version
			raw, err = json.Marshal(manifest)
			if err != nil {
				t.Fatal(err)
			}
			if err := os.WriteFile(path, raw, 0600); err != nil {
				t.Fatal(err)
			}
			selection := Selection{Version: 1, Selected: Pointer{Slot: "one", Digest: sha(raw)}, High: 1}
			selected, err := json.Marshal(selection)
			if err != nil {
				t.Fatal(err)
			}
			if err := os.WriteFile(filepath.Join(root, "runtime", "runtime.json"), selected, 0600); err != nil {
				t.Fatal(err)
			}
			command, err := verifiedCommand(root, true, false)
			allowed := manifest.OS == "macos" && manifest.Arch == "arm64" && version == "3.14.10"
			if allowed && (err != nil || len(command) == 0) {
				t.Fatalf("accepted candidate failed: %v", err)
			}
			if !allowed && (err == nil || err.Error() != "runtime-manifest-unsupported") {
				t.Fatalf("unsupported candidate accepted: %v", err)
			}
		})
	}
}

func TestNativeVerifiedEntryRejectsDuplicates(t *testing.T) {
	cases := [][]string{
		{"--management-root", "one", "--management-root", "one", "guide"},
		{"--management-root", "one", "guide", "--management-root=two"},
		{"--management-root", "one", "manage", "--json", "--runtime-slot=other", "status"},
		{"--management-root", "one", "--repair", "repair-preview", "--runtime-manifest-sha256", "other"},
		{"--management-root", "one", "manage", "--json", "--repair", "repair-preview"},
		{"--management-root", "one", "--repair", "--repair", "repair-preview"},
		{"--management-root", "one", "--root", "a", "--root=b", "guide"},
		{"--management-root", "one", "manage", "--receiver-source", "other", "notice-detail"},
	}
	for _, args := range cases {
		err := run(args)
		if err == nil || (!strings.Contains(err.Error(), "duplicate-") && err.Error() != "unexpected-forwarded-runtime-option") {
			t.Errorf("%q did not stop at the argument boundary: %v", args, err)
		}
	}
	if err := validateForwardedArgs([]string{"--root", "a", "--", "--runtime-slot", "literal"}); err != nil {
		t.Fatal(err)
	}
}
