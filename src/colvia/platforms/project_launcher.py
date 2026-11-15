"""Small project entry points selecting the installed native manager, not Python."""
from pathlib import Path
import shlex,ntpath,os,sys
from ..codec import require
from ..storage.windows import local_path


def project_launcher(entry,home,os_name,*,known_local_appdata=None,environment_local_appdata=None,
                     known_user_profile=None,environment_user_profile=None):
    if os_name=='macos':
        raw=('#!/bin/sh\nset -eu\nproject_root=$(CDPATH= cd -P -- "$(dirname -- "$0")" && pwd)\nexec '+shlex.quote(str(entry))+
             ' --management-root '+shlex.quote(str(home))+' --root "$project_root" "$@"\n').encode()
        return 'colvia','100755',raw
    require(os_name=='windows','connect-platform-port-unavailable')
    executable=local_path(entry);management=local_path(home)
    native_paths=known_local_appdata is None and sys.platform=='win32'
    if native_paths:
        from .windows_paths import local_appdata
        known_local_appdata=local_appdata()
        environment_local_appdata=os.environ.get('LOCALAPPDATA')
    standard=(known_local_appdata is not None and
              ntpath.normcase(management)==ntpath.normcase(ntpath.join(local_path(known_local_appdata),'Colvia')))
    guard=''
    if standard:
        if native_paths:
            from .windows_paths import user_profile
            known_user_profile=user_profile()
            environment_user_profile=os.environ.get('USERPROFILE')
        require(ntpath.normcase(executable)==ntpath.normcase(ntpath.join(management,'bin','colvia.exe')),
                'windows-standard-entry-mismatch')
        profile_home=(known_user_profile is not None and
                      ntpath.normcase(local_path(known_local_appdata))==
                      ntpath.normcase(ntpath.join(local_path(known_user_profile),'AppData','Local')))
        if profile_home:
            require(environment_user_profile is not None and
                    ntpath.normcase(local_path(environment_user_profile))==ntpath.normcase(local_path(known_user_profile)),
                    'windows-user-profile-environment-mismatch')
            # Keep batch bytes ASCII for Unicode account names. The native
            # launcher verifies this explicit management home before use.
            runtime_home=r'%USERPROFILE%\AppData\Local\Colvia'
            guard=('if not defined USERPROFILE exit /b 1\r\n'
                   'if not "%USERPROFILE:~1,2%"==":\\" exit /b 1\r\n')
        else:
            require(environment_local_appdata is not None and
                    ntpath.normcase(local_path(environment_local_appdata))==ntpath.normcase(local_path(known_local_appdata)),
                    'windows-local-appdata-environment-mismatch')
            runtime_home=r'%LOCALAPPDATA%\Colvia'
            guard='if not defined LOCALAPPDATA exit /b 1\r\n'
        invocation=f'"{runtime_home}\\bin\\colvia.exe" --management-root "{runtime_home}"'
    else:
        # Custom development locations remain literal and need percent escaping.
        invocation='"'+executable.replace('%','%%')+'" --management-root "'+management.replace('%','%%')+'"'
    raw=('@echo off\r\nsetlocal DisableDelayedExpansion\r\n'
         'for %%I in ("%~dp0.") do set "COLVIA_PROJECT_ROOT=%%~fI"\r\n'
         +guard+invocation+' --root "%COLVIA_PROJECT_ROOT%" %*\r\n'
         'exit /b %errorlevel%\r\n').encode('utf-8')
    require(raw.isascii(),'windows-project-launcher-unicode-path-unavailable')
    return 'colvia.cmd','100644',raw


def project_block(block,os_name):
    return block.replace(b'./colvia ',b'.\\colvia.cmd ') if os_name=='windows' else block
