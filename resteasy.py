# -*-coding: utf-8 -*-

"""
Author          : Arijit Basu <sayanarijit@gmail.com>
Website         : https://sayanarijit.github.io
"""

from __future__ import absolute_import, unicode_literals
import json
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning


class HTTPError(Exception):
    '''Status code returned by server not in range 200-299'''
    def __init__(self, status, content):
        Exception.__init__(self, 'Server returned HTTP status code: %s\n%s' % (status, content))

class InvalidResponseError(Exception):
    '''Data returned by server could not be decoded'''
    def __init__(self, content):
        Exception.__init__(self, 'Server returned incompatible response:\n'+content)


class RESTEasy(object):
    """REST API client session creator"""

    def __init__(self, base_url, auth=None, verify=False, cert=None, timeout=None,
                 encoder=json.dumps, decoder=json.loads, debug=False):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.auth = auth
        self.session.verify = verify
        self.session.cert = cert
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        self.timeout = timeout
        self.encoder = encoder
        self.decoder = decoder
        self.debug = debug

    def route(self, *args):
        """Return endpoint object"""

        return APIEndpoint(
            endpoint=self.base_url + '/' + ('/'.join(map(str, args))),
            session=self.session, timeout=self.timeout,
            encoder=self.encoder, decoder=self.decoder, debug=self.debug
        )


class APIEndpoint(object):
    """API endpoint that supports CRUD operations"""

    def __init__(self, endpoint, session, timeout=None,
                 encoder=json.dumps, decoder=json.loads, debug=False):
        self.endpoint = endpoint
        self.session = session
        self.timeout = timeout
        self.encoder = encoder
        self.decoder = decoder
        self.debug = debug

    def route(self, *args):
        """Return endpoint object"""

        return APIEndpoint(
            endpoint=self.endpoint + '/' + ('/'.join(map(str, args))),
            session=self.session, timeout=self.timeout,
            encoder=self.encoder, decoder=self.decoder, debug=self.debug
        )

    def do(self, method, kwargs={}):
        """Do the HTTP request"""

        method = method.upper()

        if self.debug:
            return dict(endpoint=self.endpoint, method=method, kwargs=kwargs, session=self.session, timeout=self.timeout)

        if method == 'GET':
            response = self.session.get(self.endpoint,
                    params=kwargs, timeout=self.timeout)
        else:
            response = self.session.request(method, self.endpoint,
                    data=self.encoder(kwargs), timeout=self.timeout)

        content = response.content.decode('latin1')
        if response.status_code not in range(200,300):
            raise HTTPError(response.status_code, content)

        try:
            return self.decoder(content)
        except Exception:
            raise InvalidResponseError(content)

    def get(self, **kwargs): return self.do('GET', kwargs)
    def post(self, **kwargs): return self.do('POST', kwargs)
    def put(self, **kwargs): return self.do('PUT', kwargs)
    def patch(self, **kwargs): return self.do('PATCH', kwargs)
    def delete(self, **kwargs): return self.do('DELETE', kwargs)
