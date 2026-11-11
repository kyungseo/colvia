package main

// Read-only owner/DACL verification. This never changes an ACL or privilege.
// Native qualification remains separate from cross compilation.
import (
	"errors"
	"os"
	"path/filepath"
	"strings"
	"syscall"
	"unsafe"
)

type aclHeader struct {
	Revision, Unused      byte
	Size, Count, Reserved uint16
}
type aceHeader struct {
	Kind, Flags byte
	Size        uint16
	Mask        uint32
}

func privateFile(path string, info os.FileInfo) error { return privateWindows(path, info, false) }
func privateRoot(path string) error {
	info, err := os.Lstat(path)
	if err != nil {
		return err
	}
	if !info.IsDir() {
		return errors.New("runtime-root-not-private")
	}
	return privateWindows(path, info, true)
}
func privateWindows(path string, info os.FileInfo, directory bool) error {
	volume := filepath.VolumeName(path)
	if len(volume) != 2 || volume[1] != ':' || !filepath.IsAbs(path) || strings.HasPrefix(path, `\\`) {
		return errors.New("runtime-local-volume-required")
	}
	name, err := syscall.UTF16PtrFromString(path)
	if err != nil {
		return err
	}
	// READ_CONTROL | FILE_READ_ATTRIBUTES; open reparse point itself and refuse.
	handle, err := syscall.CreateFile(name, 0x20080, 7, nil, 3, 0x02200000, 0)
	if err != nil {
		return err
	}
	defer syscall.CloseHandle(handle)
	var native syscall.ByHandleFileInformation
	if err = syscall.GetFileInformationByHandle(handle, &native); err != nil {
		return err
	}
	if native.FileAttributes&0x400 != 0 || (native.FileAttributes&0x10 != 0) != directory || (!directory && native.NumberOfLinks != 1) {
		return errors.New("runtime-unsafe-native-file")
	}
	// Compare the independently opened path to the file observed by the reader.
	f, err := os.Open(path)
	if err != nil {
		return err
	}
	opened, err := f.Stat()
	f.Close()
	if err != nil {
		return err
	}
	if !os.SameFile(info, opened) {
		return errors.New("runtime-file-changed")
	}
	var check syscall.ByHandleFileInformation
	checkHandle, err := syscall.CreateFile(name, 0x20080, 7, nil, 3, 0x02200000, 0)
	if err != nil {
		return err
	}
	err = syscall.GetFileInformationByHandle(checkHandle, &check)
	syscall.CloseHandle(checkHandle)
	if err != nil {
		return err
	}
	if check.VolumeSerialNumber != native.VolumeSerialNumber || check.FileIndexHigh != native.FileIndexHigh || check.FileIndexLow != native.FileIndexLow {
		return errors.New("runtime-file-changed")
	}
	token, err := syscall.OpenCurrentProcessToken()
	if err != nil {
		return err
	}
	defer token.Close()
	user, err := token.GetTokenUser()
	if err != nil {
		return err
	}
	userSID, err := user.User.Sid.String()
	if err != nil {
		return err
	}
	adv := syscall.NewLazyDLL("advapi32.dll")
	kernel := syscall.NewLazyDLL("kernel32.dll")
	var owner, dacl, descriptor uintptr
	result, _, _ := adv.NewProc("GetSecurityInfo").Call(uintptr(handle), 1, 5, uintptr(unsafe.Pointer(&owner)), 0, uintptr(unsafe.Pointer(&dacl)), 0, uintptr(unsafe.Pointer(&descriptor)))
	if result != 0 {
		return syscall.Errno(result)
	}
	if descriptor == 0 {
		return errors.New("runtime-security-unavailable")
	}
	defer kernel.NewProc("LocalFree").Call(descriptor)
	if owner == 0 || dacl == 0 {
		return errors.New("runtime-file-not-private")
	}
	ownerSID, err := (*syscall.SID)(unsafe.Pointer(owner)).String()
	if err != nil {
		return err
	}
	if ownerSID != userSID {
		return errors.New("runtime-file-not-owned")
	}
	var control uint16
	var revision uint32
	ok, _, e := adv.NewProc("GetSecurityDescriptorControl").Call(descriptor, uintptr(unsafe.Pointer(&control)), uintptr(unsafe.Pointer(&revision)))
	if ok == 0 {
		return e
	}
	if directory && control&0x1000 == 0 {
		return errors.New("runtime-dacl-not-protected")
	}
	acl := (*aclHeader)(unsafe.Pointer(dacl))
	if acl.Count == 0 || acl.Count > 32 || acl.Size < 8 {
		return errors.New("runtime-dacl-unavailable")
	}
	var allowed uint32
	for i := uint16(0); i < acl.Count; i++ {
		var ace uintptr
		ok, _, e = adv.NewProc("GetAce").Call(dacl, uintptr(i), uintptr(unsafe.Pointer(&ace)))
		if ok == 0 {
			return e
		}
		if ace < dacl+8 || ace+16 > dacl+uintptr(acl.Size) {
			return errors.New("runtime-ace-unavailable")
		}
		a := (*aceHeader)(unsafe.Pointer(ace))
		if a.Kind != 0 || a.Flags&8 != 0 || a.Size < 16 || ace+uintptr(a.Size) > dacl+uintptr(acl.Size) {
			return errors.New("runtime-ace-unavailable")
		}
		sid, err := (*syscall.SID)(unsafe.Pointer(ace + 8)).String()
		if err != nil {
			return err
		}
		if sid != userSID {
			return errors.New("runtime-file-not-private")
		}
		allowed |= a.Mask
	}
	if allowed&0x1f01ff != 0x1f01ff {
		return errors.New("runtime-owner-access-incomplete")
	}
	return nil
}
