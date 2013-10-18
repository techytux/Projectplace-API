from setuptools import setup

setup(
    name='ppapiaccess',
    version='0.1.1',
    author='Christopher Dalid, Jon Nylander',
    author_email='christopher.dalid@projectplace.com',
    packages=['ppapiaccess'],
    license='license.txt',
    description='Provides request handling (including OAuth2) for Projectplace.com API',
    long_description=open('readme.txt').read(),
    include_package_data = True, # This includes the .cfg specified in manifest.in
    install_requires=[
        "httplib2 >= 0.8",
        "oauth2 >= 1.5.211",
        "requests == 1.2.0",
    ],
)
