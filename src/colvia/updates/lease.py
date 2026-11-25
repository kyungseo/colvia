"""Installed runtime lease around each short authority transaction.

An update takes the runtime lock exclusively; installed readers/writers share it.
An old process cannot publish after the selection changes. Source-only stores do
not acquire this lease and must never be labelled installed-entry evidence.
"""
from contextlib import contextmanager
from ..codec import require
from ..storage.sqlite import GenerationStore


class RuntimeLease:
    def __init__(self,slots,*,expected_pointer=None,_retain_inventory=None):
        self.slots=slots
        require(not slots.files.exists(slots.root.parent/'uninstall.json'),'uninstall-transition-pending')
        self.expected,self.selection=slots.selection()
        require(expected_pointer is None or self.selection['selected']==expected_pointer,'runtime-entry-selection-changed')
        if _retain_inventory is None:
            self.verified=slots.verify(self.selection['selected'])
        else:
            self.verified=slots.verify(self.selection['selected'],_retain_inventory=_retain_inventory)
        self.check()
    def check(self):
        require(not self.slots.files.exists(self.slots.root.parent/'uninstall.json'),'uninstall-transition-pending')
        require(self.slots.selection()[0]==self.expected,'runtime-selection-changed')
    @contextmanager
    def hold(self):
        with self.slots.files.exclusion(self.slots.root/'runtime.lock',shared=True):
            self.check()
            try:yield
            finally:self.check()


def open_managed_store(authority,slots,*,readonly=False,expected_pointer=None,_entry=None):
    lease = None if _entry is None else _entry._take_verified_lease(slots,expected_pointer)
    if lease is None:
        lease=RuntimeLease(slots,expected_pointer=expected_pointer)
    pointer=authority.pointer_value()
    def check_pointer():
        require(authority.pointer_value()==pointer,'active-generation-changed')
    def active():
        lease.check()
        check_pointer()
    # All read and write transactions hold the shared runtime lock and check
    # selection on entry and exit. Only writes repeat that check inside both
    # store guards; reads still check their authority pointer at both guards.
    return GenerationStore(authority.root/'stores'/pointer['generation']/'state.sqlite3',
        project=authority.project,instance=pointer['instance'],generation=pointer['generation'],readonly=readonly,
        active_check=active,write_check=lambda:require(not authority.files.exists(authority.root/'pending.json'),'activation-pending'),
        reader_capabilities=lease.verified.read_capabilities,writer_capabilities=lease.verified.write_capabilities,
        transaction_scope=lease.hold,read_active_check=check_pointer)
