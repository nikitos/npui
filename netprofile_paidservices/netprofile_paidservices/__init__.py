#!/usr/bin/env python
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-
#
# NetProfile: Paid Services module
# © Copyright 2014-2017 Alex 'Unik' Unigovsky
#
# This file is part of NetProfile.
# NetProfile is free software: you can redistribute it and/or
# modify it under the terms of the GNU Affero General Public
# License as published by the Free Software Foundation, either
# version 3 of the License, or (at your option) any later
# version.
#
# NetProfile is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General
# Public License along with NetProfile. If not, see
# <http://www.gnu.org/licenses/>.

from __future__ import (
	unicode_literals,
	print_function,
	absolute_import,
	division
)

from netprofile.common.modules import ModuleBase

from sqlalchemy.orm.exc import NoResultFound
from pyramid.i18n import TranslationStringFactory

from ._version import get_versions
__version__ = get_versions()['version']
del get_versions

_ = TranslationStringFactory('netprofile_paidservices')

class Module(ModuleBase):
	def __init__(self, mmgr):
		self.mmgr = mmgr
		mmgr.cfg.add_translation_dirs('netprofile_paidservices:locale/')

	@classmethod
	def get_deps(cls):
		return ('access',)

	@classmethod
	def get_models(cls):
		from netprofile_paidservices import models
		return (
			models.PaidService,
			models.PaidServiceType
		)

	@classmethod
	def get_sql_functions(cls):
		from netprofile_paidservices import models
		return (
			models.PSCallbackProcedure,
			models.PSExecuteProcedure,
			models.PSPollProcedure,
			models.AcctPCheckProcedure
		)

	@classmethod
	def get_sql_events(cls):
		from netprofile_paidservices import models
		return (
			models.PSPollEvent,
		)

	@classmethod
	def get_sql_data(cls, modobj, vpair, sess):
		from netprofile_core.models import (
			Group,
			GroupCapability,
			LogType,
			Privilege
		)

		if not vpair.is_install:
			return

		sess.add(LogType(
			id=14,
			name='Paid Services'
		))

		privs = (
			Privilege(
				code='BASE_PAIDSERVICES',
				name=_('Menu: Paid services')
			),
			Privilege(
				code='PAIDSERVICES_LIST',
				name=_('Paid Services: List')
			),
			Privilege(
				code='PAIDSERVICES_CREATE',
				name=_('Paid Services: Create')
			),
			Privilege(
				code='PAIDSERVICES_EDIT',
				name=_('Paid Services: Edit')
			),
			Privilege(
				code='PAIDSERVICES_DELETE',
				name=_('Paid Services: Delete')
			),
			Privilege(
				code='PAIDSERVICETYPES_CREATE',
				name=_('Paid Services: Create types')
			),
			Privilege(
				code='PAIDSERVICETYPES_EDIT',
				name=_('Paid Services: Edit types')
			),
			Privilege(
				code='PAIDSERVICETYPES_DELETE',
				name=_('Paid Services: Delete types')
			)
		)
		for priv in privs:
			priv.module = modobj
			sess.add(priv)
		try:
			grp_admins = sess.query(Group).filter(Group.name == 'Administrators').one()
			for priv in privs:
				cap = GroupCapability()
				cap.group = grp_admins
				cap.privilege = priv
		except NoResultFound:
			pass

	def get_css(self, request):
		return (
			'netprofile_paidservices:static/css/main.css',
		)

	@property
	def name(self):
		return _('Paid Services')

