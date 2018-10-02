from setuptools import setup, find_packages
from codecs import open
from os import path
from sys import version_info

__version__ = '0.0.9'
__title__ = 'django-saml2-pro-auth'
__version_info__ = __version__ 
__author__ = 'Jonathan Davila'
__author_email__ = 'jonathan@davila.io'
__license__ = 'MIT'
__copyright__ = 'Copyright 2017 MindPoint Group'

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

if __name__ == "__main__":

    setup(
        name=__title__,
        version=__version__,
        description="SAML2 authentication backend for Django wrapping OneLogin's python-saml package https://github.com/onelogin/python-saml",
        long_description=long_description,
        url='https://github.com/MindPointGroup/django-saml2-pro-auth',
        author=__author__,
        author_email=__author_email__,
        license=__license__,
        classifiers=[
            'Development Status :: 4 - Beta',
            'Intended Audience :: Developers',
            'Framework :: Django :: 1.8',
            'Framework :: Django :: 1.10',
            'Framework :: Django :: 1.11',
            'Topic :: Security',
            'Topic :: System :: Systems Administration :: Authentication/Directory',
            'License :: OSI Approved :: MIT License',
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3.4',
            'Programming Language :: Python :: 3.5',
            'Programming Language :: Python :: 3.6',
        ],

        keywords='sso single-signon authentication saml saml2 django development okta onelogin',
        packages=find_packages(where="src"),
        package_dir={
            '': 'src',
        },
        install_requires=[
            'python3-saml',
            'six'
        ],
        tests_require=[
            'django',
        ],
        extras_require={
            'dev': ['check-manifest'],
        },
        test_suite='tests',
        include_package_data=True,

    )
