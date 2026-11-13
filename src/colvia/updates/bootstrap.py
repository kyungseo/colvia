"""Build-time rendering of pinned first-install/repair entry scripts.

The release builder verifies a normalized bundle before producing a script. The
script contains a concrete HTTPS asset identity, not a floating latest download.
The pinned manager owns existing-install trust verification and version choice.
No public URL, signing key or usable release command is invented by this module.
"""
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlsplit
import hashlib,re,stat,zipfile
from ..codec import require,decode_canonical
from ..tree import canonical_entries
from ..worker_state import path_namespace
from .package import _portable
from .space import STAGING_ALLOWANCE

@dataclass(frozen=True)
class BootstrapBundle:
    length:int
    sha256:str
    manifest_sha256:str
    os_name:str
    architecture:str
    python:str
    manager:str
    expanded_length:int


def inspect_bundle(path):
    path=Path(path);require(path.is_file() and not path.is_symlink(),'bootstrap-bundle-unavailable')
    info=path.stat();require(0<info.st_size<=2*1024**3,'bootstrap-bundle-limit')
    digest=hashlib.sha256()
    with path.open('rb') as stream:
        while raw:=stream.read(1024*1024):digest.update(raw)
    with zipfile.ZipFile(path) as z:
        entries=z.infolist();require(0<len(entries)<=100001,'bootstrap-entry-limit');names=[]
        for i in entries:
            require(not i.is_dir() and not i.flag_bits&1 and not i.extra and i.orig_filename==i.filename and
                    i.compress_type in (zipfile.ZIP_STORED,zipfile.ZIP_DEFLATED) and
                    stat.S_IFMT(i.external_attr>>16) in (0,stat.S_IFREG) and not (i.external_attr>>16)&0o7000,
                    'bootstrap-entry-unsupported');names.append(_portable(i.filename))
        require(len(names)==len(set(names)) and 'manifest.json' in names,'bootstrap-inventory-mismatch');path_namespace(names)
        require(z.getinfo('manifest.json').file_size<=4*1024**2,'bootstrap-manifest-limit')
        raw=z.read('manifest.json');m=decode_canonical(raw);require(type(m) is dict,'bootstrap-manifest-invalid')
        entries=canonical_entries(m['inventory']);index={v['path']:v for v in entries}
        require(all(v['kind']=='regular' for v in entries) and set(names)==set(index)|{'manifest.json'},'bootstrap-inventory-mismatch')
        payload_length = sum(v['size'] for v in entries)
        require(payload_length<=4*1024**3,'bootstrap-expanded-limit')
        expanded_length = len(raw) + payload_length
        for v in entries:
            require(z.getinfo(v['path']).file_size==v['size'],'bootstrap-content-mismatch');h=hashlib.sha256();count=0
            with z.open(v['path']) as member:
                while chunk:=member.read(1024*1024):count+=len(chunk);require(count<=v['size'],'bootstrap-expanded-limit');h.update(chunk)
            require(count==v['size'] and h.hexdigest()==v['sha256'],'bootstrap-content-mismatch')
        require((m['os'],m['architecture']) in (('macos','arm64'),('windows','arm64'),('windows','x64')),'bootstrap-platform-unavailable')
        require(m['python'] in index and index[m['python']]['mode']=='100755' and m['manager'] in index,'bootstrap-entry-unavailable')
        result=BootstrapBundle(info.st_size,digest.hexdigest(),hashlib.sha256(raw).hexdigest(),m['os'],m['architecture'],m['python'],m['manager'],expanded_length)
    after=path.stat();require((info.st_dev,info.st_ino,info.st_size,info.st_mtime_ns,info.st_ctime_ns)==
                             (after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns,after.st_ctime_ns),'bootstrap-bundle-changed')
    return result


_WINDOWS_PREFLIGHT = r"""# Use memory-only interop so Windows PowerShell does not need compiler files.
function New-ColviaPreflightNative {
    $name = [Reflection.AssemblyName]::new('ColviaPreflight' + [Guid]::NewGuid().ToString('N'))
    $access = [Reflection.Emit.AssemblyBuilderAccess]::Run
    if ($PSVersionTable.PSEdition -eq 'Core') {
        $assembly = [Reflection.Emit.AssemblyBuilder]::DefineDynamicAssembly($name, $access)
    } else {
        $assembly = [AppDomain]::CurrentDomain.DefineDynamicAssembly($name, $access)
    }
    $module = $assembly.DefineDynamicModule($name.Name)
    $type = $module.DefineType('ColviaPreflightNative', [Reflection.TypeAttributes]::Public)
    $flags = [Reflection.MethodAttributes]'Public, Static, PinvokeImpl'
    $convention = [Reflection.CallingConventions]::Standard
    $winapi = [Runtime.InteropServices.CallingConvention]::Winapi
    $unicode = [Runtime.InteropServices.CharSet]::Unicode
    $preserve = [Reflection.MethodImplAttributes]::PreserveSig
    $machine = [uint16].MakeByRefType()
    $length = [uint32].MakeByRefType()
    $bytes = [uint64].MakeByRefType()
    $method = $type.DefinePInvokeMethod('GetCurrentProcess', 'kernel32.dll', $flags,
        $convention, [IntPtr], [Type[]]@(), $winapi, $unicode)
    $method.SetImplementationFlags($method.GetMethodImplementationFlags() -bor $preserve)
    $method = $type.DefinePInvokeMethod('IsWow64Process2', 'kernel32.dll', $flags,
        $convention, [bool], [Type[]]@([IntPtr], $machine, $machine), $winapi, $unicode)
    $method.SetImplementationFlags($method.GetMethodImplementationFlags() -bor $preserve)
    $method = $type.DefinePInvokeMethod('GetCurrentPackageFullName', 'kernel32.dll', $flags,
        $convention, [int], [Type[]]@($length, [IntPtr]), $winapi, $unicode)
    $method.SetImplementationFlags($method.GetMethodImplementationFlags() -bor $preserve)
    $method = $type.DefinePInvokeMethod('GetDiskFreeSpaceExW', 'kernel32.dll', $flags,
        $convention, [bool], [Type[]]@([string], $bytes, $bytes, $bytes), $winapi, $unicode)
    $method.SetImplementationFlags($method.GetMethodImplementationFlags() -bor $preserve)
    $method = $type.DefinePInvokeMethod('GetVolumePathNameW', 'kernel32.dll', $flags,
        $convention, [bool], [Type[]]@([string], [Text.StringBuilder], [uint32]), $winapi, $unicode)
    $method.SetImplementationFlags($method.GetMethodImplementationFlags() -bor $preserve)
    $method = $type.DefinePInvokeMethod('GetFileInformationByHandle', 'kernel32.dll', $flags,
        $convention, [bool], [Type[]]@([IntPtr], [IntPtr]), $winapi, $unicode)
    $method.SetImplementationFlags($method.GetMethodImplementationFlags() -bor $preserve)
    return $type.CreateType()
}

function Assert-ColviaNativeArchitecture([Type]$Native, [uint16]$Expected) {
    $processMachine = [uint16]0
    $nativeMachine = [uint16]0
    try { $ok = $Native::IsWow64Process2($Native::GetCurrentProcess(), [ref]$processMachine, [ref]$nativeMachine) }
    catch { throw 'bootstrap-architecture-unavailable. Could not identify the native Windows architecture.' }
    if (-not $ok -or $nativeMachine -notin @(0x8664, 0xAA64)) {
        throw 'bootstrap-architecture-unavailable. Could not identify the native Windows architecture.'
    }
    if ($nativeMachine -ne $Expected) { throw 'This installer does not match the native Windows architecture.' }
}

function Get-ColviaInstallParent([Type]$Native) {
    $guidance = 'Open Windows PowerShell from Start and run the same Colvia installation command there.'
    $length = [uint32]0
    try { $packageStatus = $Native::GetCurrentPackageFullName([ref]$length, [IntPtr]::Zero) }
    catch { throw "bootstrap-package-query-unavailable. $guidance" }
    if ($packageStatus -eq 122 -and $length -gt 0) { throw "bootstrap-app-context. $guidance" }
    if ($packageStatus -ne 15700) { throw "bootstrap-package-query-unavailable ($packageStatus). $guidance" }

    $parent = [Environment]::GetFolderPath('LocalApplicationData')
    if ($parent -notmatch '^[A-Za-z]:\\' -or -not [IO.Directory]::Exists($parent)) {
        throw "bootstrap-local-appdata-unavailable. $guidance"
    }
    $parent = [IO.Path]::GetFullPath($parent)
    $cachePath = '\\Packages\\[^\\]+\\LocalCache(?:\\|$)'
    if ($parent -match $cachePath -or $env:LOCALAPPDATA -match $cachePath) {
        throw "bootstrap-app-context. $guidance"
    }
    $drive = [IO.DriveInfo]::new([IO.Path]::GetPathRoot($parent))
    if ($drive.DriveType -ne [IO.DriveType]::Fixed) { throw "bootstrap-local-appdata-unavailable. $guidance" }
    for ($dir = [IO.DirectoryInfo]::new($parent); $null -ne $dir; $dir = $dir.Parent) {
        if ($dir.Attributes -band [IO.FileAttributes]::ReparsePoint) {
            throw "bootstrap-local-appdata-unavailable. $guidance"
        }
    }
    return $parent
}

function Assert-ColviaFreeSpace([Type]$Native, [string]$Directory, [uint64]$Required, [string]$Phase) {
    $available = [uint64]0
    $total = [uint64]0
    $free = [uint64]0
    $volume = [Text.StringBuilder]::new(32768)
    if (-not $Native::GetVolumePathNameW($Directory, $volume, [uint32]$volume.Capacity) -or
        -not $Native::GetDiskFreeSpaceExW($Directory, [ref]$available, [ref]$total, [ref]$free)) {
        throw "bootstrap-space-query-unavailable ($Phase). Check access to the installation volume."
    }
    if ($available -lt $Required) {
        throw "bootstrap-space-insufficient ($Phase) on $volume. Available $available bytes, required $Required bytes. Free space on this volume."
    }
}

function Stop-ColviaDiskWrite($Failure, [string]$Phase, [string]$Stage) {
    for ($cause = $Failure.Exception; $null -ne $cause; $cause = $cause.InnerException) {
        if ($cause -is [IO.IOException] -and $cause.HResult -in @(-2147024784, -2147024857)) {
            throw "bootstrap-disk-full ($Phase). Free space on the installation volume. Recovery files: $Stage"
        }
    }
    throw $Failure
}
"""


def render_windows_preflight(bundle):
    """The read-only checks shared by Windows bootstrap and native qualification."""
    machine = {'arm64': '0xAA64', 'x64': '0x8664'}[bundle.architecture]
    required = bundle.length + bundle.expanded_length + STAGING_ALLOWANCE
    return _windows_parent_check(machine) + f"Assert-ColviaFreeSpace $native $parent {required} 'download-and-expand'\n"


def _windows_parent_check(machine):
    return _WINDOWS_PREFLIGHT + f"""$ErrorActionPreference = 'Stop'
try {{ $native = New-ColviaPreflightNative }} catch {{ throw 'bootstrap-native-preflight-unavailable. Open Windows PowerShell from Start and run the same Colvia installation command there.' }}
Assert-ColviaNativeArchitecture $native {machine}
$parent = Get-ColviaInstallParent $native
"""


_MAC_EXISTING = r"""# Ordinary updates use the manager already trusted by this installation.
colvia_recovery='Existing Colvia installation cannot be verified. Keep its files and use the explicit Colvia installation recovery procedure.'
colvia_refuse_existing() { printf '%s\n' "$colvia_recovery" >&2; exit 2; }
colvia_private_directory() {
    [ -d "$1" ] && [ ! -L "$1" ] &&
        [ "$(/usr/bin/stat -f '%u' "$1")" = "$colvia_uid" ] &&
        case "$(/usr/bin/stat -f '%OLp' "$1")" in *00) true;; *) false;; esac
}
colvia_private_file() {
    [ -f "$1" ] && [ ! -L "$1" ] &&
        [ "$(/usr/bin/stat -f '%u:%l' "$1")" = "$colvia_uid:1" ] &&
        case "$(/usr/bin/stat -f '%OLp' "$1")" in
            *[0145][0145]) true;; *) false;;
        esac
}
if [ "$command" = bootstrap-install-or-update ]; then
    root="$parent/Colvia"
    # Search/read permission and a resolved parent are required even to decide
    # absence. A dangling link, unreadable location or partial home is not new.
    [ -r "$parent" ] && [ -x "$parent" ] &&
        [ "$(CDPATH= cd -P -- "$parent" && pwd -P)" = "$parent" ] || colvia_refuse_existing
    if [ -e "$root" ] || [ -L "$root" ]; then
        colvia_uid=$(/usr/bin/id -u)
        launcher="$root/bin/colvia-manage"
        identity="$root/entry.json"
        colvia_private_directory "$root" && colvia_private_directory "$root/bin" &&
            colvia_private_file "$launcher" && [ -x "$launcher" ] &&
            colvia_private_file "$identity" || colvia_refuse_existing
        [ "$(/usr/bin/stat -f '%z' "$identity")" -le 16384 ] &&
        [ "$(/usr/bin/stat -f '%z' "$launcher")" -le 67108864 ] || colvia_refuse_existing
        [ "$(/usr/bin/plutil -extract version raw -expect integer "$identity" 2>/dev/null)" = 1 ] &&
            [ "$(/usr/bin/plutil -extract os raw -expect string "$identity" 2>/dev/null)" = macos ] &&
            [ "$(/usr/bin/plutil -extract architecture raw -expect string "$identity" 2>/dev/null)" = arm64 ] || colvia_refuse_existing
        expected=$(/usr/bin/plutil -extract sha256 raw -expect string "$identity" 2>/dev/null) || colvia_refuse_existing
        case "$expected" in *[!0-9a-f]*) colvia_refuse_existing;; esac
        [ "${#expected}" -eq 64 ] || colvia_refuse_existing
        actual=$(/usr/bin/shasum -a 256 "$launcher") || colvia_refuse_existing
        [ "${actual%% *}" = "$expected" ] || colvia_refuse_existing
        # The native verifier and manager own runtime verification. Preserve
        # their output and status and do not fall through to first install.
        if "$launcher" update; then exit 0; else
            status=$?
            printf '%s\n' 'Colvia update stopped. Review the message above and use explicit recovery if requested.' >&2
            exit "$status"
        fi
    fi
fi
"""


_WINDOWS_EXISTING = r"""# The bootstrap may discover an installed entry, but must never repair it.
function Get-ColviaExistingHome([string]$Root) {
    # Confirm absence by enumerating the already checked parent. Access or
    # enumeration failures must not be converted into permission to install.
    $entries = @([IO.Directory]::EnumerateFileSystemEntries([IO.Path]::GetDirectoryName($Root), 'Colvia'))
    if ($entries.Count -eq 0) { return $null }
    if ($entries.Count -ne 1) { throw 'Ambiguous Colvia installation path.' }
    Get-Item -LiteralPath $entries[0] -Force -ErrorAction Stop
}
function Assert-ColviaPrivateEntry($Item, [bool]$Directory) {
    if ($Item.PSIsContainer -ne $Directory -or
        ($Item.Attributes -band [IO.FileAttributes]::ReparsePoint)) { throw 'Invalid installed path.' }
    # Use the .NET ACL API through Get-Acl, rather than matching localized user names.
    $acl = Get-Acl -LiteralPath $Item.FullName
    $sid = [Security.Principal.WindowsIdentity]::GetCurrent().User.Value
    if ($acl.GetOwner([Security.Principal.SecurityIdentifier]).Value -ne $sid -or
        ($Directory -and -not $acl.AreAccessRulesProtected)) { throw 'Installed path is not private.' }
    $rules = $acl.GetAccessRules($true, $true, [Security.Principal.SecurityIdentifier])
    if ($rules.Count -eq 0 -or $rules.Count -gt 32) { throw 'Installed permissions are unavailable.' }
    $allowed = 0
    foreach ($rule in $rules) {
        if ($rule.IdentityReference.Value -ne $sid -or
            $rule.AccessControlType -ne [Security.AccessControl.AccessControlType]::Allow -or
            ($rule.PropagationFlags -band [Security.AccessControl.PropagationFlags]::InheritOnly)) {
            throw 'Installed path is not private.'
        }
        $allowed = $allowed -bor [int]$rule.FileSystemRights
    }
    if (($allowed -band 0x1f01ff) -ne 0x1f01ff) { throw 'Installed owner access is incomplete.' }
}
function Get-ColviaInstalledCommand($HomeItem, [Type]$Native, [string]$Architecture) {
    Assert-ColviaPrivateEntry $HomeItem $true
    $root = $HomeItem.FullName
    $bin = Get-Item -LiteralPath (Join-Path $root 'bin') -Force
    Assert-ColviaPrivateEntry $bin $true
    $entry = Get-Item -LiteralPath (Join-Path $root 'entry.json') -Force
    $launcher = Get-Item -LiteralPath (Join-Path $bin.FullName 'colvia-manage.exe') -Force
    Assert-ColviaPrivateEntry $entry $false
    Assert-ColviaPrivateEntry $launcher $false
    if ($entry.Length -gt 16384) { throw 'Installed entry record is too large.' }

    # Hold exact, single-link bytes while checking the installed verifier and
    # using its read-only inspection. Release them before the updater runs so
    # Windows can replace its native launcher during an authorized update.
    $recordFile = $null
    $launcherFile = $null
    try {
        $recordFile = Open-ColviaInstalledFile $Native $entry.FullName
        $launcherFile = Open-ColviaInstalledFile $Native $launcher.FullName
        if ($recordFile.Length -gt 16384 -or $launcherFile.Length -gt 64MB) {
            throw 'Installed entry exceeds its size limit.'
        }
        $reader = [IO.StreamReader]::new($recordFile, [Text.UTF8Encoding]::new($false, $true))
        try { $identity = ConvertFrom-Json -InputObject $reader.ReadToEnd() } finally { $reader.Dispose() }
        if (($identity.version -isnot [int] -and $identity.version -isnot [long]) -or
            $identity.version -ne 1 -or $identity.os -cne 'windows' -or
            $identity.architecture -cne $Architecture -or $identity.sha256 -cnotmatch '^[0-9a-f]{64}$') {
            throw 'Invalid installed entry record.'
        }
        $hasher = [Security.Cryptography.SHA256]::Create()
        try { $digest = [BitConverter]::ToString($hasher.ComputeHash($launcherFile)).Replace('-', '').ToLowerInvariant() }
        finally { $hasher.Dispose() }
        if ($digest -cne $identity.sha256) { throw 'Installed launcher hash changed.' }

        $info = [Diagnostics.ProcessStartInfo]::new($launcher.FullName, '--inspect-only')
        $info.UseShellExecute = $false
        $info.RedirectStandardOutput = $true
        $info.StandardOutputEncoding = [Text.UTF8Encoding]::new($false, $true)
        $process = [Diagnostics.Process]::Start($info)
        try {
            $pending = $process.StandardOutput.ReadToEndAsync()
            if (-not $process.WaitForExit(120000)) { $process.Kill(); throw 'Installed runtime verification timed out.' }
            if ($process.ExitCode -ne 0 -or -not $pending.Wait(5000)) { throw 'Installed runtime verification failed.' }
            $inspection = ConvertFrom-Json -InputObject $pending.Result
        } finally { $process.Dispose() }
    } finally {
        if ($null -ne $launcherFile) { $launcherFile.Dispose() }
        if ($null -ne $recordFile) { $recordFile.Dispose() }
    }
    $command = $inspection.command
    if ($inspection.source_inspection_only -isnot [bool] -or -not $inspection.source_inspection_only -or
        $command -isnot [Array] -or $command.Count -ne 10 -or
        $command[1] -cne '-I' -or $command[2] -cne '-B' -or $command[4] -cne '--management-root' -or
        $command[5] -ne $root -or $command[6] -cne '--runtime-slot' -or
        $command[7] -cnotmatch '^[A-Za-z0-9][A-Za-z0-9._-]{0,159}$' -or
        $command[8] -cne '--runtime-manifest-sha256' -or $command[9] -cnotmatch '^[0-9a-f]{64}$') {
        throw 'Invalid installed runtime selection.'
    }
    $slot = Join-Path $root ('runtime\slots\' + $command[7])
    foreach ($path in @($command[0], $command[3])) {
        if (-not ($path -is [string]) -or
            -not $path.StartsWith($slot + '\', [StringComparison]::OrdinalIgnoreCase) -or
            $path -ne [IO.Path]::GetFullPath($path)) { throw 'Invalid installed runtime path.' }
    }
    return $command
}
function Open-ColviaInstalledFile([Type]$Native, [string]$Path) {
    $stream = [IO.File]::Open($Path, [IO.FileMode]::Open, [IO.FileAccess]::Read, [IO.FileShare]::Read)
    try {
        # BY_HANDLE_FILE_INFORMATION is 13 DWORDs; number of links is DWORD 10.
        $buffer = [Runtime.InteropServices.Marshal]::AllocHGlobal(52)
        try {
            if (-not $Native::GetFileInformationByHandle($stream.SafeFileHandle.DangerousGetHandle(), $buffer) -or
                ([Runtime.InteropServices.Marshal]::ReadInt32($buffer, 0) -band 0x410) -or
                [Runtime.InteropServices.Marshal]::ReadInt32($buffer, 40) -ne 1) {
                throw 'Installed entry must be a regular single-link file.'
            }
        } finally { [Runtime.InteropServices.Marshal]::FreeHGlobal($buffer) }
        return $stream
    } catch { $stream.Dispose(); throw }
}
"""


def render(bundle,url):
    require(type(bundle) is BootstrapBundle,'verified-bootstrap-bundle-required')
    parsed=urlsplit(url)
    require(parsed.scheme=='https' and parsed.hostname and parsed.netloc==parsed.hostname and not parsed.query and not parsed.fragment and
            re.fullmatch(r'/[A-Za-z0-9._/%-]+',parsed.path),'bootstrap-https-asset-required')
    for entry in (bundle.python,bundle.manager):
        require(_portable(entry)==entry and re.fullmatch(r'[A-Za-z0-9._/-]+',entry),'bootstrap-entry-spelling')
    if bundle.os_name=='macos':
        return f'''#!/bin/sh
set -eu
umask 077
command=bootstrap-install-or-update
if [ "$#" -eq 1 ] && [ "$1" = --install-status ]; then
    command=bootstrap-install-status; set --
elif [ "$#" -ne 0 ]; then
    action=$1
    [ "$#" -ge 2 ] || {{ echo 'An explicit recovery operation is required.' >&2; exit 2; }}
    operation=$2
    case "$operation" in ''|*[!A-Za-z0-9._-]*|[!A-Za-z0-9]*) echo 'Invalid installation operation.' >&2; exit 2;; esac
    [ "${{#operation}}" -le 160 ] || exit 2
    case "$action" in
      --resume-install|--repair-runtime|--resume-repair|--retry-install)
        [ "$#" -eq 2 ] || {{ [ "$action" = --resume-install ] && [ "$#" -eq 3 ]; }} || exit 2
        case "$action" in --resume-install) command=bootstrap-resume-install;; --resume-repair) command=bootstrap-resume-repair;; --retry-install) command=bootstrap-retry-install;; *) command=bootstrap-repair-runtime;; esac
        if [ "$#" -eq 3 ]; then set -- --operation "$operation" --renewal "$3"; else set -- --operation "$operation"; fi;;
      --quarantine-preview)
        [ "$#" -eq 2 ] || exit 2
        command=bootstrap-quarantine-preview; set -- --operation "$operation";;
      --replace-install)
        [ "$#" -eq 3 ] || exit 2
        command=bootstrap-replace-install; set -- --operation "$operation" --receipt "$3";;
      --refresh-install)
        [ "$#" -eq 4 ] || exit 2
        command=bootstrap-refresh-install; set -- --operation "$operation" --receipt "$3" --renewal "$4";;
      --rollback-preview)
        [ "$#" -eq 3 ] || exit 2
        command=bootstrap-rollback-preview; set -- --operation "$operation" --receipt "$3";;
      --rollback-update)
        [ "$#" -eq 4 ] || exit 2
        command=bootstrap-rollback; set -- --operation "$operation" --receipt "$3" --rollback-receipt "$4";;
      *) echo 'Unknown recovery action.' >&2; exit 2;;
    esac
fi
[ "$(/usr/bin/uname -s)" = Darwin ] && [ "$(/usr/bin/uname -m)" = arm64 ] || {{ echo 'This installer requires macOS Apple Silicon.' >&2; exit 2; }}
[ -n "${{HOME:-}}" ] && [ "${{HOME#/}}" != "$HOME" ] || {{ echo 'A local user home is required.' >&2; exit 2; }}
parent="$HOME/Library/Application Support"
[ -d "$parent" ] && [ ! -L "$parent" ] || {{ echo 'The user application-data folder is unavailable.' >&2; exit 2; }}
{_MAC_EXISTING}stage="$parent/Colvia-bootstrap-{bundle.sha256[:16]}-$$"
/bin/mkdir -m 700 "$stage"
echo "Preparing Colvia. Recovery files: $stage"
/usr/bin/curl --proto '=https' --tlsv1.2 --fail --silent --show-error --max-time 120 --max-redirs 0 --output "$stage/bundle.zip" '{url}'
[ "$(/usr/bin/wc -c < "$stage/bundle.zip" | /usr/bin/tr -d ' ')" = '{bundle.length}' ] || {{ echo 'Download length mismatch; nothing installed.' >&2; exit 3; }}
actual=$(/usr/bin/shasum -a 256 "$stage/bundle.zip")
[ "${{actual%% *}}" = '{bundle.sha256}' ] || {{ echo 'Download verification failed; nothing installed.' >&2; exit 3; }}
# The build-time verifier admitted only this exact normalized regular-file ZIP.
/bin/mkdir -m 700 "$stage/runtime"
/usr/bin/ditto -x -k "$stage/bundle.zip" "$stage/runtime"
/bin/chmod 700 "$stage/runtime/{bundle.python}"
exec "$stage/runtime/{bundle.python}" -I -B "$stage/runtime/{bundle.manager}" "$command" --management-root "$parent/Colvia" --bootstrap-stage "$stage/runtime" --bootstrap-manifest-sha256 '{bundle.manifest_sha256}' "$@"
'''
    require(bundle.os_name=='windows','bootstrap-platform-unavailable')
    machine = {'arm64': '0xAA64', 'x64': '0x8664'}[bundle.architecture]
    return f'''#requires -Version 5.1
param([string]$ResumeInstall = '', [string]$RepairRuntime = '', [string]$ResumeRepair = '', [string]$RetryInstall = '', [string]$RefreshInstall = '', [string]$RollbackPreview = '', [string]$RollbackUpdate = '', [string]$Receipt = '', [string]$Renewal = '', [string]$RollbackReceipt = '', [string]$QuarantinePreview = '', [string]$ReplaceInstall = '', [switch]$InstallStatus)
$managerArgs = @('bootstrap-install-or-update')
if ($InstallStatus) {{
    if (@(@($ResumeInstall, $RepairRuntime, $ResumeRepair, $RetryInstall, $RefreshInstall, $RollbackPreview, $RollbackUpdate, $QuarantinePreview, $ReplaceInstall) | Where-Object {{ $_ -ne '' }}).Count -gt 0) {{ throw 'Choose one recovery action.' }}
    $managerArgs = @('bootstrap-install-status')
}}
if (@(@($ResumeInstall, $RepairRuntime, $ResumeRepair, $RetryInstall, $RefreshInstall, $RollbackPreview, $RollbackUpdate, $QuarantinePreview, $ReplaceInstall) | Where-Object {{ $_ -ne '' }}).Count -gt 1) {{ throw 'Choose one explicit recovery action.' }}
if ($RepairRuntime -ne '') {{
    if ($RepairRuntime -cnotmatch '^[A-Za-z0-9][A-Za-z0-9._-]{{0,159}}$') {{ throw 'Invalid installation operation.' }}
    $managerArgs = @('bootstrap-repair-runtime', '--operation', $RepairRuntime)
}}
if ($ResumeInstall -ne '') {{
    if ($ResumeInstall -cnotmatch '^[A-Za-z0-9][A-Za-z0-9._-]{{0,159}}$') {{ throw 'Invalid installation operation.' }}
    $managerArgs = @('bootstrap-resume-install', '--operation', $ResumeInstall)
}}
if ($ResumeRepair -ne '') {{
    if ($ResumeRepair -cnotmatch '^[A-Za-z0-9][A-Za-z0-9._-]{{0,159}}$') {{ throw 'Invalid installation operation.' }}
    $managerArgs = @('bootstrap-resume-repair', '--operation', $ResumeRepair)
}}
foreach ($operation in @($RetryInstall, $RefreshInstall, $RollbackPreview, $RollbackUpdate, $QuarantinePreview, $ReplaceInstall)) {{
    if ($operation -ne '' -and $operation -cnotmatch '^[A-Za-z0-9][A-Za-z0-9._-]{{0,159}}$') {{ throw 'Invalid recovery operation.' }}
}}
if ($QuarantinePreview -ne '') {{ $managerArgs = @('bootstrap-quarantine-preview', '--operation', $QuarantinePreview) }}
if ($ReplaceInstall -ne '') {{
    if ($Receipt -eq '') {{ throw 'The quarantine preview receipt is required.' }}
    $managerArgs = @('bootstrap-replace-install', '--operation', $ReplaceInstall, '--receipt', $Receipt)
}}
if ($RetryInstall -ne '') {{ $managerArgs = @('bootstrap-retry-install', '--operation', $RetryInstall) }}
if ($ResumeInstall -ne '' -and $Renewal -ne '') {{ $managerArgs += @('--renewal', $Renewal) }}
if ($RefreshInstall -ne '') {{
    if ($Receipt -eq '' -or $Renewal -eq '') {{ throw 'The original receipt and renewal name are required.' }}
    $managerArgs = @('bootstrap-refresh-install', '--operation', $RefreshInstall, '--receipt', $Receipt, '--renewal', $Renewal)
}}
if ($RollbackPreview -ne '') {{
    if ($Receipt -eq '') {{ throw 'The original release receipt is required.' }}
    $managerArgs = @('bootstrap-rollback-preview', '--operation', $RollbackPreview, '--receipt', $Receipt)
}}
if ($RollbackUpdate -ne '') {{
    if ($Receipt -eq '' -or $RollbackReceipt -eq '') {{ throw 'The release and rollback receipts are required.' }}
    $managerArgs = @('bootstrap-rollback', '--operation', $RollbackUpdate, '--receipt', $Receipt, '--rollback-receipt', $RollbackReceipt)
}}
{_WINDOWS_EXISTING}{_windows_parent_check(machine)}if ($managerArgs[0] -ceq 'bootstrap-install-or-update') {{
    try {{
        $homeItem = Get-ColviaExistingHome (Join-Path $parent 'Colvia')
        if ($null -ne $homeItem) {{ $installed = @(Get-ColviaInstalledCommand $homeItem $native '{bundle.architecture}') }}
    }} catch {{
        throw ('Existing Colvia installation cannot be verified. Keep its files and use the explicit Colvia installation recovery procedure. ' + $_.Exception.Message)
    }}
    if ($null -ne $homeItem) {{
        $installedPython = $installed[0]
        $installedArgs = @($installed[1..9]) + @('update')
        & $installedPython @installedArgs
        $status = $LASTEXITCODE
        if ($status -ne 0) {{
            [Console]::Error.WriteLine('Colvia update stopped. Review the message above and use explicit recovery if requested.')
        }}
        exit $status
    }}
}}
Assert-ColviaFreeSpace $native $parent {bundle.length + bundle.expanded_length + STAGING_ALLOWANCE} 'download-and-expand'
$stage = Join-Path $parent ('Colvia-bootstrap-{bundle.sha256[:16]}-' + [Guid]::NewGuid().ToString('N'))
if (Test-Path -LiteralPath $stage) {{ throw 'Preparation folder already exists.' }}
try {{ $directory = New-Item -ItemType Directory -Path $stage }} catch {{ Stop-ColviaDiskWrite $_ 'prepare' $stage }}
$sid = [Security.Principal.WindowsIdentity]::GetCurrent().User
$acl = New-Object Security.AccessControl.DirectorySecurity
$acl.SetOwner($sid)
$acl.SetAccessRuleProtection($true, $false)
$rule = New-Object Security.AccessControl.FileSystemAccessRule($sid, 'FullControl', 'ContainerInherit,ObjectInherit', 'None', 'Allow')
$acl.AddAccessRule($rule)
Set-Acl -LiteralPath $stage -AclObject $acl
Write-Output ('Preparing Colvia. Recovery files: ' + $stage)
$bundlePath = Join-Path $stage 'bundle.zip'
$oldTls = [Net.ServicePointManager]::SecurityProtocol
try {{
    [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
    Invoke-WebRequest -Uri '{url}' -UseBasicParsing -MaximumRedirection 0 -TimeoutSec 120 -OutFile $bundlePath
}} catch {{ Stop-ColviaDiskWrite $_ 'download' $stage }} finally {{ [Net.ServicePointManager]::SecurityProtocol = $oldTls }}
if ((Get-Item -LiteralPath $bundlePath).Length -ne {bundle.length}) {{ throw 'Download length mismatch; nothing installed.' }}
if ((Get-FileHash -LiteralPath $bundlePath -Algorithm SHA256).Hash.ToLowerInvariant() -ne '{bundle.sha256}') {{ throw 'Download verification failed; nothing installed.' }}
Assert-ColviaFreeSpace $native $stage {bundle.expanded_length + STAGING_ALLOWANCE} 'expand'
$runtime = Join-Path $stage 'runtime'
try {{
    New-Item -ItemType Directory -Path $runtime | Out-Null
    Set-Acl -LiteralPath $runtime -AclObject $acl
    # Only the exact build-verified regular-file ZIP is expanded.
    Expand-Archive -LiteralPath $bundlePath -DestinationPath $runtime
}} catch {{ Stop-ColviaDiskWrite $_ 'expand' $stage }}
$python = Join-Path $runtime '{bundle.python}'
$manager = Join-Path $runtime '{bundle.manager}'
& $python -I -B $manager @managerArgs --management-root (Join-Path $parent 'Colvia') --bootstrap-stage $runtime --bootstrap-manifest-sha256 '{bundle.manifest_sha256}'
if ($LASTEXITCODE -ne 0) {{ throw ('Colvia preparation stopped; preserve ' + $stage) }}
'''
