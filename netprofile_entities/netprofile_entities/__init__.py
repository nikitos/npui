#!/usr/bin/env python
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-
#
# NetProfile: Entities module
# © Copyright 2013-2017 Alex 'Unik' Unigovsky
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

_ = TranslationStringFactory('netprofile_entities')

class Module(ModuleBase):
	def __init__(self, mmgr):
		self.mmgr = mmgr
		mmgr.cfg.add_translation_dirs('netprofile_entities:locale/')
		mmgr.cfg.scan()

	@classmethod
	def get_deps(cls):
		return ('geo',)

	@classmethod
	def get_models(cls):
		from netprofile_entities import models
		return (
			models.Address,
			models.Phone,
			models.EntityType,
			models.Entity,
			models.EntityComment,
			models.EntityFile,
			models.EntityFlag,
			models.EntityFlagType,
			models.EntityState,
			models.EntityCommunicationChannel,
			models.PhysicalEntity,
			models.LegalEntity,
			models.StructuralEntity,
			models.ExternalEntity
		)

	@classmethod
	def get_sql_views(cls):
		from netprofile_entities import models
		return (
			models.EntitiesBaseView,
		)

	@classmethod
	def get_sql_data(cls, modobj, vpair, sess):
		from netprofile_entities import models
		from netprofile_core.models import (
			Group,
			GroupCapability,
			LogType,
			Privilege
		)

		if not vpair.is_install:
			return

		sess.add(LogType(
			id=2,
			name='Entities'
		))
		sess.flush()

		privs = (
			Privilege(
				code='BASE_ENTITIES',
				name=_('Menu: Entities')
			),
			Privilege(
				code='ENTITIES_LIST',
				name=_('Entities: List')
			),
			Privilege(
				code='ENTITIES_CREATE',
				name=_('Entities: Create')
			),
			Privilege(
				code='ENTITIES_EDIT',
				name=_('Entities: Edit')
			),
			Privilege(
				code='ENTITIES_DELETE',
				name=_('Entities: Delete')
			),
			Privilege(
				code='FILES_ATTACH_2ENTITIES',
				name=_('Files: Attach to entities')
			),
			Privilege(
				code='ENTITIES_STATES_CREATE',
				name=_('Entities: Create states')
			),
			Privilege(
				code='ENTITIES_STATES_EDIT',
				name=_('Entities: Edit states')
			),
			Privilege(
				code='ENTITIES_STATES_DELETE',
				name=_('Entities: Delete states')
			),
			Privilege(
				code='ENTITIES_FLAGTYPES_CREATE',
				name=_('Entities: Create flag types')
			),
			Privilege(
				code='ENTITIES_FLAGTYPES_EDIT',
				name=_('Entities: Edit flag types')
			),
			Privilege(
				code='ENTITIES_FLAGTYPES_DELETE',
				name=_('Entities: Delete flag types')
			),
			Privilege(
				code='ENTITIES_COMMENT',
				name=_('Entities: Add comments')
			),
			Privilege(
				code='ENTITIES_COMMENTS_EDIT',
				name=_('Entities: Edit comments')
			),
			Privilege(
				code='ENTITIES_COMMENTS_DELETE',
				name=_('Entities: Delete comments')
			),
			Privilege(
				code='ENTITIES_COMMENTS_MARK',
				name=_('Entities: Mark comments as obsolete')
			),
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

		types = (
			models.EntityType(
				id=1,
				name=_('Individual'),
				model='PhysicalEntity',
				long_name=_('Individual'),
				plural=_('Individuals'),
				description=_('Definition of a single person.')
			),
			models.EntityType(
				id=2,
				name=_('Legal'),
				model='LegalEntity',
				long_name=_('Legal Entity'),
				plural=_('Legal Entities'),
				description=_('Definition of a legal entity (a company, corporation etc.).')
			),
			models.EntityType(
				id=3,
				name=_('Structure'),
				model='StructuralEntity',
				long_name=('Structure'),
				plural=_('Structures'),
				description=_('Definition of a building or a comparable structure.')
			),
			models.EntityType(
				id=4,
				name=_('Misc.'),
				model='ExternalEntity',
				long_name=('Miscellaneous'),
				plural=_('Miscellaneous'),
				description=_('Definition of an object without well-defined metadata.')
			)
		)
		for et in types:
			et.module = modobj
			sess.add(et)

		sess.add(models.EntityState(
			name='Default',
			description='Default entity state. You can safely rename and/or delete it if you wish.'
		))

	def get_local_js(self, request, lang):
		return (
			'netprofile_entities:static/webshell/locale/webshell-lang-' + lang + '.js',
		)

	def get_autoload_js(self, request):
		return (
			'NetProfile.entities.grid.HistoryGrid',
		)

	def get_css(self, request):
		return (
			'netprofile_entities:static/css/main.css',
		)

	@property
	def name(self):
		return _('Entities')

