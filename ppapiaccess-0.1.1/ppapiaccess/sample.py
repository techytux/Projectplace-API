"""
Sample script to show how to work with the ppapiaccess library.
This script includes calls to two basic data fetching
functions that are available in the library: get_me() and
get_projects().
To create more such functions look at the definitions of get_me
and get_project and you should be able to get started quickly.
Documentation is available at http://api.projectplace.com. 

By C.Dalid, 2013-05-15
"""

def main(creds):
    """
    Authenticate with Projectplace.com API and present
    some basic info about the user.

    @param creds: Credentials
    @type creds: {...} (see ppapiaccess.connect for further info)
    """
    from ppapiaccess import connect, get_me, get_projects

    connect(creds)
    
    print
    print "Info fetched via API regarding current user:"
    data = get_me()
    print " - Name: %s %s"%(data['first_name'],data['last_name'])
    print " - Email:",data['email']
    print " - Number of available projects:",len(get_projects())
    print
    
    

if __name__ == '__main__':

    
    ## TODO: Support provision of credentials via arguments?
    ##       (Individual credentials, path to conf file)

    # Make use of default configuration file. This can be replaced
    # by your own configuration file, view existing for syntax.
    confpath = '/Users/vaibhav/Documents/workspace/pp_api_utils_ppapiaccess/ppapiaccess/apiaccess.cfg'
    if not confpath:
        from ppapiaccess import default_confpath
        confpath = default_confpath

    # Extract credentials from config file. 
    from ppapiaccess.credentials import credentials_from_cfg
    creds = credentials_from_cfg(filepath=confpath)

    # Values for "oauth_token_secret" and "oauth_token" are not
    # available by default in the default configuration file
    # (default_confpath). These values refer to user specific
    # credentials and must be obtained through a OAuth authentication
    # process. If you haven't specified them in config file or here
    # in this file then the process will automatically trigger such
    # OAuth authentication process when you run this script.
    # Afterwards you can take the generated token & secret and either
    # put them here in the file to use by this script alone or
    # in the config file to make use of them in all scripts that
    # uses the ppapiaccess lib.

    #creds['oauth_token_secret'] = ''
    #creds['oauth_token'] = ''

    ## Call main()
    main(creds)

    import sys
    print 'Script (%s) finished.'%sys.argv[0]

