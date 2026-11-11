"""Explicit metadata-only renewal bound to one immutable preparation.

Callers hold the management exclusion. The returned descriptor replaces only
in-memory authentication evidence, never the original plan or payload bytes.
"""
import hashlib
from ..codec import canonical_bytes,decode_canonical,require
from ..storage.sqlite import _token


def forward_allowed(home,operation):
    _token(operation)
    require(not home.files.exists(home.root/'operations'/operation/'retried-by.json'),'installation-attempt-superseded')
    require(not home.files.exists(home.root/'operations'/operation/'quarantine-intent.json'),'initial-quarantine-started')
    require(not home.files.exists(home.root/'operations'/operation/'rollback.json'),
            'release-rollback-started')


def target_identity(download):
    return {key:download[key] for key in ('path','length','sha256','custom')}


def renew(home,trust,*,operation,original,download,renewal,cancelled=lambda:False):
    _token(operation);_token(renewal);forward_allowed(home,operation)
    area=home.root/'operations'/operation;home.files.private_directory(area)
    attempt=area/('renewal-'+renewal);home.files.create_directory(attempt)
    binding=dict(version=1,operation=operation,original=original,target=target_identity(download))
    home.files.create(attempt/'intent.json',canonical_bytes(binding))
    def same(description):
        require(target_identity(description)==binding['target'],'renewal-target-changed')
        return True # No target body download, even on an exact match.
    fresh=trust.stage(download['path'],destination=attempt/'never-download',cancelled=cancelled,already_present=same)
    require(fresh.get('staged') is None and target_identity(fresh)==binding['target'],'renewal-target-changed')
    trust.activation_check(fresh)
    raw=canonical_bytes(dict(binding,download=fresh))
    home.files.create(attempt/'renewed.json',raw)
    return dict(state='reauthenticated',operation=operation,renewal=renewal+'@'+hashlib.sha256(raw).hexdigest())


def effective(home,trust,*,operation,original,download,renewal=None):
    forward_allowed(home,operation)
    if renewal is not None:
        require(type(renewal) is str and renewal.count('@')==1,'renewal-reference-invalid')
        name,digest=renewal.split('@');_token(name)
        require(len(digest)==64 and all(c in '0123456789abcdef' for c in digest),'renewal-reference-invalid')
        raw=home.files.read(home.root/'operations'/operation/('renewal-'+name)/'renewed.json',4*1024*1024)
        require(hashlib.sha256(raw).hexdigest()==digest,'renewal-receipt-changed')
        value=decode_canonical(raw)
        require(type(value) is dict and set(value)=={'version','operation','original','target','download'} and
                type(value['version']) is int and value['version']==1 and value['operation']==operation and
                value['original']==original and value['target']==target_identity(download) and
                target_identity(value['download'])==value['target'],'renewal-preparation-mismatch')
        download=value['download']
    trust.activation_check(download)
    return download


def metadata_only(fetcher,metadata_url):
    """Pinned verifier metadata names only; no target download through this port."""
    import re
    from tuf.ngclient.fetcher import FetcherInterface
    from .trust import _url
    prefix=_url(metadata_url)
    class MetadataOnly(FetcherInterface):
        def _fetch(self,url):
            require(type(url) is str and url.startswith(prefix) and re.fullmatch(r'(?:[0-9]+\.)?(?:root|timestamp|snapshot|targets)\.json',url[len(prefix):]),
                    'renewal-target-download-forbidden')
            return fetcher.fetch(url)
    return MetadataOnly()
