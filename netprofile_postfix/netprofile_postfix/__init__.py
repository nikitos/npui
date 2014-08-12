#!/usr/bin/env python
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-
#
# NetProfile: Postfix module
# © Copyright 2013 Alex 'Unik' Unigovsky
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


from pyramid.i18n import TranslationStringFactory

_ = TranslationStringFactory('netprofile_postfix')

class Module(ModuleBase):
	def __init__(self, mmgr):
		self.mmgr = mmgr
		mmgr.cfg.add_route(
			'postfix.cl.mail',
			'/mail',
			vhost='client'
		)

		mmgr.cfg.add_route(
			'postfix.cl.delete',
			'/mail/delete',
			vhost='client'
		)

		mmgr.cfg.add_route(
			'postfix.cl.create',
			'/mail/create',
			vhost='client'
		)

		mmgr.cfg.add_route(
			'postfix.cl.edit',
			'/mail/edit',
			vhost='client'
		)

		mmgr.cfg.add_translation_dirs('netprofile_postfix:locale/')
		mmgr.cfg.scan()
		

	@classmethod
	def get_deps(cls):
		return ('domains',)

	@classmethod
	def get_models(self):
		from netprofile_postfix import models
		return (
			models.PostfixAdmin,
			models.PostfixDomain,
			models.PostfixDomainAdmins,
			models.PostfixLog,
			models.PostfixVacation,
			models.PostfixAlias,
			models.PostfixMailbox,
		)

	def get_css(self, request):
		return (
			'netprofile_postfix:static/css/main.css',
		)

	@property
	def name(self):
		return _('Postfix Admin Tool')

