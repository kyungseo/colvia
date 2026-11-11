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


ICON_SHA256 = ""  # Replaced by the source release builder; verified with the payload.


def digest_value(value):
    if not isinstance(value, str) or not re.fullmatch("[0-9a-f]{64}", value):
        raise ValueError("알림 앱의 버전 기록을 확인해 주세요.")
    return value


def regular_bytes(path):
    # The shared Windows observer rejects reparse points in the entire ancestor chain.
    state = windows_path_observation(path)
    if state["directory"] or state["links"] != 1:
        raise ValueError("알림 앱 파일을 확인해 주세요.")
    return path.read_bytes()


def retained_copy(store, source, *, suffix=".exe", expected=None):
    if suffix not in (".exe", ".png"):
        raise ValueError("알림 앱 파일 형식을 확인해 주세요.")
    data = regular_bytes(Path(source))
    identity = hashlib.sha256(data).hexdigest()
    if expected is not None and identity != digest_value(expected):
        raise ValueError("알림 아이콘이 검증한 배포본과 다릅니다.")
    folder = store / "notification-tools"
    folder.mkdir(exist_ok=True)
    windows_path_observation(folder)
    dest = folder / (identity + suffix)
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
    if regular_bytes(dest) != data:
        raise ValueError("알림 앱 파일을 확인해 주세요.")
    return identity


def registration_state(value, *, legacy=False):
    if value is None:
        return None
    if legacy:
        return {"manager": digest_value(value), "icon": None}
    if not isinstance(value, dict) or set(value) != {"manager", "icon"}:
        raise ValueError("알림 등록의 복구 기록을 확인해 주세요.")
    digest_value(value["manager"])
    if value["icon"] is not None:
        digest_value(value["icon"])
    return dict(value)


def registration(store, source, *, enable):
    with exclusive_file_lock(store / "notice-registration.lock"):
        requested, icon = None, None
        if enable:
            icon = retained_copy(store, Path(__file__).with_name("notice-icon.png"),
                                 suffix=".png", expected=digest_value(ICON_SHA256))
            requested = retained_copy(store, source)
        change_registration(store, requested, icon=icon)


def change_registration(store, requested, *, icon=None):
    if requested is None and icon is not None:
        raise ValueError("알림 등록의 요청을 확인해 주세요.")
    target = registration_state({"manager": requested, "icon": icon}) if requested is not None else None
    app, cls = windows_notice_identity(store)
    app_key = BASE + "\\AppUserModelId\\" + app
    class_key = BASE + "\\CLSID\\" + cls
    server = class_key + "\\LocalServer32"
    base_values = {"DisplayName": ("Colvia", winreg.REG_SZ), "CustomActivator": (cls, winreg.REG_SZ)}
    journal = store / "notice-registration.pending"

    def icon_path(identity):
        return store / "notification-tools" / (digest_value(identity) + ".png")

    def app_values(value):
        result = dict(base_values)
        if value["icon"] is not None:
            result["IconUri"] = (str(icon_path(value["icon"])), winreg.REG_SZ)
        return result

    def command(value):
        path = store / "notification-tools" / (value["manager"] + ".exe")
        return ('"' + str(path) + '" notice-activate', winreg.REG_SZ)

    def state():
        return tuple(owned_values(k) for k in (app_key, class_key, server))

    def expected_state(value):
        if value is None:
            return (None, None, None)
        return ((set(), app_values(value)), ({"LocalServer32"}, {}), (set(), {"": command(value)}))

    def verify_icon(value):
        if value is not None and value["icon"] is not None:
            raw = regular_bytes(icon_path(value["icon"]))
            if hashlib.sha256(raw).hexdigest() != value["icon"]:
                raise ValueError("알림 아이콘 파일을 확인해 주세요.")

    def apply(value, *, check_icon=False):
        if check_icon:
            verify_icon(value)
        if value is None:
            for k in (app_key, server, class_key):
                if owned_values(k) is not None:
                    winreg.DeleteKey(HKCU, k)
        else:
            text, kind = command(value)
            with winreg.CreateKey(HKCU, class_key):
                pass
            with winreg.CreateKey(HKCU, server) as key:
                winreg.SetValueEx(key, "", 0, kind, text)
            with winreg.CreateKey(HKCU, app_key) as key:
                for name, (text, kind) in app_values(value).items():
                    winreg.SetValueEx(key, name, 0, kind, text)
                if value["icon"] is None:
                    try:
                        winreg.DeleteValue(key, "IconUri")
                    except FileNotFoundError:
                        pass
            if windows_notice_manager(store).stem != value["manager"]:
                raise ValueError("등록한 알림 앱 버전을 확인해 주세요.")
        if state() != expected_state(value):
            raise ValueError("알림 앱 등록 결과를 확인해 주세요.")
        if check_icon:
            verify_icon(value)

    def restore(previous, candidate):
        # Partial values must belong to the recorded transition, by value name.
        allowed = {}
        commands = set()
        for value in (previous, candidate):
            if value is not None:
                commands.add(command(value))
                for name, item in app_values(value).items():
                    allowed.setdefault(name, set()).add(item)
        a, c, s = state()
        if ((a and (a[0] or any(item not in allowed.get(name, set()) for name, item in a[1].items()))) or
                (c and (c[0] - {"LocalServer32"} or c[1])) or
                (s and (s[0] or set(s[1]) - {""} or ("" in s[1] and s[1][""] not in commands)))):
            raise ValueError("기존 알림 등록의 변경 내역을 확인해 주세요.")
        # Restore exact prior registry values even if its cosmetic PNG is now missing.
        apply(previous)
        journal.unlink()

    if journal.exists():
        pending = load_json(journal)
        if not isinstance(pending, dict):
            raise ValueError("알림 등록의 복구 기록을 확인해 주세요.")
        if set(pending) == {"previous", "requested"}:
            previous, candidate = (registration_state(pending[k], legacy=True) for k in ("previous", "requested"))
        elif (set(pending) == {"schema", "previous", "requested"} and
              type(pending["schema"]) is int and pending["schema"] == 2):
            previous, candidate = (registration_state(pending[k]) for k in ("previous", "requested"))
        else:
            raise ValueError("알림 등록의 복구 기록을 확인해 주세요.")
        restore(previous, candidate)
    a, c, s = state()
    previous = None
    if (a, c, s) != (None, None, None):
        if (not a or a[0] or c != ({"LocalServer32"}, {}) or not s or s[0] or set(s[1]) != {""}):
            raise ValueError("기존 알림 앱 등록을 확인해 주세요.")
        previous_icon = None
        if "IconUri" in a[1]:
            text, kind = a[1]["IconUri"]
            if not isinstance(text, str) or kind != winreg.REG_SZ:
                raise ValueError("기존 알림 아이콘 경로를 확인해 주세요.")
            previous_icon = digest_value(Path(text).stem)
            if text != str(icon_path(previous_icon)):
                raise ValueError("기존 알림 아이콘 경로를 확인해 주세요.")
        previous = registration_state({"manager": windows_notice_manager(store).stem, "icon": previous_icon})
        if state() != expected_state(previous):
            raise ValueError("기존 알림 앱 등록을 확인해 주세요.")
    verify_icon(target)
    if previous == target:
        return
    replace_json(journal, {"schema": 2, "previous": previous, "requested": target})
    try:
        apply(target, check_icon=True)
    except Exception:
        restore(previous, target)
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
        "<text>Colvia · 맡긴 작업</text><text>맡긴 작업에 확인할 내용이 있습니다. 눌러서 상세를 여세요.</text>"
        "</binding></visual><actions><action content=\"보기\" arguments=\"v:" + event +
        "\" activationType=\"foreground\"/></actions></toast>');"
        "$toast=[Windows.UI.Notifications.ToastNotification,Windows.UI.Notifications,ContentType=WindowsRuntime]::new($doc);"
        "[Windows.UI.Notifications.ToastNotificationManager,Windows.UI.Notifications,ContentType=WindowsRuntime]"
        "::CreateToastNotifier('" + app + "').Show($toast)"
    )
    subprocess.run([str(ps), "-NoProfile", "-NonInteractive", "-Command", code], cwd=store,
                   check=True, timeout=12, creationflags=subprocess.CREATE_NO_WINDOW)
