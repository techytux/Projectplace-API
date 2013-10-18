# -*- coding: utf-8 -*-

from urlparse import parse_qs
import random
import time
import oauth2 as oauth
import sys
import requests


def _parse_parameters(parameter_string):
    """
    Takes a string containing parameters and dictifies them.
    @return: dict
    """
    parsed_string = parse_qs(parameter_string)

    for k, v in parsed_string.items():
        if isinstance(v, list):
            parsed_string[k] = v[0]

    return parsed_string


class ApiConnection():

    done_count = 0

    def __init__(self, settings):
        """
        Receives information about an API provider and attempts to establish a connection.

        Takes a settings object that MUST contain the following:

        settings: {
            'api_endpoint': 'https://api.projectplace.com or something',
            'consumer_key': 'CONSUMER_KEY',
            'consumer_secret': 'CONSUMER_SECRET',
        }

        It also optionally supports the addition of oauth_token and oauth_token_secret. That way
        the ApiConnection knows to skip the OAuth dance and allows you to get started using the APIs
        right away. Like this:

        settings: {
            'api_endpoint': 'https://api.projectplace.com or something',
            'consumer_key': 'CONSUMER_KEY',
            'consumer_secret': 'CONSUMER_SECRET',
            'oauth_token': 'OPTIONAL_VALID_ACCESS_TOKEN_KEY',
            'oauth_token_secret': 'OPTIONAL_VALID_ACCESS_TOKEN_SECRET'
        }

        @param settings: a dictionary containing API settings
        @type settings: dict
        """
        self.api_endpoint = settings['api_endpoint']
        self.consumer = oauth.Consumer(key=settings['consumer_key'], secret=settings['consumer_secret'])
        self.signature_method = oauth.SignatureMethod_HMAC_SHA1()
        self.prepared_requests = []
        #if "access_token_key" in settings and "access_token_secret" in settings:
        if "oauth_token" in settings and settings["oauth_token"] and \
           "oauth_token_secret" in settings and settings["oauth_token_secret"]:
            access_token_key = settings['oauth_token']
            access_token_secret = settings['oauth_token_secret']
            self.access_token = oauth.Token(key=access_token_key, secret=access_token_secret)
        else:
            self.access_token = self._establish_connection()

    @property
    def request_token_endpoint(self):
        return self.api_endpoint + '/initiate'

    @property
    def authorize_endpoint(self):
        return self.api_endpoint + '/authorize'

    @property
    def access_token_endpoint(self):
        return self.api_endpoint + '/token'

    def _minimal_oauth_parameters(self):
        """
        All of these parameters are absolutely necessary for an oauth
        request to take place.
        """

        def _generate_nonce():
            """ Returns a string with a random number. """
            return str(random.getrandbits(20))

        def _get_timestamp():
            """ Returns a string with a UNIX timestamp representing UTC now."""
            return str(int(time.time()))

        return {
            'oauth_nonce': _generate_nonce(),
            'oauth_signature_method': 'HMAC-SHA1',
            'oauth_timestamp': _get_timestamp(),
            'oauth_version': '1.0',
            'oauth_consumer_key': self.consumer.key
        }

    def _pack_oauth_request(self, method, url, parameters, consumer, token):
        req = oauth.Request(method=method, url=url, parameters=parameters)

        req.sign_request(self.signature_method, consumer, token)

        auth_header = req.to_header()

        payload = req.get_nonoauth_parameters()

        return auth_header, payload

    def _send_oauth_request(self, method, url, parameters, consumer, token=None, request_body=""):
        """
        Gateway for all OAuth requests.

        @param method: The HTTP verb, "GET" or "POST"
        @type method: str

        @param url: The URL to call
        @type url: str

        @param parameters: a dict with parameters to send to the API, only
        oauth parameters and POST form parameters need to be in here. GET
        parameters are implicitly included by means of the url.
        @type parameters: dict

        @param consumer: the OAuth Consumer object
        @type consumer: oauth2.Consumer

        @param token: the oauth_token, either a request or an access token will suffice
        @type token: oauth2.Token
        """
        auth_header, payload = self._pack_oauth_request(method, url, parameters, consumer, token)


        if method == "GET":
            response = requests.get(url, headers=auth_header, verify=False)

        elif method == "POST":
            response = requests.post(url, headers=auth_header, verify=False, data=payload)

        elif method == "PUT":
            response = requests.put(url, headers=auth_header, verify=False, data=request_body)

        else:
            raise ValueError('Invalid value for method parameter: "%s" (valid values are: GET,POST,PUT)'%method)

        return response

    def _get_prepared_oauth_request(self, method, url, parameters, consumer, token=None, request_body=""):
        auth_header, payload = self._pack_oauth_request(method, url, parameters, consumer, token)

        prepared_request = None

        if method == "GET":
            prepared_request = requests.Request("GET", url, headers=auth_header)

        if method == "POST":
            prepared_request = requests.Request("POST", url, headers=auth_header, data=payload)

        if method == "PUT":
            prepared_request = requests.Request("PUT", headers=auth_header, data=request_body)

        return prepared_request.prepare()

    def _get_request_token(self):
        """ Returns an oauth2.Token representing the request token. """
        parameters = self._minimal_oauth_parameters()

        response = self._send_oauth_request('GET', self.request_token_endpoint, parameters, self.consumer)

        parsed_response = _parse_parameters(response.text)

        return oauth.Token(key=parsed_response['oauth_token'], secret=parsed_response['oauth_token_secret'])

    def _authorize(self, request_token):
        """
        Authorizes the opening a web browser to the authorize endpoint and asking the user for the resulting
        oauth_verifier

        @return: oauth2.Token representing the verified request token.
        """
        import webbrowser

        authorize_url = "%s?oauth_token=%s" % (self.authorize_endpoint, request_token.key)

        print ""
        print "Missing user specific credentials. Initializing process to collect these."
        print " - 1. Will launch web browser with URL to authorization process"
        print "      (URL: %s)"%authorize_url
        print " - 2. You fill in user details and then continue to grant permission."
        print " - 3. Page will reload."
        print "      Copy value of oauth_verifier parameter from address bar."
        #print " - 4. Enter oauth_verifier value when prompted for it here..."
        webbrowser.open(authorize_url)
        oauth_verifier = raw_input(" - 4. Enter OAuth verifier: ")
        request_token.set_verifier(oauth_verifier)

        return request_token

    def _get_access_token(self, request_token):
        """
        Exchanges the verified request token for an access token.

        @return: oauth2.Token representing the access token
        """
        parameters = self._minimal_oauth_parameters()
        parameters['oauth_token'] = request_token.key
        parameters['oauth_verifier'] = request_token.verifier

        response = self._send_oauth_request('GET', self.access_token_endpoint, parameters, self.consumer, request_token)

        parsed_response = _parse_parameters(response.text)

        return oauth.Token(key=parsed_response['oauth_token'], secret=parsed_response['oauth_token_secret'])

    def _establish_connection(self):
        """
        Establishes a trusted connection with the provider's APIs.

        This is signified by the access token which is a permanent credential to
        act on behalf of a user.
        """
        authorized_request_token = self._authorize(self._get_request_token())
        access_token = self._get_access_token(authorized_request_token)
        
        print
        print "Collected user credentials. Save these in your credentials config:"
        values = str(access_token).split('&')
        print '  ',values[0]
        print '  ',values[1]
        
        return access_token

    def _pack_request(self, url, parameters):
        oauth_parameters = self._minimal_oauth_parameters()
        oauth_parameters['oauth_token'] = self.access_token.key

        parameters = dict(parameters.items() + oauth_parameters.items())

        url = self.api_endpoint + url

        return url, parameters

    def request(self, method, url, parameters={}, request_body=""):
        """
        Performs an API request and returns a requests.response object.
        """
        url, parameters = self._pack_request(url, parameters)

        response = self._send_oauth_request(method, url, parameters, self.consumer, self.access_token, request_body)

        return response

    def _get_prepared_request(self, which):
        """
        This method returns a Requests.PreparedRequest ready for execution.

        @param which: the index of the method signature representing the request we want to send
        """
        method, url, parameters, consumer, access_token, request_body = self.prepared_requests[which]

        url, parameters = self._pack_request(url, parameters)

        return self._get_prepared_oauth_request(method, url, parameters, consumer, access_token, request_body)

    def prepare_request(self, method, url, parameters={}, request_body="", times=1):
        """
        This method lines up the signature needed to formulate a Requests.PreparedRequest. It simply stores a tuple
        of the signature on the prepared_requests list.
        """
        for i in range(times):
            self.prepared_requests.append((method, url, parameters, self.consumer, self.access_token, request_body))

    def send_prepared_requests(self):
        """
        Uses the stored request signatures from the prepared_requests list to create Requests.PreparedRequest
        objects. Each PreparedRequest is then sent in its own thread and prints the response status code to stdout.
        """
        from threading import Thread

        session = requests.Session()

        concurrent = len(self.prepared_requests)

        def send_it(prepared_request, which):
            response = session.send(prepared_request)
            sys.stdout.write("%s " % response.status_code)
            self.done_count += 1
            if (self.done_count == concurrent):
                sys.stdout.write("Done!")

        for i in range(concurrent):
            prepared_request = self._get_prepared_request(i)
            t = Thread(target=send_it, args=(prepared_request, i,))
            t.daemon = True
            t.start()

        self.prepared_requests = []

        # To prevent the process from dying due to terminal exit
        try:
            input("Sending %s requests to %s, press ENTER to cancel\r\n" % (concurrent, self.api_endpoint))
        except:
            pass






