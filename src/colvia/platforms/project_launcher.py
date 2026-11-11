"""Small project entry points selecting the installed native manager, not Python."""
from pathlib import Path
import shlex,ntpath,os,sys
from ..codec import require
from ..storage.windows import local_path


def project_launcher(entry,home,os_name,*,known_local_appdata=None,environment_local_appdata=None):
    if os_name=='macos':
        raw=('#!/bin/sh\nset -eu\nproject_root=$(CDPATH= cd -P -- "$(dirname -- "$0")" && pwd)\nexec '+shlex.quote(str(entry))+
             ' --management-root '+shlex.quote(str(home))+' --root "$project_root" "$@"\n').encode()
        return 'colvia','100755',raw
    require(os_name=='windows','connect-platform-port-unavailable')
    executable=local_path(entry);management=local_path(home)
    if known_local_appdata is None and sys.platform=='win32':
        from .windows_paths import local_appdata
        known_local_appdata=local_appdata()
        environment_local_appdata=os.environ.get('LOCALAPPDATA')
    standard=(known_local_appdata is not None and
              ntpath.normcase(management)==ntpath.normcase(ntpath.join(local_path(known_local_appdata),'Colvia')))
    if standard:
        require(environment_local_appdata is not None and
                ntpath.normcase(local_path(environment_local_appdata))==ntpath.normcase(local_path(known_local_appdata)),
                'windows-local-appdata-environment-mismatch')
        require(ntpath.normcase(executable)==ntpath.normcase(ntpath.join(management,'bin','colvia.exe')),
                'windows-standard-entry-mismatch')
        # The batch bytes stay ASCII even with a Unicode account name. The
        # native entry selects KnownFolder itself; no Python/PATH/code-page edit.
        invocation='"%LOCALAPPDATA%\\Colvia\\bin\\colvia.exe"'
    else:
        # Custom development locations remain literal and need percent escaping.
        invocation='"'+executable.replace('%','%%')+'" --management-root "'+management.replace('%','%%')+'"'
    raw=('@echo off\r\nsetlocal DisableDelayedExpansion\r\n'
         'for %%I in ("%~dp0.") do set "COLVIA_PROJECT_ROOT=%%~fI"\r\n'
         +invocation+' --root "%COLVIA_PROJECT_ROOT%" %*\r\n'
         'exit /b %errorlevel%\r\n').encode('utf-8')
    require(raw.isascii(),'windows-project-launcher-unicode-path-unavailable')
    return 'colvia.cmd','100644',raw


def project_block(block,os_name):
    return block.replace(b'./colvia ',b'.\\colvia.cmd ') if os_name=='windows' else block
