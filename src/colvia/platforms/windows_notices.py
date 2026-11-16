"""User-scoped native notification registration with explicit partial recovery.

No registration occurs at import, installation or ordinary Work creation. The
Owner's notice-enable command changes only the exact per-user owned keys. Native
qualification is separate from protocol fixtures using a registry double.
"""
from pathlib import Path
import hashlib,re,uuid,subprocess,os
from ..codec import canonical_bytes,decode_canonical,require,RecordError

BASE=r'Software\Classes'

class Registry:
    def __init__(self):
        import winreg
        self.api=winreg;self.root=winreg.HKEY_CURRENT_USER
    def read(self,path):
        a=self.api
        try:key=a.OpenKey(self.root,path)
        except FileNotFoundError:return None
        with key:
            children,count,_=a.QueryInfoKey(key)
            return dict(children=sorted(a.EnumKey(key,i) for i in range(children)),
                values={n:[v,t] for n,v,t in (a.EnumValue(key,i) for i in range(count))})
    def write(self,path,value):
        a=self.api
        if value is None:
            if self.read(path) is not None:a.DeleteKey(self.root,path)
            return
        with a.CreateKeyEx(self.root,path,0,a.KEY_READ|a.KEY_WRITE) as key:
            old=self.read(path)
            for name in set(old['values'])-set(value):a.DeleteValue(key,name)
            for name,(raw,kind) in value.items():a.SetValueEx(key,name,0,kind,raw)
            a.FlushKey(key)

class WindowsNotices:
    receiver_identity=dict(id='windows-user',version=1)
    def __init__(self,home,*,registry=None):
        self.home=home;self.files=home.files;self.registry=registry or Registry()
        value=uuid.uuid5(uuid.NAMESPACE_URL,'colvia:foundation-notice:v1:'+str(home.root).casefold())
        self.app='Colvia.Work.'+value.hex;self.cls='{'+str(value).upper()+'}'
        self.keys=(BASE+'\\AppUserModelId\\'+self.app,BASE+'\\CLSID\\'+self.cls,BASE+'\\CLSID\\'+self.cls+'\\LocalServer32')
    def expected(self,target):
        if target is None:return [None,None,None]
        require(type(target) is str and re.fullmatch('[0-9a-f]{64}',target),'notice-native-digest-invalid')
        path=self.home.root/'notification-tools'/(target+'.exe')
        # subprocess.list2cmdline quotes native Windows argument boundaries.
        command=subprocess.list2cmdline([str(path),'manage','--management-root',str(self.home.root),'notice-activate'])
        return [dict(children=[],values={'DisplayName':['Colvia',1],'CustomActivator':[self.cls,1]}),
            dict(children=['LocalServer32'],values={}),dict(children=[],values={'':[command,1]})]
    def state(self):return [self.registry.read(key) for key in self.keys]
    def executable(self,target):
        self.expected(target);path=self.home.root/'notification-tools'/(target+'.exe')
        self.files.private_directory(path.parent);raw=self.files.read(path,64*1024*1024)
        require(hashlib.sha256(raw).hexdigest()==target,'notice-native-file-changed');return path
    def current(self):
        path=self.home.root/'notice-registration.json'
        if not self.files.exists(path):
            require(self.state()==self.expected(None),'notice-registration-foreign');return None
        value=decode_canonical(self.files.read(path));require(set(value)=={'version','target'} and value['version']==1,'notice-registration-invalid')
        target=value['target'];require(self.state()==self.expected(target),'notice-registration-changed')
        if target is not None:self.executable(target)
        return target
    def candidate_bytes(self):
        _,state=self.home.slots.selection();slot=self.home.slots.verify(state['selected'])
        from ..updates.installation import configuration
        location=self.home.slots.root/'slots'/slot.slot;config=configuration(self.files,location)
        raw=self.files.read(location/config['native_entry'],64*1024*1024);return raw
    def candidate(self):
        raw=self.candidate_bytes();target=hashlib.sha256(raw).hexdigest()
        root=self.home.root/'notification-tools'
        if not root.exists():self.files.create_directory(root)
        self.files.private_directory(root);path=root/(target+'.exe')
        if path.exists():require(self.files.read(path,64*1024*1024)==raw,'notice-native-file-changed')
        else:
            self.files.create(path,raw,executable=True)
        return target
    def inspect(self):
        # Read-only even if the old home metadata is gone. No inferred ownership
        # and no registry cleanup authorization follows from a matching shape.
        rows=self.state();metadata=self.home.root/'notice-registration.json'
        value=decode_canonical(self.files.read(metadata)) if self.files.exists(metadata) else None
        try:self.current();state='recorded' if value is not None else 'unregistered'
        except (RecordError,OSError):state='ownership-unconfirmed'
        return dict(state=state,registration=value,registry=[dict(key=k,observed=v) for k,v in zip(self.keys,rows)],
            pending=self.files.exists(self.home.root/'notice-registration.pending'),automatic_cleanup=False)
    def change(self,*,enable):
        require(type(enable) is bool,'notice-mode-invalid')
        with self.files.exclusion(self.home.root/'management.lock'):
            require(not self.files.exists(self.home.root/'notice-registration.pending'),'notice-registration-pending')
            previous=self.current();target=self.candidate() if enable else None
            if previous==target:return dict(state='enabled' if enable else 'disabled',changed=False)
            operation='notice-'+uuid.uuid4().hex;area=self.home.root/'operations'/operation;self.files.create_directory(area)
            plan=dict(version=1,operation=operation,previous=previous,target=target)
            raw=canonical_bytes(plan);self.files.create(area/'intent.json',raw)
            self.files.create(self.home.root/'notice-registration.pending',raw)
            return self._complete(plan,raw)
    def disable_for_uninstall(self, operation, previous):
        """Called under the uninstall operation's management exclusion."""
        if previous is None:
            require(self.current() is None and not self.files.exists(self.home.root/'notice-registration.pending'),
                    'notice-registration-foreign')
            return
        name='notice-'+hashlib.sha256(('uninstall:'+operation).encode()).hexdigest()[:32]
        pending=self.home.root/'notice-registration.pending'
        area=self.home.root/'operations'/name
        intent=area/'intent.json'
        completion=area/'completed.json'
        plan=dict(version=1,operation=name,previous=previous,target=None)
        raw=canonical_bytes(plan)
        if self.files.exists(pending):
            require(self.files.read(pending)==raw and self.files.read(intent)==raw,'notice-registration-intent-changed')
        elif self.files.exists(completion):
            require(self.files.read(intent)==raw and self.files.read(completion)==canonical_bytes(dict(version=1,state=self.expected(None)))
                    and self.current() is None,'notice-registration-completion-changed')
            return
        else:
            require(self.current()==previous,'notice-registration-changed')
            if not self.files.exists(area):self.files.create_directory(area)
            if not self.files.exists(intent):self.files.create(intent,raw)
            else:require(self.files.read(intent)==raw,'notice-registration-intent-changed')
            self.files.create(pending,raw)
        self._complete(plan,raw)

    def resume(self):
        with self.files.exclusion(self.home.root/'management.lock'):
            raw=self.files.read(self.home.root/'notice-registration.pending');plan=decode_canonical(raw)
            require(set(plan)=={'version','operation','previous','target'} and plan['version']==1 and re.fullmatch('notice-[0-9a-f]{32}',plan['operation']),
                    'notice-registration-invalid')
            require(self.files.read(self.home.root/'operations'/plan['operation']/'intent.json')==raw,'notice-registration-intent-changed')
            return self._complete(plan,raw)
    def partial(self,actual,before,after):
        for now,old,new in zip(actual,before,after):
            if now is None:continue
            allowed_children=set((old or {}).get('children',[]))|set((new or {}).get('children',[]))
            require(set(now['children'])<=allowed_children,'notice-registration-foreign')
            for name,value in now['values'].items():
                require(any(item is not None and item['values'].get(name)==value for item in (old,new)),'notice-registration-foreign')
    def _complete(self,plan,raw):
        before=self.expected(plan['previous']);after=self.expected(plan['target']);actual=self.state()
        self.partial(actual,before,after)
        if plan['target'] is not None:self.executable(plan['target'])
        # Delete leaf before parent. Every observed field must still belong to
        # this recorded transition; foreign values are never reset wholesale.
        order=(0,2,1) if plan['target'] is None else (1,2,0)
        for i in order:
            require(self.state()==actual,'notice-registration-raced')
            self.registry.write(self.keys[i],None if after[i] is None else after[i]['values'])
            actual=self.state();self.partial(actual,before,after)
        require(actual==after,'notice-registration-unconfirmed')
        destination=self.home.root/'notice-registration.json';completed=canonical_bytes(dict(version=1,target=plan['target']))
        if self.files.exists(destination):
            prior=self.files.read(destination)
            require(prior in (canonical_bytes(dict(version=1,target=plan['previous'])),completed),'notice-registration-description-changed')
            if prior!=completed:self.files.replace(destination,completed,prior)
        else:
            require(plan['previous'] is None,'notice-registration-description-missing');self.files.create(destination,completed)
        area=self.home.root/'operations'/plan['operation'];receipt=canonical_bytes(dict(version=1,state=after))
        if self.files.exists(area/'completed.json'):require(self.files.read(area/'completed.json')==receipt,'notice-registration-completion-changed')
        else:self.files.create(area/'completed.json',receipt)
        self.files.remove(self.home.root/'notice-registration.pending',raw)
        return dict(state='enabled' if plan['target'] is not None else 'disabled',changed=True)
    def identity(self,source):
        require(not self.files.exists(self.home.root/'notice-registration.pending'),'notice-registration-pending')
        target=self.current();require(target is not None,'notice-registration-required')
        require(Path(source)==self.executable(target),'notice-receiver-source-mismatch')
        return dict(app=self.app,cls=self.cls)

    def check(self,identity):
        require(identity==dict(id='windows-user',version=1),'notice-receiver-mismatch')
        require(not self.files.exists(self.home.root/'notice-registration.pending'),'notice-registration-pending')
        target=self.current();require(target is not None,'notice-registration-required')
        require(hashlib.sha256(self.candidate_bytes()).hexdigest()==target,'notice-registration-update-required')
        return dict(state='registered',receiver=dict(id='windows-user',version=1),os_consent_verified=False)
    def emit(self,event,*,runner=None,system_directory=None):
        require(type(event) is str and re.fullmatch('[0-9a-f]{32}',event),'notice-event-id-invalid')
        self.check(dict(id='windows-user',version=1))
        if system_directory is None:
            import ctypes
            api=ctypes.WinDLL('kernel32',use_last_error=True);buf=ctypes.create_unicode_buffer(32768)
            api.GetSystemDirectoryW.argtypes=[ctypes.c_wchar_p,ctypes.c_uint];api.GetSystemDirectoryW.restype=ctypes.c_uint
            size=api.GetSystemDirectoryW(buf,len(buf));require(0<size<len(buf),'notice-system-directory-unavailable');system_directory=Path(buf.value)
        executable=Path(system_directory)/'WindowsPowerShell/v1.0/powershell.exe'
        code=("$ErrorActionPreference='Stop';"
            "$doc=[Windows.Data.Xml.Dom.XmlDocument,Windows.Data.Xml.Dom.XmlDocument,ContentType=WindowsRuntime]::new();"
            "$doc.LoadXml('<toast launch=\"b:"+event+"\"><visual><binding template=\"ToastGeneric\">"
            "<text>Colvia · 맡긴 작업</text><text>맡긴 작업에 확인할 내용이 있습니다. 눌러서 상세를 여세요.</text>"
            "</binding></visual><actions><action content=\"보기\" arguments=\"v:"+event+"\" activationType=\"foreground\"/></actions></toast>');"
            "$toast=[Windows.UI.Notifications.ToastNotification,Windows.UI.Notifications,ContentType=WindowsRuntime]::new($doc);"
            "[Windows.UI.Notifications.ToastNotificationManager,Windows.UI.Notifications,ContentType=WindowsRuntime]::CreateToastNotifier('"+self.app+"').Show($toast)")
        if runner is None:
            from .windows_child import WindowsChild
            area=self.home.root/'operations'/('notice-send-'+uuid.uuid4().hex);self.files.create_directory(area)
            runner=WindowsChild(area,files=self.files).run
        # No model, provider or arbitrary Work text is placed in the script.
        env={k:v for k,v in os.environ.items() if k.upper() in ('SYSTEMROOT','WINDIR','USERPROFILE','LOCALAPPDATA','TEMP','TMP')}
        result=runner([str(executable),'-NoProfile','-NonInteractive','-Command',code],cwd=self.home.root,env=env,seconds=20,limit=65536)
        # A non-zero exit cannot prove no toast was queued. Core preserves the
        # emission intent and will never automatically repeat this attempt.
        return 'emitted' if result.code==0 else 'unknown'
