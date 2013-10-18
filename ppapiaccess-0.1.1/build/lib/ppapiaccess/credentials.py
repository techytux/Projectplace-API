def credentials_from_cfg(filepath):
    """
    Will extract credentials from specified configuration file. File should have a
    standard key=value format. The following keys will be extracted:
    api_endpoint (mandatory)
    consumer_key (mandatory)
    consumer_secret (mandatory)
    access_token_secret (optional)
    access_token_key (optional
    
    @param filepath: Path to configuration file
    @type filepath: '<file path>'
    @return: {Configurations}
    """
    import ConfigParser
    settings = dict()
    
    config = ConfigParser.ConfigParser()
    config.read(filepath)

    settings['api_endpoint'] = config.get('Basic API configuration','api_endpoint')
    settings['consumer_key'] = config.get('Basic API configuration','consumer_key')
    settings['consumer_secret'] = config.get('Basic API configuration','consumer_secret')

    value = config.get('User Credentials','oauth_token_secret')
    if value:
        settings['oauth_token_secret'] = value

    value = config.get('User Credentials','oauth_token')
    if value:
        settings['oauth_token'] = value

    return settings






