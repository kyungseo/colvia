// Source-reused native callback/window; foundation manager supplies identity and detail.
package main

import (
	"encoding/hex"
	"errors"
	"runtime"
	"strings"
	"syscall"
	"time"
	"unsafe"
)

var noticeRoot string
var appID string
var cls syscall.GUID
var callbackID = syscall.GUID{Data1: 0x53e31837, Data2: 0x6600, Data3: 0x4a81, Data4: [8]byte{0x93, 0x95, 0x75, 0xcf, 0xfe, 0x74, 0x6f, 0x94}}
var unknown = syscall.GUID{Data4: [8]byte{0xc0, 0, 0, 0, 0, 0, 0, 0x46}}
var factoryID = syscall.GUID{Data1: 1, Data4: unknown.Data4}
var factory, callback struct{ vt *uintptr }
var ftable [5]uintptr
var ctable [4]uintptr
var inbox = make(chan string, 4)

func ptr[T any](p *T) uintptr { return uintptr(unsafe.Pointer(p)) }
func str(p uintptr, limit int) string {
	if p == 0 {
		return ""
	}
	a := unsafe.Slice((*uint16)(unsafe.Pointer(p)), limit)
	for i, c := range a {
		if c == 0 {
			return syscall.UTF16ToString(a[:i])
		}
	}
	return ""
}
func qi(self, iid, out uintptr) uintptr {
	if iid == 0 || out == 0 {
		return 0x80004003
	}
	target := (*uintptr)(unsafe.Pointer(out))
	*target = 0
	id := *(*syscall.GUID)(unsafe.Pointer(iid))
	if id != unknown && !(self == ptr(&factory) && id == factoryID) && !(self == ptr(&callback) && id == callbackID) {
		return 0x80004002
	}
	*target = self
	return 0
}
func create(self, outer, iid, out uintptr) uintptr {
	if outer != 0 {
		return 0x80040110
	}
	return qi(ptr(&callback), iid, out)
}
func activate(self, app, args, data, count uintptr) uintptr {
	key := str(args, 101)
	if str(app, 64) != appID || count != 0 || (len(key) != 34 && len(key) != 99) || (key[:2] != "v:" && key[:2] != "b:") {
		return 0x80070057
	}
	if _, err := hex.DecodeString(key[2:34]); err != nil || strings.ToLower(key) != key || (len(key) == 99 && (key[34] != ':' || !digestPattern.MatchString(key[35:]))) {
		return 0x80070057
	}
	select {
	case inbox <- key[2:]:
		return 0
	default:
		return 0x80004005
	}
}

var user = syscall.NewLazyDLL("user32.dll")
var ole = syscall.NewLazyDLL("ole32.dll")

func utf(s string) *uint16 {
	p, e := syscall.UTF16PtrFromString(s)
	if e != nil {
		panic(e)
	}
	return p
}

// Use a top-level window class with standard close and paint handling.
// A STATIC control paints its caption again inside the client area.
func registerNoticeWindow() (*uint16, uintptr, error) {
	module, _, err := syscall.NewLazyDLL("kernel32.dll").NewProc("GetModuleHandleW").Call(0)
	if module == 0 {
		return nil, 0, err
	}
	name := utf("ColviaWorkNoticeWindow")
	type windowClass struct {
		size, style                        uint32
		procedure                          uintptr
		classExtra, windowExtra            int32
		instance, icon, cursor, background uintptr
		menu, name                         *uint16
		smallIcon                          uintptr
	}
	cursor, _, _ := user.NewProc("LoadCursorW").Call(0, 32512)
	wc := windowClass{procedure: user.NewProc("DefWindowProcW").Addr(), instance: module, cursor: cursor, background: 6, name: name}
	// Resource 101 is bundled with this executable. Icon failure must not block review.
	loadIcon := func(metricX, metricY uintptr) uintptr {
		w, _, _ := user.NewProc("GetSystemMetrics").Call(metricX)
		h, _, _ := user.NewProc("GetSystemMetrics").Call(metricY)
		icon, _, _ := user.NewProc("LoadImageW").Call(module, 101, 1, w, h, 0x8000) // LR_SHARED
		return icon
	}
	wc.icon = loadIcon(11, 12)      // SM_CXICON, SM_CYICON
	wc.smallIcon = loadIcon(49, 50) // SM_CXSMICON, SM_CYSMICON
	wc.size = uint32(unsafe.Sizeof(wc))
	atom, _, err := user.NewProc("RegisterClassExW").Call(ptr(&wc))
	if atom == 0 {
		return nil, 0, err
	}
	return name, module, nil
}

func noticeWindow(self string, root string) error {
	noticeRoot = root
	runtime.LockOSThread()
	defer runtime.UnlockOSThread()
	syscall.NewLazyDLL("kernel32.dll").NewProc("FreeConsole").Call()
	ids, err := noticeRead(self, "notice-identity")
	if err != nil {
		return err
	}
	fields := strings.Fields(ids)
	if len(fields) != 2 {
		return errors.New("등록한 알림 앱 정보를 확인해 주세요.")
	}
	appID = fields[0]
	hr, _, _ := ole.NewProc("CLSIDFromString").Call(ptr(utf(fields[1])), ptr(&cls))
	if int32(hr) < 0 {
		return errors.New("알림 앱 식별값을 확인해 주세요.")
	}
	add := syscall.NewCallback(func(self uintptr) uintptr { return 2 })
	release := syscall.NewCallback(func(self uintptr) uintptr { return 1 })
	ftable = [5]uintptr{syscall.NewCallback(qi), add, release, syscall.NewCallback(create), syscall.NewCallback(func(a, b uintptr) uintptr { return 0 })}
	ctable = [4]uintptr{ftable[0], add, release, syscall.NewCallback(activate)}
	factory.vt = &ftable[0]
	callback.vt = &ctable[0]
	hr, _, _ = ole.NewProc("CoInitializeEx").Call(0, 0)
	if int32(hr) < 0 {
		return errors.New("Windows 알림 수신을 시작할 수 없습니다.")
	}
	defer ole.NewProc("CoUninitialize").Call()
	var cookie uint32
	hr, _, _ = ole.NewProc("CoRegisterClassObject").Call(ptr(&cls), ptr(&factory), 4, 1, ptr(&cookie))
	if int32(hr) < 0 {
		return errors.New("Windows 알림 수신기를 등록할 수 없습니다.")
	}
	defer ole.NewProc("CoRevokeClassObject").Call(uintptr(cookie))
	class, module, err := registerNoticeWindow()
	if err != nil {
		return err
	}
	defer user.NewProc("UnregisterClassW").Call(ptr(class), module)
	var window, editor uintptr
	var msg [64]byte
	type rendered struct {
		sequence uint64
		text     string
		final    bool
	}
	results := make(chan rendered, 4)
	var sequence uint64
	busy := false
	pending := ""
	deadline := time.Now().Add(time.Minute)
	for window != 0 || time.Now().Before(deadline) {
		for {
			ok, _, _ := user.NewProc("PeekMessageW").Call(ptr(&msg[0]), 0, 0, 0, 1)
			if ok == 0 {
				break
			}
			user.NewProc("TranslateMessage").Call(ptr(&msg[0]))
			user.NewProc("DispatchMessageW").Call(ptr(&msg[0]))
		}
		if window != 0 {
			ok, _, _ := user.NewProc("IsWindow").Call(window)
			if ok == 0 {
				return nil
			}
		}
		// Only the newest notification may replace the text in this window.
		select {
		case id := <-inbox:
			sequence++
			pending = id
			if window == 0 {
				window, _, _ = user.NewProc("CreateWindowExW").Call(0, ptr(class), ptr(utf("Colvia · 맡긴 작업")), 0x10ca0000, 100, 100, 640, 380, 0, 0, module, 0)
				if window == 0 {
					return errors.New("상세 창을 열 수 없습니다.")
				}
				editor, _, _ = user.NewProc("CreateWindowExW").Call(0x200, ptr(utf("EDIT")), ptr(utf("")), 0x50210844, 8, 8, 606, 312, window, 0, module, 0)
				if editor == 0 {
					return errors.New("상세 내용을 표시할 수 없습니다.")
				}
				font, _, _ := syscall.NewLazyDLL("gdi32.dll").NewProc("GetStockObject").Call(17)
				if font != 0 {
					user.NewProc("SendMessageW").Call(editor, 0x30, font, 1)
				}
			}
			user.NewProc("SetWindowTextW").Call(editor, ptr(utf("작업 기록을 확인하고 있습니다.")))
			user.NewProc("ShowWindow").Call(window, 5)
			user.NewProc("SetForegroundWindow").Call(window)
		case data := <-results:
			if data.final {
				busy = false
			}
			if data.sequence == sequence {
				user.NewProc("SetWindowTextW").Call(editor, ptr(utf(data.text)))
			}
		default:
			time.Sleep(25 * time.Millisecond)
		}
		if !busy && pending != "" {
			id := pending
			pending = ""
			busy = true
			go func(n uint64, key string) {
				event, digest, ok := strings.Cut(key, ":")
				if !ok {
					results <- rendered{n, "이전 알림입니다. 프로젝트에서 해당 작업의 결과를 확인해 주세요.", true}
					return
				}
				args := []string{"notice-original", "--event", event, "--route-sha256", digest}
				text, err := noticeRead(self, args...)
				if err != nil || text == "" {
					results <- rendered{n, noticeFailureText(err), true}
					return
				}
				format := func(s string) string { return strings.ReplaceAll(strings.ReplaceAll(s, "\x00", "�"), "\n", "\r\n") }
				results <- rendered{n, format(text + "\n\n현재 작업 상태를 확인하고 있습니다."), false}
				args[0] = "notice-detail"
				text, err = noticeRead(self, args...)
				if err != nil || text == "" {
					text = noticeFailureText(err)
				}
				results <- rendered{n, format(text), true}
			}(sequence, id)
		}
	}
	return nil
}
