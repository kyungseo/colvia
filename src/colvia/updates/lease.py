"""Installed runtime lease around each short authority transaction.

An update takes the runtime lock exclusively; installed readers/writers share it.
An old process cannot publish after the selection changes. Source-only stores do
not acquire this lease and must never be labelled installed-entry evidence.
"""
from contextlib import contextmanager
from ..codec import require
from ..storage.sqlite import GenerationStore


class RuntimeLease:
    def __init__(self,slots,*,expected_pointer=None):
        self.slots=slots;self.expected,self.selection=slots.selection()
        require(expected_pointer is None or self.selection['selected']==expected_pointer,'runtime-entry-selection-changed')
        self.verified=slots.verify(self.selection['selected'])
        self.check()
    def check(self):
        require(self.slots.selection()[0]==self.expected,'runtime-selection-changed')
    @contextmanager
    def hold(self):
        with self.slots.files.exclusion(self.slots.root/'runtime.lock',shared=True):
            self.check()
            try:yield
            finally:self.check()


def open_managed_store(authority,slots,*,readonly=False,expected_pointer=None):
    lease=RuntimeLease(slots,expected_pointer=expected_pointer);pointer=authority.pointer_value()
    def active():
        lease.check();require(authority.pointer_value()==pointer,'active-generation-changed')
    return GenerationStore(authority.root/'stores'/pointer['generation']/'state.sqlite3',
        project=authority.project,instance=pointer['instance'],generation=pointer['generation'],readonly=readonly,
        active_check=active,write_check=lambda:require(not authority.files.exists(authority.root/'pending.json'),'activation-pending'),
        reader_capabilities=lease.verified.read_capabilities,writer_capabilities=lease.verified.write_capabilities,
        transaction_scope=lease.hold)
