"""Narrow HTTPS download port for the pinned verifier; no redirects or retries."""
import time
from ..codec import require
from .trust import _url


def https_fetcher(*,metadata_url,target_url,seconds=120,requests=128,bytes_limit=1024**3):
    from tuf.ngclient.fetcher import FetcherInterface
    from tuf.api.exceptions import DownloadHTTPError
    import urllib3
    require(type(seconds) in (int,float) and 0<seconds<=300 and type(requests) is int and 0<requests<=256 and
            type(bytes_limit) is int and 0<bytes_limit<=2*1024**3,'invalid-update-fetch-budget')
    origins=(_url(metadata_url),_url(target_url))
    class Fetcher(FetcherInterface):
        def __init__(self):
            self.deadline=time.monotonic()+seconds;self.requests=0;self.bytes=0
            self.pool=urllib3.PoolManager(cert_reqs='CERT_REQUIRED',retries=False)
        def close(self):self.pool.clear()
        def _fetch(self,url):
            require(any(url.startswith(base) for base in origins) and '?' not in url and '#' not in url and
                    '/..' not in url and '@' not in url,'update-fetch-origin')
            self.requests+=1;require(self.requests<=requests,'update-fetch-request-limit')
            remaining=self.deadline-time.monotonic();require(remaining>0,'update-fetch-deadline')
            response=self.pool.request('GET',url,redirect=False,retries=False,preload_content=False,
                timeout=urllib3.Timeout(connect=min(5,remaining),read=min(5,remaining)))
            try:
                if response.status!=200:raise DownloadHTTPError('Update download unavailable',response.status)
                for chunk in response.stream(64*1024,decode_content=False):
                    require(time.monotonic()<self.deadline,'update-fetch-deadline')
                    self.bytes+=len(chunk);require(self.bytes<=bytes_limit,'update-fetch-byte-limit')
                    yield chunk
            finally:response.close();response.release_conn()
    return Fetcher()
