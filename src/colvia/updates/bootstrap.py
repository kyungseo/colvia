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

@dataclass(frozen=True)
class BootstrapBundle:
    length:int
    sha256:str
    manifest_sha256:str
    os_name:str
    architecture:str
    python:str
    manager:str


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
        require(sum(v['size'] for v in entries)<=4*1024**3,'bootstrap-expanded-limit')
        for v in entries:
            require(z.getinfo(v['path']).file_size==v['size'],'bootstrap-content-mismatch');h=hashlib.sha256();count=0
            with z.open(v['path']) as member:
                while chunk:=member.read(1024*1024):count+=len(chunk);require(count<=v['size'],'bootstrap-expanded-limit');h.update(chunk)
            require(count==v['size'] and h.hexdigest()==v['sha256'],'bootstrap-content-mismatch')
        require((m['os'],m['architecture']) in (('macos','arm64'),('windows','arm64'),('windows','x64')),'bootstrap-platform-unavailable')
        require(m['python'] in index and index[m['python']]['mode']=='100755' and m['manager'] in index,'bootstrap-entry-unavailable')
        result=BootstrapBundle(info.st_size,digest.hexdigest(),hashlib.sha256(raw).hexdigest(),m['os'],m['architecture'],m['python'],m['manager'])
    after=path.stat();require((info.st_dev,info.st_ino,info.st_size,info.st_mtime_ns,info.st_ctime_ns)==
                             (after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns,after.st_ctime_ns),'bootstrap-bundle-changed')
    return result


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
stage="$parent/Colvia-bootstrap-{bundle.sha256[:16]}-$$"
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
    arch='Arm64' if bundle.architecture=='arm64' else 'X64'
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
$ErrorActionPreference = 'Stop'
$expectedArchitecture = '{arch}'
if ([System.Runtime.InteropServices.RuntimeInformation]::OSArchitecture.ToString() -ne $expectedArchitecture) {{ throw 'This installer does not match the native Windows architecture.' }}
$parent = [Environment]::GetFolderPath('LocalApplicationData')
if (-not [IO.Path]::IsPathRooted($parent)) {{ throw 'The user application-data folder is unavailable.' }}
$stage = Join-Path $parent ('Colvia-bootstrap-{bundle.sha256[:16]}-' + [Guid]::NewGuid().ToString('N'))
if (Test-Path -LiteralPath $stage) {{ throw 'Preparation folder already exists.' }}
$directory = New-Item -ItemType Directory -Path $stage
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
}} finally {{ [Net.ServicePointManager]::SecurityProtocol = $oldTls }}
if ((Get-Item -LiteralPath $bundlePath).Length -ne {bundle.length}) {{ throw 'Download length mismatch; nothing installed.' }}
if ((Get-FileHash -LiteralPath $bundlePath -Algorithm SHA256).Hash.ToLowerInvariant() -ne '{bundle.sha256}') {{ throw 'Download verification failed; nothing installed.' }}
$runtime = Join-Path $stage 'runtime'
New-Item -ItemType Directory -Path $runtime | Out-Null
Set-Acl -LiteralPath $runtime -AclObject $acl
# Only the exact build-verified regular-file ZIP is expanded.
Expand-Archive -LiteralPath $bundlePath -DestinationPath $runtime
$python = Join-Path $runtime '{bundle.python}'
$manager = Join-Path $runtime '{bundle.manager}'
& $python -I -B $manager @managerArgs --management-root (Join-Path $parent 'Colvia') --bootstrap-stage $runtime --bootstrap-manifest-sha256 '{bundle.manifest_sha256}'
if ($LASTEXITCODE -ne 0) {{ throw ('Colvia preparation stopped; preserve ' + $stage) }}
'''
