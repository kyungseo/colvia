package main

import (
	"crypto/rand"
	"encoding/hex"
	"encoding/json"
	"errors"
	"os"
	"path/filepath"
	"strings"
	"syscall"
	"time"
	"unsafe"
)

const noticeReadLimit = 60 * time.Second

// Audit only the fixed read operation, not its result body or the environment.
// New files receive an explicit owner-only ACL; existing ACLs never change.
func noticeRead(self string, args ...string) (string, error) {
	if !(len(args) == 1 && args[0] == "notice-identity" || len(args) == 3 && args[0] == "notice-detail" && args[1] == "--event" && validNoticeKey(args[2])) {
		return "", errors.New("notice-read-arguments")
	}
	if err := privateRoot(noticeRoot); err != nil {
		return "", errors.New("notice-log-unavailable")
	}
	// Pin the directory against replacement until its diagnostic file is closed.
	root, err := syscall.CreateFile(utf(noticeRoot), 0x20080, 1, nil, 3, 0x02200000, 0)
	if err != nil {
		return "", errors.New("notice-log-unavailable")
	}
	defer syscall.CloseHandle(root)
	if err = privateRoot(noticeRoot); err != nil {
		return "", errors.New("notice-log-unavailable")
	}
	var id [16]byte
	if _, err = rand.Read(id[:]); err != nil {
		return "", errors.New("notice-log-unavailable")
	}
	path := filepath.Join(noticeRoot, "notice-read-"+hex.EncodeToString(id[:])+".jsonl")
	log, err := createNoticeLog(path)
	if err != nil {
		return "", errors.New("notice-log-unavailable")
	}
	defer log.Close()
	info, err := log.Stat()
	if err != nil {
		return "", errors.New("notice-log-unavailable")
	}
	if err = privateFile(path, info); err != nil {
		return "", errors.New("notice-log-unavailable")
	}
	enc := json.NewEncoder(log)
	started := time.Now().UTC()
	event := ""
	if len(args) == 3 {
		event = args[2]
	}
	if err = enc.Encode(map[string]any{"stage": "started", "operation": args[0], "event": event, "utc": started.Format(time.RFC3339Nano), "limit_seconds": 60}); err != nil {
		return "", errors.New("notice-log-unavailable")
	}
	if err = log.Sync(); err != nil {
		return "", errors.New("notice-log-unavailable")
	}
	command := append([]string{self, "manage", "--management-root", noticeRoot}, args...)
	result := runNoticeProcess(command, noticeRoot, noticeReadLimit, 131072)
	if result.Code == "ok" && strings.TrimSpace(result.Stdout) == "" {
		result.Code = "empty-output"
	}
	if err = enc.Encode(map[string]any{"stage": "finished", "utc": time.Now().UTC().Format(time.RFC3339Nano), "result": result}); err != nil {
		return "", errors.New("notice-log-unavailable")
	}
	if err = log.Sync(); err != nil {
		return "", errors.New("notice-log-unavailable")
	}
	if result.Code != "ok" {
		return "", errors.New("notice-" + result.Code)
	}
	return strings.TrimSpace(result.Stdout), nil
}
func validNoticeKey(key string) bool {
	if len(key) != 32 || key != strings.ToLower(key) {
		return false
	}
	_, err := hex.DecodeString(key)
	return err == nil
}
func noticeFailureText(err error) string {
	if err != nil && err.Error() == "notice-timeout" {
		return "작업 기록 조회가 제한 시간(60초)을 넘었습니다. 기존 기록은 보존돼 있습니다. 프로젝트 채팅에서 결과를 확인하고 알림 진단 기록을 전달해 주세요."
	}
	if err != nil && err.Error() == "notice-log-unavailable" {
		return "알림 진단 기록을 저장할 수 없어 조회를 중단했습니다. 프로젝트 채팅에서 관리 홈 접근 상태를 확인해 주세요."
	}
	return "이 알림의 기록을 열 수 없습니다. 기존 작업 기록은 보존돼 있습니다. 프로젝트 채팅에서 결과와 알림 진단 기록을 확인해 주세요."
}

// Same owner-only protected DACL contract as the existing Windows file adapter.
func noticeSecurity() (*syscall.SecurityAttributes, func(), error) {
	token, err := syscall.OpenCurrentProcessToken()
	if err != nil {
		return nil, nil, err
	}
	defer token.Close()
	owner, err := token.GetTokenUser()
	if err != nil {
		return nil, nil, err
	}
	sid, err := owner.User.Sid.String()
	if err != nil {
		return nil, nil, err
	}
	sddl, err := syscall.UTF16PtrFromString("O:" + sid + "D:P(A;;FA;;;" + sid + ")")
	if err != nil {
		return nil, nil, err
	}
	var descriptor uintptr
	proc := syscall.NewLazyDLL("advapi32.dll").NewProc("ConvertStringSecurityDescriptorToSecurityDescriptorW")
	if err = noticeResult(proc.Call(uintptr(unsafe.Pointer(sddl)), 1, uintptr(unsafe.Pointer(&descriptor)), 0)); err != nil {
		return nil, nil, err
	}
	sa := &syscall.SecurityAttributes{Length: uint32(unsafe.Sizeof(syscall.SecurityAttributes{})), SecurityDescriptor: descriptor}
	return sa, func() { noticeKernel.NewProc("LocalFree").Call(descriptor) }, nil
}
func createNoticeLog(path string) (*os.File, error) {
	sa, free, err := noticeSecurity()
	if err != nil {
		return nil, err
	}
	defer free()
	h, err := syscall.CreateFile(utf(path), 0x40020080, 1, sa, 1, 0x00200080, 0)
	if err != nil {
		return nil, err
	}
	return os.NewFile(uintptr(h), path), nil
}
