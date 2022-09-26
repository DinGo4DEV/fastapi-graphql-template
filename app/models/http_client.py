from re import S
from requests import session
from arango.http import DefaultHTTPClient
from requests import Session
from requests.adapters import HTTPAdapter
from requests_toolbelt import MultipartEncoder
from urllib3.util.retry import Retry

from arango.response import Response
from arango.typings import Headers
import urllib3
import logging
from aioarango.http import DefaultHTTPClient as AsyncDefaultHTTPClient
import httpx

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
class HTTPClient(DefaultHTTPClient):
    REQUEST_TIMEOUT = 60000
    def create_session(self, host: str) -> session:
        """Create and return a new session/connection.

        :param host: ArangoDB host URL.
        :type host: str
        :returns: requests session object
        :rtype: requests.Session
        """
        retry_strategy = Retry(
            total=self.RETRY_ATTEMPTS,
            backoff_factor=self.BACKOFF_FACTOR,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"],
        )
        http_adapter = HTTPAdapter(max_retries=retry_strategy)

        session = Session()
        
        session.mount("https://", http_adapter)
        session.mount("http://", http_adapter)
        session.verify = False
        return session
    
## Disable unused logging 
logging.getLogger('httpcore').setLevel(logging.WARN)
logging.getLogger('httpx').setLevel(logging.WARN)

class AsyncHTTPClient(AsyncDefaultHTTPClient):
    def create_session(self, host: str) -> httpx.AsyncClient:
        """Create and return a new session/connection.

        :param host: ArangoDB host URL.
        :type host: str | unicode
        :returns: httpx client object
        :rtype: httpx.AsyncClient
        """
        transport = httpx.AsyncHTTPTransport(retries=self.RETRY_ATTEMPTS,verify=False)
        return httpx.AsyncClient(transport=transport,verify=False)