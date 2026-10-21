"""Instrumented real installed CLI; original guard and publication calls execute."""
from __future__ import annotations
import builtins
import contextlib
import fcntl
import json
import os
from pathlib import Path
import runpy
import sys
import time

target, evidence, config_path = map(Path, sys.argv[1:4])
config=json.loads(config_path.read_bytes())
held=False
def emit(name, **extra):
    payload={"event":name,"pid":os.getpid(),"pgid":os.getpgrp(),"monotonic_ns":time.monotonic_ns(),
             "guard_held":held,**extra}
    staged=evidence/(name+".writing")
    with staged.open("x") as stream:
        json.dump(payload,stream);stream.flush();os.fsync(stream.fileno())
    os.replace(staged,evidence/(name+".json"))

def wait_for(path):
    deadline=time.monotonic()+120
    while not path.exists():
        if time.monotonic()>deadline:raise TimeoutError("fixture barrier deadline")
        time.sleep(.01)

def pause(point,path):
    if config.get("phase")!=point:return
    if not held:raise RuntimeError("publication barrier outside real guard")
    emit("barrier",point=point,path=str(path.relative_to(target)))
    wait_for(evidence/"continue")

original_flock=fcntl.flock
def observed_flock(fd,operation):
    if operation==fcntl.LOCK_EX:emit("lock-attempting")
    return original_flock(fd,operation)
fcntl.flock=observed_flock

original_import=builtins.__import__
workspace_patched=False
work_patched=False
def instrument(name,globals=None,locals=None,fromlist=(),level=0):
    global workspace_patched,work_patched
    module=original_import(name,globals,locals,fromlist,level)
    workspace=sys.modules.get("hv2ref.workspace")
    if not workspace_patched and workspace is not None and hasattr(workspace,"writer_guard"):
        workspace_patched=True
        original_guard=workspace.writer_guard
        original_directory=workspace._durable_directory
        @contextlib.contextmanager
        def guard(*args,**kwargs):
            global held
            emit("waiting")
            if config["mode"]=="contend":wait_for(evidence.parent/"start")
            with original_guard(*args,**kwargs):
                held=True;emit("acquired")
                if config["mode"]=="contend":wait_for(evidence/"permit")
                try:yield
                finally:emit("leaving");held=False
            emit("released")
        def directory(path):
            original_directory(path)
            if Path(path).parts[-2:]==("continuation","selections"):
                pause("after-directories",Path(path))
        workspace.writer_guard=guard
        workspace._durable_directory=directory
    work=sys.modules.get("hv2ref.work")
    if not work_patched and work is not None and hasattr(work,"WorkStore"):
        work_patched=True
        original_immutable=work._publish_immutable
        original_current=work._publish_current
        def immutable(path,value):
            original_immutable(path,value)
            kind=value.get("record_type")
            if kind=="continuation-current":pause("after-initial-current",path)
            elif kind=="continuation-choice":pause("after-choice",path)
            elif kind=="continuation-selection":pause("after-selection",path)
        def current(target,path,value,inject_at):
            original_current(target,path,value,inject_at)
            if value.get("record_type")=="continuation-current":pause("after-current",path)
        work._publish_immutable=immutable;work._publish_current=current
    return module
builtins.__import__=instrument

original_replace=os.replace
def replace(source,destination,*args,**kwargs):
    path=Path(destination)
    if path.parts[-2:]==("continuation","current.json"):
        pause("after-staged-current",path)
    return original_replace(source,destination,*args,**kwargs)
os.replace=replace
sys.argv=[str(target/"colvia"),*config["command"]]
runpy.run_path(str(target/"colvia"),run_name="__main__")
