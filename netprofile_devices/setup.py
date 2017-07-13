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
	'setuptools',
	'netprofile_entities >= 0',
	'netprofile_hosts >= 0',
	'netprofile_rates >= 0',

	'snimpy >= 0.8.11'
]

setup(
	name='netprofile_devices',
	version=versioneer.get_version(),
	cmdclass=commands,
	description='NetProfile Administrative UI - Devices Module',
	license='GNU Affero General Public License v3 or later (AGPLv3+)',
	long_description=README_LOCAL + '\n\n' + README_GLOBAL,
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
	packages=find_packages(),
	include_package_data=True,
	zip_safe=False,
	test_suite='netprofile_devices',
	install_requires=requires,
	entry_points={
		'netprofile.modules' : [
			'devices = netprofile_devices:Module'
		],
		'netprofile.devices.handlers' : [
			'default = netprofile_devices.handlers:NetworkDeviceHandler'
		],
		'netprofile.devices.host_probers' : [
			'fping = netprofile_devices.probe:FPingProber',
			'fping+arp = netprofile_devices.probe:FPingARPProber'
		]
	},
	message_extractors={'.' : [
		('**.py', 'python', None),
		('**.pt', 'xml', None),
		('**.mak', 'mako', None)
	]}
)

