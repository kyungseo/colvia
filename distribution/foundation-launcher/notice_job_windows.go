package main

// An owned, non-breakaway job contains the verified read command and every
// descendant. The suspended child is assigned before any child instruction runs.
import (
	"errors"
	"os"
	"runtime"
	"strings"
	"syscall"
	"time"
	"unsafe"
)

var noticeKernel = syscall.NewLazyDLL("kernel32.dll")
var (
	noticeCreateJobObjectW                  = noticeKernel.NewProc("CreateJobObjectW")
	noticeSetInformationJobObject           = noticeKernel.NewProc("SetInformationJobObject")
	noticeQueryInformationJobObject         = noticeKernel.NewProc("QueryInformationJobObject")
	noticeTerminateJobObject                = noticeKernel.NewProc("TerminateJobObject")
	noticeInitializeProcThreadAttributeList = noticeKernel.NewProc("InitializeProcThreadAttributeList")
	noticeUpdateProcThreadAttribute         = noticeKernel.NewProc("UpdateProcThreadAttribute")
	noticeDeleteProcThreadAttributeList     = noticeKernel.NewProc("DeleteProcThreadAttributeList")
	noticeCreateProcessW                    = noticeKernel.NewProc("CreateProcessW")
	noticeAssignProcessToJobObject          = noticeKernel.NewProc("AssignProcessToJobObject")
	noticeResumeThread                      = noticeKernel.NewProc("ResumeThread")
	noticePeekNamedPipe                     = noticeKernel.NewProc("PeekNamedPipe")
)

type noticeBasicLimit struct {
	ProcessTime, JobTime int64
	Flags                uint32
	Minimum, Maximum     uintptr
	Active               uint32
	Affinity             uintptr
	Priority, Scheduling uint32
}
type noticeJobLimit struct {
	Basic                                          noticeBasicLimit
	IO                                             [6]uint64
	ProcessMemory, JobMemory, PeakProcess, PeakJob uintptr
}
type noticeAccounting struct {
	Times                             [4]int64
	Faults, Total, Active, Terminated uint32
}
type noticeStartup struct {
	Info       syscall.StartupInfo
	Attributes uintptr
}
type noticeProcess struct {
	job, process syscall.Handle
	pid          uint32
}
type noticeOutcome struct {
	Code        string `json:"code"`
	Exit        uint32 `json:"exit_code"`
	PID         uint32 `json:"pid"`
	Active      uint32 `json:"active_children"`
	Closed      bool   `json:"closure_confirmed"`
	Elapsed     int64  `json:"elapsed_ms"`
	StdoutBytes int    `json:"stdout_bytes"`
	Stderr      string `json:"stderr"`
	Stdout      string `json:"-"`
}

func noticeResult(ok uintptr, _ uintptr, e error) error {
	if ok != 0 {
		return nil
	}
	if e != syscall.Errno(0) {
		return e
	}
	return errors.New("notice-native-call-failed")
}
func (p noticeProcess) active() (uint32, error) {
	var a noticeAccounting
	e := noticeResult(noticeQueryInformationJobObject.Call(uintptr(p.job), 1, uintptr(unsafe.Pointer(&a)), unsafe.Sizeof(a), 0))
	return a.Active, e
}
func startNoticeProcess(args []string, cwd string, streams [3]syscall.Handle) (p noticeProcess, err error) {
	h, _, e := noticeCreateJobObjectW.Call(0, 0)
	if h == 0 {
		return p, e
	}
	p.job = syscall.Handle(h)
	var pi syscall.ProcessInformation
	assigned := false
	defer func() {
		if pi.Thread != 0 {
			syscall.CloseHandle(pi.Thread)
		}
		if err != nil {
			if pi.Process != 0 {
				var kill error
				if assigned {
					kill = noticeResult(noticeTerminateJobObject.Call(uintptr(p.job), 1))
				} else {
					kill = syscall.TerminateProcess(pi.Process, 1)
				}
				waited, we := syscall.WaitForSingleObject(pi.Process, 5000)
				if kill != nil || we != nil || waited != 0 {
					err = errors.New("notice-spawn-closure-unknown")
				}
				syscall.CloseHandle(pi.Process)
			}
			syscall.CloseHandle(p.job)
		}
	}()
	limit := noticeJobLimit{}
	limit.Basic.Flags = 0x2000 // KILL_ON_JOB_CLOSE; no breakaway.
	if err = noticeResult(noticeSetInformationJobObject.Call(uintptr(p.job), 9, uintptr(unsafe.Pointer(&limit)), unsafe.Sizeof(limit))); err != nil {
		return
	}
	var size uintptr
	noticeInitializeProcThreadAttributeList.Call(0, 1, 0, uintptr(unsafe.Pointer(&size)))
	if size == 0 || size > 1024*1024 {
		err = errors.New("notice-attribute-size")
		return
	}
	attributes := make([]byte, size)
	defer func() { runtime.KeepAlive(attributes) }()
	pinned := runtime.Pinner{}
	pinned.Pin(&attributes[0])
	handles := new([3]syscall.Handle)
	*handles = streams
	pinned.Pin(handles)
	defer pinned.Unpin()
	ap := uintptr(unsafe.Pointer(&attributes[0]))
	if err = noticeResult(noticeInitializeProcThreadAttributeList.Call(ap, 1, 0, uintptr(unsafe.Pointer(&size)))); err != nil {
		return
	}
	defer noticeDeleteProcThreadAttributeList.Call(ap)
	inherited := []syscall.Handle{}
	defer func() {
		for _, h := range inherited {
			if e := syscall.SetHandleInformation(h, 1, 0); e != nil && err == nil {
				err = e
			}
		}
	}()
	for _, h := range streams {
		if err = syscall.SetHandleInformation(h, 1, 1); err != nil {
			return
		}
		inherited = append(inherited, h)
	}
	if err = noticeResult(noticeUpdateProcThreadAttribute.Call(ap, 0, 0x20002, uintptr(unsafe.Pointer(handles)), unsafe.Sizeof(*handles), 0, 0)); err != nil {
		return
	}
	startup := noticeStartup{Attributes: ap}
	startup.Info.Cb = uint32(unsafe.Sizeof(startup))
	startup.Info.Flags = 0x100
	startup.Info.StdInput, startup.Info.StdOutput, startup.Info.StdErr = streams[0], streams[1], streams[2]
	var quoted []string
	for _, a := range args {
		quoted = append(quoted, syscall.EscapeArg(a))
	}
	var exe, line, dir *uint16
	if exe, err = syscall.UTF16PtrFromString(args[0]); err != nil {
		return
	}
	if line, err = syscall.UTF16PtrFromString(strings.Join(quoted, " ")); err != nil {
		return
	}
	if dir, err = syscall.UTF16PtrFromString(cwd); err != nil {
		return
	}
	// Inherit current environment, but only the three explicit stream handles.
	err = noticeResult(noticeCreateProcessW.Call(uintptr(unsafe.Pointer(exe)), uintptr(unsafe.Pointer(line)), 0, 0, 1, 0x08080004, 0, uintptr(unsafe.Pointer(dir)), uintptr(unsafe.Pointer(&startup)), uintptr(unsafe.Pointer(&pi))))
	runtime.KeepAlive(handles)
	runtime.KeepAlive(exe)
	runtime.KeepAlive(line)
	runtime.KeepAlive(dir)
	runtime.KeepAlive(startup)
	if err != nil {
		return
	}
	for _, h := range inherited {
		if err = syscall.SetHandleInformation(h, 1, 0); err != nil {
			return
		}
	}
	inherited = nil
	if err = noticeResult(noticeAssignProcessToJobObject.Call(uintptr(p.job), uintptr(pi.Process))); err != nil {
		return
	}
	assigned = true
	n, _, e := noticeResumeThread.Call(uintptr(pi.Thread))
	if uint32(n) == 0xffffffff {
		err = e
		return
	}
	p.process, p.pid = pi.Process, pi.ProcessId
	return
}

// Poll a single-reader anonymous pipe before reading. No pending ReadFile or
// collector goroutine exists when handles close, including unknown cleanup.
func drainNoticePipe(f *os.File, data *[]byte, limit int) (bool, error) {
	var available uint32
	ok, _, e := noticePeekNamedPipe.Call(f.Fd(), 0, 0, 0, uintptr(unsafe.Pointer(&available)), 0)
	if ok == 0 {
		if e == syscall.ERROR_BROKEN_PIPE {
			return true, nil
		}
		return false, e
	}
	if available == 0 {
		return false, nil
	}
	count := int(available)
	if count > 65536 {
		count = 65536
	}
	if count > limit+1-len(*data) {
		count = limit + 1 - len(*data)
	}
	if count <= 0 {
		return false, nil
	}
	b := make([]byte, count)
	var read uint32
	e = syscall.ReadFile(syscall.Handle(f.Fd()), b, &read, nil)
	if e == syscall.ERROR_BROKEN_PIPE {
		return true, nil
	}
	if e != nil {
		return false, e
	}
	*data = append(*data, b[:read]...)
	return false, nil
}
func runNoticeProcess(args []string, cwd string, seconds time.Duration, limit int) (out noticeOutcome) {
	started := time.Now()
	out.Code = "start-failed"
	out.Active = ^uint32(0)
	defer func() { out.Elapsed = time.Since(started).Milliseconds() }()
	if len(args) == 0 || seconds <= 0 || limit <= 0 {
		return
	}
	stdin, e := os.Open(os.DevNull)
	if e != nil {
		return
	}
	defer stdin.Close()
	stdout, stdoutWriter, e := os.Pipe()
	if e != nil {
		return
	}
	defer stdout.Close()
	defer stdoutWriter.Close()
	stderr, stderrWriter, e := os.Pipe()
	if e != nil {
		return
	}
	defer stderr.Close()
	defer stderrWriter.Close()
	p, e := startNoticeProcess(args, cwd, [3]syscall.Handle{syscall.Handle(stdin.Fd()), syscall.Handle(stdoutWriter.Fd()), syscall.Handle(stderrWriter.Fd())})
	if e != nil {
		out.Code = "spawn-failed"
		out.Stderr = e.Error()
		return
	}
	out.PID = p.pid
	defer syscall.CloseHandle(p.process)
	defer syscall.CloseHandle(p.job)
	stdoutWriter.Close()
	stderrWriter.Close()
	deadline := started.Add(seconds)
	out.Code = "ok"
	var a, b []byte
	closedA, closedB := false, false
	collect := func() error {
		var e error
		if !closedA {
			closedA, e = drainNoticePipe(stdout, &a, limit)
			if e != nil {
				return e
			}
		}
		if !closedB {
			closedB, e = drainNoticePipe(stderr, &b, 8192)
		}
		return e
	}
	for {
		if e = collect(); e != nil {
			out.Code = "pipe-error"
			break
		}
		if len(a) > limit || len(b) > 8192 {
			out.Code = "output-limit"
			break
		}
		active, e := p.active()
		out.Active = active
		if e != nil {
			out.Code = "job-query-failed"
			break
		}
		waited, e := syscall.WaitForSingleObject(p.process, 0)
		if e != nil {
			out.Code = "wait-failed"
			break
		}
		if waited == 0 && active == 0 && closedA && closedB {
			out.Closed = true
			break
		}
		if !time.Now().Before(deadline) {
			out.Code = "timeout"
			break
		}
		time.Sleep(10 * time.Millisecond)
	}
	if !out.Closed {
		kill := noticeResult(noticeTerminateJobObject.Call(uintptr(p.job), 1))
		end := time.Now().Add(5 * time.Second)
		for time.Now().Before(end) {
			active, e := p.active()
			out.Active = active
			waited, we := syscall.WaitForSingleObject(p.process, 0)
			if kill == nil && e == nil && we == nil && active == 0 && waited == 0 {
				out.Closed = true
				break
			}
			time.Sleep(10 * time.Millisecond)
		}
		if !out.Closed {
			out.Code = "closure-unknown"
		}
	}
	// Drain remaining bounded bytes without blocking, even on closure-unknown.
	end := time.Now().Add(time.Second)
	for (!closedA || !closedB) && len(a) <= limit && len(b) <= 8192 && time.Now().Before(end) {
		if e = collect(); e != nil {
			out.Code = "pipe-error"
			break
		}
		time.Sleep(time.Millisecond)
	}
	if out.Code == "ok" && (!closedA || !closedB) {
		out.Code = "collection-unknown"
	}
	if e = syscall.GetExitCodeProcess(p.process, &out.Exit); e != nil {
		out.Code = "exit-unknown"
	}
	out.StdoutBytes = len(a)
	if len(a) > limit {
		a = a[:limit]
	}
	if len(b) > 8192 {
		b = b[:8192]
	}
	out.Stdout = string(a)
	out.Stderr = strings.ToValidUTF8(string(b), "�")
	if out.Code == "ok" && out.Exit != 0 {
		out.Code = "child-failed"
	}
	return
}
