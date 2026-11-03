"""User-scoped Windows notification registration and fixed, local toast publication."""
import ctypes
import hashlib
import os
from pathlib import Path
import re
import subprocess
import tempfile
import winreg

from hv2ref.continuation import notification_detail, windows_notice_identity, windows_notice_manager
from hv2ref.jsonio import exclusive_file_lock, load_json, windows_path_observation, replace_json

BASE = r"Software\Classes"
HKCU = winreg.HKEY_CURRENT_USER


def owned_values(path):
    try:
        key = winreg.OpenKey(HKCU, path)
    except FileNotFoundError:
        return None
    with key:
        children, count, _ = winreg.QueryInfoKey(key)
        return ({winreg.EnumKey(key, i) for i in range(children)},
                {name: (value, kind) for name, value, kind in (winreg.EnumValue(key, i) for i in range(count))})


def retained_copy(store, source):
    folder = store / "notification-tools"
    folder.mkdir(exist_ok=True)
    windows_path_observation(folder)
    data = Path(source).read_bytes()
    dest = folder / (hashlib.sha256(data).hexdigest() + ".exe")
    if not dest.exists():
        staged = tempfile.NamedTemporaryFile(dir=folder, delete=False)
        try:
            with staged:
                staged.write(data)
                staged.flush()
                os.fsync(staged.fileno())
            try:
                os.rename(staged.name, dest)
            except FileExistsError:
                pass
        finally:
            Path(staged.name).unlink(missing_ok=True)
    st = windows_path_observation(dest)
    if st["directory"] or st["links"] != 1 or dest.read_bytes() != data:
        raise ValueError("알림 앱 파일을 확인해 주세요.")
    return dest.stem


def registration(store, source, *, enable):
    with exclusive_file_lock(store / "notice-registration.lock"):
        requested = retained_copy(store, source) if enable else None
        change_registration(store, requested)


def change_registration(store, requested):
    app, cls = windows_notice_identity(store)
    app_key = BASE + "\\AppUserModelId\\" + app
    class_key = BASE + "\\CLSID\\" + cls
    server = class_key + "\\LocalServer32"
    app_values = {"DisplayName": ("Colvia", winreg.REG_SZ), "CustomActivator": (cls, winreg.REG_SZ)}
    journal = store / "notice-registration.pending"

    def command(digest):
        if not isinstance(digest, str) or not re.fullmatch("[0-9a-f]{64}", digest):
            raise ValueError("알림 앱의 버전 기록을 확인해 주세요.")
        path = store / "notification-tools" / (digest + ".exe")
        return ('"' + str(path) + '" notice-activate', winreg.REG_SZ)

    def state():
        return tuple(owned_values(k) for k in (app_key, class_key, server))

    def apply(digest):
        if digest is None:
            for k in (app_key, server, class_key):
                if owned_values(k) is not None:
                    winreg.DeleteKey(HKCU, k)
            return
        value, kind = command(digest)
        with winreg.CreateKey(HKCU, class_key):
            pass
        with winreg.CreateKey(HKCU, server) as key:
            winreg.SetValueEx(key, "", 0, kind, value)
        with winreg.CreateKey(HKCU, app_key) as key:
            for name, (value, kind) in app_values.items():
                winreg.SetValueEx(key, name, 0, kind, value)
        if windows_notice_manager(store).stem != digest:
            raise ValueError("등록한 알림 앱 버전을 확인해 주세요.")

    def restore(previous, candidate):
        # The store-local pending record is created before the first registry edit.
        # Never clean an unjournaled partial key or an unexpected value/child.
        allowed = {command(d) for d in (previous, candidate) if d is not None}
        a, c, s = state()
        if ((a and (a[0] or not a[1].items() <= app_values.items())) or
                (c and (c[0] - {"LocalServer32"} or c[1])) or
                (s and (s[0] or set(s[1]) - {""} or ("" in s[1] and s[1][""] not in allowed)))):
            raise ValueError("기존 알림 등록의 변경 내역을 확인해 주세요.")
        apply(previous)
        journal.unlink()

    if journal.exists():
        pending = load_json(journal)
        if not isinstance(pending, dict) or set(pending) != {"previous", "requested"}:
            raise ValueError("알림 등록의 복구 기록을 확인해 주세요.")
        restore(pending["previous"], pending["requested"])
    a, c, s = state()
    previous = None
    if (a, c, s) != (None, None, None):
        if a != (set(), app_values) or c != ({"LocalServer32"}, {}) or not s or s[0] or set(s[1]) != {""}:
            raise ValueError("기존 알림 앱 등록을 확인해 주세요.")
        previous = windows_notice_manager(store).stem
    if previous == requested:
        return
    replace_json(journal, {"previous": previous, "requested": requested})
    try:
        apply(requested)
    except Exception:
        restore(previous, requested)
        raise
    journal.unlink()


def handle(store, source, command, event):
    app, cls = windows_notice_identity(store)
    if command in ("notice-enable", "notice-disable"):
        registration(store, source, enable=command == "notice-enable")
        return
    if windows_notice_manager(store) != Path(source):
        raise ValueError("현재 등록된 알림 앱을 사용해 주세요.")
    if command == "notice-identity":
        print(app, cls)
        return
    if not re.fullmatch("[0-9a-f]{32}", event or ""):
        raise ValueError("알림을 다시 확인해 주세요.")
    if command == "notice-detail":
        print(notification_detail(store, event))
        return
    buf = ctypes.create_unicode_buffer(32768)
    size = ctypes.windll.kernel32.GetSystemDirectoryW(buf, len(buf))
    if not 0 < size < len(buf):
        raise ValueError("Windows 알림 도구를 찾을 수 없습니다.")
    ps = Path(buf.value) / "WindowsPowerShell/v1.0/powershell.exe"
    # Values admitted above are hex or derived from the physical store, never Work text.
    code = (
        "$ErrorActionPreference='Stop';"
        "$doc=[Windows.Data.Xml.Dom.XmlDocument,Windows.Data.Xml.Dom.XmlDocument,ContentType=WindowsRuntime]::new();"
        "$doc.LoadXml('<toast launch=\"b:" + event + "\"><visual><binding template=\"ToastGeneric\">"
        "<text>Colvia · 맡긴 작업</text><text>새 소식이 있습니다. 눌러서 작업을 확인하세요.</text>"
        "</binding></visual><actions><action content=\"보기\" arguments=\"v:" + event +
        "\" activationType=\"foreground\"/></actions></toast>');"
        "$toast=[Windows.UI.Notifications.ToastNotification,Windows.UI.Notifications,ContentType=WindowsRuntime]::new($doc);"
        "[Windows.UI.Notifications.ToastNotificationManager,Windows.UI.Notifications,ContentType=WindowsRuntime]"
        "::CreateToastNotifier('" + app + "').Show($toast)"
    )
    subprocess.run([str(ps), "-NoProfile", "-NonInteractive", "-Command", code], cwd=store,
                   check=True, timeout=12, creationflags=subprocess.CREATE_NO_WINDOW)
