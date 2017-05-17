#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from setuptools import setup, find_packages
import versioneer

commands = versioneer.get_cmdclass().copy()
here = os.path.abspath(os.path.dirname(__file__))
README_LOCAL = open(os.path.join(here, 'README.rst')).read()
README_GLOBAL = open(os.path.join(here, 'README-NP.rst')).read()

requires = [
	'setuptools >= 17.1',
	'packaging >= 16.1',
	'python-dateutil',
	'dogpile.cache >= 0.4.1',
	'repoze.tm2',

	'SQLAlchemy >= 1.0',
	'zope.sqlalchemy',
	'transaction',
	'alembic >= 0.8.3',

	'waitress >= 0.7',
	'pyramid >= 1.5',
	'pyramid_mako >= 0.3',
	'pyramid_rpc >= 0.5.2',
	'pyramid_debugtoolbar >= 1.0',
	'pyramid_redis_sessions >= 0.9b5',
	'pyramid_mailer >= 0.13',
	'Babel',
	'lingua',
	'lxml',

	'cliff >= 1.7.0',

	'tornado',
	'sockjs-tornado',
	'tornado-redis',
	'tornado-celery',

	'celery >= 4.0',
	'kombu != 3.0.34',
	'msgpack-python >= 0.4',

	'reportlab >= 3.1'
]
extras_require = {
	':python_version<"3.2"' : [
		'backports.ssl_match_hostname',
		'functools32'
	],
	':python_version<"3.3"' : [
		'ipaddress'
	]
}

setup_requires = [
	'pytest-runner'
]

tests_require = [
	'pytest',
	'netprofile_core'
]

setup(
	name='netprofile',
	version=versioneer.get_version(),
	cmdclass=commands,
	description='NetProfile Administrative UI',
	license='GNU Affero General Public License v3 or later (AGPLv3+)',
	long_description=README_LOCAL + '\n\n' +  README_GLOBAL,
	classifiers=[
		'Programming Language :: Python',
		'Programming Language :: Python :: 2',
		'Programming Language :: Python :: 2.7',
		'Programming Language :: Python :: 3',
		'Programming Language :: Python :: 3.2',
		'Programming Language :: Python :: 3.4',
		'Programming Language :: Python :: Implementation :: CPython',
		'Framework :: Pyramid',
		'Topic :: Internet :: WWW/HTTP',
		'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
		'Topic :: Office/Business :: Groupware',
		'Topic :: Office/Business :: Scheduling',
		'Development Status :: 3 - Alpha',
		'Intended Audience :: Customer Service',
		'Intended Audience :: Information Technology',
		'Intended Audience :: System Administrators',
		'Intended Audience :: Telecommunications Industry',
		'License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)',
		'Operating System :: OS Independent'
	],
	author='Alex Unigovsky',
	author_email='unik@compot.ru',
	url='https://github.com/unikmhz/npui',
	keywords='web wsgi pyramid np netprofile crm billing accounting network isp',
	packages=find_packages(exclude=['tests', 'htmlcov']),
	include_package_data=True,
	zip_safe=False,
	test_suite='tests',
	tests_require=tests_require,
	setup_requires=setup_requires,
	install_requires=requires,
	extras_require=extras_require,
	entry_points={
		'paste.app_factory' : [
			'main = netprofile:main'
		],
		'console_scripts' : [
			'npctl = netprofile.scripts.ctl:main',
			'np_rtd = netprofile.scripts.rtd:main'
		],
		'netprofile.cli.commands' : [
			'module list = netprofile.cli:ListModules',
			'module ls = netprofile.cli:ListModules',

			'module show = netprofile.cli:ShowModule',
			'module info = netprofile.cli:ShowModule',

			'module install = netprofile.cli:InstallModule',
			'module upgrade = netprofile.cli:UpgradeModule',
			'module uninstall = netprofile.cli:UninstallModule',
			'module enable = netprofile.cli:EnableModule',
			'module disable = netprofile.cli:DisableModule',

			'alembic = netprofile.cli:Alembic',
			'db revision = netprofile.cli:DBRevision',

			'deploy = netprofile.cli:Deploy',

			'rt = netprofile.cli:RTServer'
		],
		'netprofile.export.formats' : [
			'csv = netprofile.export.csv:CSVExportFormat',
			'pdf = netprofile.export.pdf:PDFExportFormat'
		]
	}
)

