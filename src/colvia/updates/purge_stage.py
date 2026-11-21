"""Cleanup of the single just-created external preparation directory after success."""
import hashlib
import os
from pathlib import Path
import stat
import zipfile

from ..codec import require


def clean_macos(stage, bundle_sha, identity):
    stage = Path(stage)
    info = stage.lstat()
    require(f'{info.st_dev}:{info.st_ino}' == identity and info.st_uid == os.getuid()
            and stat.S_ISDIR(info.st_mode) and info.st_mode & 0o077 == 0, 'purge-stage-replaced')
    require({p.name for p in stage.iterdir()} == {'bundle.zip','runtime'}, 'purge-stage-changed')
    archive = stage/'bundle.zip'
    def regular(path):
        item = path.lstat()
        require(stat.S_ISREG(item.st_mode) and item.st_nlink == 1 and item.st_uid == os.getuid(),
                'purge-stage-changed')
        return item.st_dev, item.st_ino, item.st_mtime_ns, item.st_size
    items = {archive:regular(archive)}
    dirs = {}
    with archive.open('rb') as stream:
        require(hashlib.file_digest(stream,'sha256').hexdigest() == bundle_sha, 'purge-stage-bundle-changed')
        stream.seek(0)
        with zipfile.ZipFile(stream) as z:
            runtime = stage/'runtime'
            expected = set(z.namelist())
            for directory, children, names in os.walk(runtime, followlinks=False, onerror=lambda exc: (_ for _ in ()).throw(exc)):
                directory = Path(directory)
                require(all(not (directory/child).is_symlink() for child in children), 'purge-stage-changed')
                st = directory.lstat()
                require(stat.S_ISDIR(st.st_mode) and st.st_uid == os.getuid(), 'purge-stage-changed')
                dirs[directory] = (st.st_dev,st.st_ino)
                for name in names:
                    path = directory/name
                    rel = path.relative_to(runtime).as_posix()
                    require(rel in expected,'purge-stage-unknown-file')
                    items[path] = regular(path)
                    with z.open(rel) as original, path.open('rb') as actual:
                        require(hashlib.file_digest(original,'sha256').digest() ==
                                hashlib.file_digest(actual,'sha256').digest(),'purge-stage-changed')
                    expected.remove(rel)
            require(not expected and set(dirs) == {parent for path in items if path!=archive
                    for parent in path.parents if parent==runtime or runtime in parent.parents},
                    'purge-stage-changed')
    for path, snapshot in items.items():
        require(regular(path)==snapshot,'purge-stage-changed')
        path.unlink()
    for path in sorted(dirs,key=lambda p:-len(p.parts)):
        st=path.lstat()
        require((st.st_dev,st.st_ino)==dirs[path], 'purge-stage-replaced')
        path.rmdir()
    stage.rmdir()


# The stage's interpreter has exited by the time the Windows host reaches this
# code. Pin the exact archive while checking each extracted member. Delete only
# the enumerated members and empty directories. A mismatch retains the stage.
WINDOWS_CLEAN = r"""
if ($managerArgs[0] -like 'bootstrap-purge*') {
    $runtimePath = [IO.Path]::GetFullPath($runtime)
    $allowed = New-Object 'System.Collections.Generic.HashSet[string]' ([StringComparer]::Ordinal)
    $dirs = New-Object 'System.Collections.Generic.HashSet[string]' ([StringComparer]::OrdinalIgnoreCase)
    $files = New-Object 'System.Collections.Generic.List[string]'
    [void]$dirs.Add($runtimePath)
    $roots = @(Get-ChildItem -LiteralPath $stage -Force)
    if ($roots.Count -ne 2 -or 'runtime' -cnotin $roots.Name -or 'bundle.zip' -cnotin $roots.Name -or ($roots | Where-Object { $_.Attributes -band [IO.FileAttributes]::ReparsePoint })) { throw 'Preparation directory changed.' }
    Add-Type -AssemblyName System.IO.Compression
    $stream = Open-ColviaInstalledFile $native $bundlePath
    try {
        $sha = [Security.Cryptography.SHA256]::Create()
        if ([BitConverter]::ToString($sha.ComputeHash($stream)).Replace('-','').ToLowerInvariant() -cne 'BUNDLE_SHA') { throw 'Preparation ZIP changed.' }
        $stream.Position = 0
        $zip = [IO.Compression.ZipArchive]::new($stream,[IO.Compression.ZipArchiveMode]::Read,$true)
        try {
            foreach ($e in $zip.Entries) {
                $path = [IO.Path]::GetFullPath((Join-Path $runtimePath $e.FullName))
                if (!$path.StartsWith($runtimePath+'\',[StringComparison]::OrdinalIgnoreCase) -or !$allowed.Add($path)) { throw 'Preparation path changed.' }
                $dir = [IO.Path]::GetDirectoryName($path)
                while ($dir -ne $runtimePath) {
                    if ((Get-Item -LiteralPath $dir -Force).Attributes -band [IO.FileAttributes]::ReparsePoint) { throw 'Preparation directory changed.' }
                    [void]$dirs.Add($dir)
                    $dir = [IO.Path]::GetDirectoryName($dir)
                }
                $entry = $e.Open()
                $actual = Open-ColviaInstalledFile $native $path
                try {
                    if ([BitConverter]::ToString($sha.ComputeHash($entry)) -cne [BitConverter]::ToString($sha.ComputeHash($actual))) { throw 'Preparation file changed.' }
                } finally { $entry.Dispose(); $actual.Dispose() }
                $files.Add($path)
            }
            foreach ($dir in $dirs) {
                foreach ($item in (Get-ChildItem -LiteralPath $dir -Force)) {
                    if (!$dirs.Contains($item.FullName) -and !$allowed.Contains($item.FullName)) { throw 'Unknown preparation file.' }
                }
            }
        } finally { $zip.Dispose(); $sha.Dispose() }
    } finally { $stream.Dispose() }
    foreach ($path in $files) { [IO.File]::Delete($path) }
    foreach ($dir in ($dirs | Sort-Object Length -Descending)) { [IO.Directory]::Delete($dir) }
    [IO.File]::Delete($bundlePath)
    [IO.Directory]::Delete($stage)
}
"""
