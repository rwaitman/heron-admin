'''setup.py -- heron_wsgi package information

Usage:

A virtuale environment is recommended:

  % mkdir haenv
  % virtualenv haenv
  % . haenv/bin/activate

Then:

  % export ORACLE_HOME=/usr/lib/oracle/11.2/client64/  # salt to taste
  (haenv)% python setup.py develop

Then compare the output of `pip freeze` with requirements.txt.


Be careful with site-packages dependencies. You don't want:
pkg_resources.VersionConflict: (zope.interface 3.6.1
 (/usr/lib/python2.7/dist-packages),
  Requirement.parse('zope.interface>=3.8.0'))

Older notes:

Starting from scratch seems to work, though it depends
on some Ubuntu modules.

$ sudo apt-get install libsasl2-dev libmysqlclient-dev python2.6-dev
or:
$ sudo zypper install libmysqlclient-devel

$ curl -O https://raw.github.com/pypa/virtualenv/master/virtualenv.py
$ mv virtualenv.py ~/bin/virtualenv
$ chmod +x ~/bin/virtualenv
$ virtualenv --python=python2.6 --no-site-packages haenv/
$ . haenv/bin/activate


'''

__author__ = 'Dan Connolly <dconnolly@kumc.edu>'
__copyright__ = '(c) 2011 University of Kansas Medical Center'
__contact__ = 'http://informatics.kumc.edu/work/wiki/HeronAdminDev'
__license__ = 'Apache 2'
__version__ = '0.2'


import os
import sys

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()
CHANGES = '@@TODO'  # open(os.path.join(here, 'CHANGES.txt')).read()

requires = [
    'injector',
    'genshi',
    'pyramid==1.2.1',
    'pyramid_mailer',
    # pyramid_mailer-0.5.tar.gz#md5=115ed5a721e9f881e59529b901568aa4
    # repoze.sendmail-2.3.tar.gz#md5=a2cc03e2dcac35bbdc44724de5f3efb2
    # transaction-1.1.1.tar.gz#md5=30b062baa34fe1521ad979fb088c8c55

    'SQLAlchemy==0.7.2',
    'python-ldap',
    'cx_Oracle',
    'MySQL-python',
    'py-dom-xpath',
    # py-dom-xpath-0.1.tar.gz 4bbca5671245421e93ef2c1ea4e6e36810ccecbc
    #'pyinotify'
    ]

if sys.version_info[:3] < (2, 5, 0):
    requires.append('pysqlite')

setup(name='heron_wsgi',
      version=__version__,
      description=README.split('\n', 1)[0],
      long_description=README + '\n\n' + CHANGES,
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        ],
      author=__author__.split('<')[0][:-1],
      author_email=__author__.split('<')[1][:-1],
      url=__contact__,
      license=__license__,
      keywords='web wsgi hipaa policy enforcement',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
# TODO: learn how test_suite works
#     test_suite='heron_acct',
      install_requires=requires,
      tests_require=requires + ['lxml'],
      entry_points={
        'console_scripts':
            ['logwatch=heron_wsgi.logwatch:main'],
        'paste.app_factory':
            #['main = heron_wsgi.heron_srv:app_factory']
            ['main = heron_wsgi:main']
        },
      paster_plugins=['pyramid'],
      package_data={'heron_wsgi': ['templates/*.html', 'templates/*.xml']},
      data_files=[('apache_mod_wsgi',
                   ['apache/heron_admin.conf',
                    'apache/heron_wsgi.py',
                    'apache/test.wsgi']),
                  ('av',
                   ['heron_wsgi/templates/av/220px-Heron_tricol_01.JPG']),
                    ]
      )
