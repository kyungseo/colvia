"""Fixed per-user macOS receiver composition, never a terminal notification."""
from pathlib import Path
import os,pwd
from ..codec import canonical_bytes,decode_canonical,require
from ..updates.notice_app import MacNoticeFiles,APP
from .process import run


def standard_root():return Path(pwd.getpwuid(os.getuid()).pw_dir)/'Library/Application Support/Colvia'

class DarwinNotices:
    receiver_identity=dict(id='macos-user',version=1)
    def __init__(self,home,*,runner=run,root_provider=standard_root):self.home=home;self.files=home.files;self.runner=runner;self.root_provider=root_provider
    def verified(self):
        require(self.home.root==self.root_provider(),'notice-standard-location-required')
        require(not self.files.exists(self.home.root/'notice-app.pending'),'notice-app-update-pending')
        _,state=self.home.slots.selection();package=MacNoticeFiles(self.home,state['selected'],'notice-check')
        candidate=package.candidate();require(candidate is not None,'notice-platform-not-prepared')
        rows,_=candidate;require(self.files.read(self.home.root/'receiver.json')==package.record(rows),'notice-app-description-changed');package.check_files(rows)
        return self.home.root/'bin'/APP/'Contents/MacOS/ColviaWork'
    def command(self,arguments,seconds):
        app=self.verified()
        return self.runner([str(app),*arguments],cwd=self.home.root,env={'PATH':'/usr/bin:/bin','LANG':'en_US.UTF-8'},seconds=seconds,output_limit=65536)
    def choice(self):
        path=self.home.root/'notice-choice.json'
        if not self.files.exists(path):return False
        value=decode_canonical(self.files.read(path));require(type(value) is dict and set(value)=={'version','enabled'} and value['version']==1 and type(value['enabled']) is bool,'notice-choice-invalid')
        return value['enabled']
    def inspect(self):
        try:self.verified();state='prepared' if self.choice() else 'disabled'
        except (OSError,ValueError):state='unavailable'
        return dict(state=state,os_registration_observed=False,automatic_cleanup=False)
    def change(self,*,enable):
        require(type(enable) is bool,'notice-mode-invalid')
        # Do not hold the manager lock while the OS waits for the user's click.
        if enable:require(self.command(['--authorize'],35).code==0,'notice-authorization-unconfirmed')
        with self.files.exclusion(self.home.root/'management.lock'):
            if enable:self.verified()
            path=self.home.root/'notice-choice.json';raw=canonical_bytes(dict(version=1,enabled=enable))
            if self.files.exists(path):
                prior=self.files.read(path)
                if prior!=raw:self.files.replace(path,raw,prior)
            else:self.files.create(path,raw)
        return dict(state='enabled' if enable else 'disabled',os_permission_removed=False)
    def resume(self):require(False,'notice-registration-resume-unavailable')
    def check(self,identity):
        require(identity==self.receiver_identity,'notice-receiver-mismatch');require(self.choice(),'notice-registration-required')
        require(self.command(['--check-receiver'],15).code==0,'notice-registration-changed')
        return dict(state='registered',receiver=self.receiver_identity,os_consent_verified=False)
    def identity(self,source):require(False,'notice-receiver-source-unavailable')
    def emit(self,event):
        import re
        require(type(event) is str and re.fullmatch('[0-9a-f]{32}',event),'notice-event-id-invalid');require(self.choice(),'notice-registration-required')
        result=self.command(['--post',event],35)
        return 'emitted' if result.code==0 else 'unknown'
