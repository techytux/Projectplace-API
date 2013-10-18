#@param conn: Connection (includign authentication info) to API
#@type conn: ppapiaccess.core.ApiConnection
conn = None

from os.path import dirname, join as joinpath
default_confpath = joinpath(dirname(__file__),'apiaccess.cfg')

def minimum_cred_provided(creds):
    """
    Verify that minimum credential info is provided
    @param creds: Credentials info
    @type creds: {'api_endpoint':,'<value>', 'consumer_key':'<value>','consumer_secret':'<value>'}
    """
    if not 'api_endpoint' in creds or not creds['api_endpoint']:
        raise ValueError('Missing mandatory key "api_endpoint" in parameter "credentials"')
    elif not 'consumer_key' in creds or not creds['consumer_key']:
        raise ValueError('Missing mandatory key "consumer_key" in parameter "credentials"')
    elif not 'consumer_secret' in creds or not creds['consumer_secret']:
        raise ValueError('Missing mandatory key "consumer_secret" in parameter "credentials"')
    

def connect(credentials=None):
    """
    Create session to Projectplace API. This method should be called with credentials
    before trying to access any data through the API to initiate a session (else those
    will fail). If the credentials only include consumer credentials (general) and not
    also user credentials (specific for user account at Projectplace.com) then a manual
    authentication process will be initiated (you want to avoid this).
    
    @param credentials: Contain credential details for authentication with Projectplace.com API
    @type credentials: {'api_endpoint': 'normaly this is https://api.projectplace.com',
                        'consumer_key': 'CONSUMER_KEY',
                        'consumer_secret': 'CONSUMER_SECRET',
                        'oauth_token': 'OPTIONAL_VALID_ACCESS_TOKEN_KEY_FOR_USER',
                        'oauth_token_secret': 'OPTIONAL_VALID_ACCESS_TOKEN_SECRET_FOR_USER'
        }
    """
    global conn
    if conn == None:
        from ppapiaccess.core import ApiConnection

        if not credentials:
            raise ValueError('Parameter credentials required for API initialization')
        else:
            minimum_cred_provided(credentials)

        conn = ApiConnection(credentials)
    return conn



def get_projects(name='', id=0):
    """
    Get available projects at Projectplace.com 
    @param name: Optional Project name, if provided will only return corresponding project
    @type name: '<name>'
    @param id: Optional Project id, if provided will only return corresponding project
    @type id: <id>
    @return: List of projects
    """
    from ppapiaccess import connect

    global conn
    if not conn: conn = connect()
    
    response = conn.request('GET','/1/user/me/projects.json')
    if response.status_code != 200:
        raise RuntimeError('Error occured. Server returned http status code %d. Return message: %s'%(response.status_code, response.text))

    data = response.json()
    
    if name or id:
        name = name.lower()
        for project in data:
            if project['name'].lower() == name or project['id'] == id:
                return project
        return dict()   # Empty dict
    else:
        return data
        


def get_me():
    """
    Return basic profile info from Projectplace.com about the user account used to access API
    """
    from ppapiaccess import connect
    
    global conn
    if not conn: conn = connect()
    
    response = conn.request('GET','/1/user/me/profile.json')
    if response.status_code != 200:
        raise RuntimeError('Error occured. Server returned http status code %d. Return message: %s'%(response.status_code, response.text))
    return response.json()







