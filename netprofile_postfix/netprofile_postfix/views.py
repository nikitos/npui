#!/usr/bin/env python
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-
#
# NetProfile: Postfix module - Views
# © Copyright 2013-2014 Alex 'Unik' Unigovsky
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

from pyramid.i18n import (
	TranslationStringFactory,
	get_localizer
)

import requests 
from pyramid.view import view_config
from pyramid.httpexceptions import (
	HTTPForbidden,
	HTTPSeeOther
)
from sqlalchemy import func
from sqlalchemy.orm.exc import NoResultFound

from netprofile.common.factory import RootFactory
from netprofile.common.hooks import register_hook
from netprofile.db.connection import DBSession

from netprofile_access.models import AccessEntity
from netprofile_access.models import AccessEntity
from netprofile_powerdns.models import PDNSDomain
from .models import PostfixAdmin, PostfixDomain, PostfixDomainAdmins, PostfixLog, PostfixVacation, PostfixAlias, PostfixMailbox

_ = TranslationStringFactory('netprofile_postfix')


@view_config(
	route_name='postfix.cl.create',
	request_method='POST',
	permission='USAGE',
)
def createMailBox(request):
	loc = get_localizer(request)
	cfg = request.registry.settings
	sess = DBSession()
	errmess = None
	csrf = request.POST.get('csrf', '')
	access_user = sess.query(AccessEntity).filter_by(nick=str(request.user)).first()
	admindomains = sess.query(PostfixDomainAdmins).filter_by(username=str(request.user))

	if csrf != request.get_csrf():
		request.session.flash({
				'text' : loc.translate(_('Error submitting form')),
				'class' : 'danger'
				})
		return HTTPSeeOther(location=request.route_url('postfix.cl.mail'))
	else:
		domain_name = request.POST.get('mbDomain', None)
		domain_descr = request.POST.get('mbDomainDescription', None)
		username = request.POST.get('mbUsername', None)
		mailbox_name = request.POST.get('mbName', None)
		mailbox_password = request.POST.get('mbPassword', None)
		if domain_name and username:
			if username == access_user.nick:
				if mailbox_name and mailbox_password:
					newmailbox = PostfixMailbox(
						username=username, 
						password=mailbox_password, 
						name=mailbox_name, 
						domain=domain_name
						)
					sess.add(newmailbox)
					sess.flush()
				else:
					if domain_name not in [ad.username for ad in admindomains]:
						newdomainadmin = PostfixDomainAdmins(username=username, domain=domain_name) 
						newdomain = PostfixDomain(domain=domain_name, description=domain_descr)
						sess.add(newdomainadmin)
						sess.add(newdomain)
						sess.flush()

	return HTTPSeeOther(location=request.route_url('postfix.cl.mail'))

@view_config(
	route_name='postfix.cl.edit',
	request_method='POST',
	permission='USAGE',
)
def editMailBox(request):
	loc = get_localizer(request)
	cfg = request.registry.settings
	sess = DBSession()
	errmess = None
	csrf = request.POST.get('csrf', '')
	access_user = sess.query(AccessEntity).filter_by(nick=str(request.user)).first()
	
	if csrf != request.get_csrf():
		request.session.flash({
				'text' : loc.translate(_('Error submitting form')),
				'class' : 'danger'
				})
		return HTTPSeeOther(location=request.route_url('postfix.cl.mail'))
	else:
		#get vars
		domain_name = request.POST.get('mbDomain', None)
		domain_descr = request.POST.get('mbDomainDescription', None)
		username = request.POST.get('mbUsername', None)
		mailbox_name = request.POST.get('mbName', None)
		mailbox_id = request.POST.get('id', None)
		domain_id = request.POST.get('did', None)
		mailbox_password = request.POST.get('mbPassword', None)
		if username:
			if username == access_user.nick:
				if mailbox_name and mailbox_password:
					mailbox = sess.query(PostfixMailbox).filter_by(id=int(mailbox_id)).first()
					mailbox.name = mailbox_name
					mailbox.password = mailbox_password
					mailbox.domain = domain_name

				else:
					domain = sess.query(PostfixDomain).filter_by(id=domain_id).first()
					domain.description = domain_descr

				sess.flush()

	return HTTPSeeOther(location=request.route_url('postfix.cl.mail'))

@view_config(
	route_name='postfix.cl.delete',
	request_method='POST',
	permission='USAGE',
)
def deleteMailBox(request):
	loc = get_localizer(request)
	cfg = request.registry.settings
	sess = DBSession()
	errmess = None
	csrf = request.POST.get('csrf', '')
	access_user = sess.query(AccessEntity).filter_by(nick=str(request.user)).first()
	if csrf != request.get_csrf():
		request.session.flash({
				'text' : loc.translate(_('Error submitting form')),
				'class' : 'danger'
				})
		return HTTPSeeOther(location=request.route_url('postfix.cl.mail'), _query=(('error', 'asc'),))
	else:
		domainid = request.POST.get('domainid', None)
		mboxid = request.POST.get('mboxid', None)
		if mboxid:
			mbox = sess.query(PostfixMailbox).filter_by(id=int(mboxid)).first()
			if mbox.username == access_user.nick:
				sess.delete(mbox)
				sess.flush()
		elif domainid:
			domain = sess.query(PostfixDomain).filter_by(id=int(domainid)).first()
			domainadmins = sess.query(PostfixDomainAdmins).filter_by(domain=domain.domain)
			if access_user.nick in [adm.username for adm in domainadmins]:
				sess.delete(domain)
				sess.query(PostfixDomainAdmins).filter_by(domain=domain.domain).delete()
				sess.flush()

	return HTTPSeeOther(location=request.route_url('postfix.cl.mail'))


@view_config(
	route_name='postfix.cl.mail',
	permission='USAGE',
	renderer='netprofile_postfix:templates/client_mail.mak'
)
def postfix_mailboxes(request):
	loc = get_localizer(request)
	cfg = request.registry.settings
	sess = DBSession()
	errmess = None
	csrf = request.POST.get('csrf', '')

	if 'submit' in request.POST:
		if csrf != request.get_csrf():
			request.session.flash({
					'text' : loc.translate(_('Error submitting form')),
					'class' : 'danger'
					})
			return HTTPSeeOther(location=request.route_url('postfix.cl.mail'))

	access_user = sess.query(AccessEntity).filter_by(nick=str(request.user)).first()
	userdomains = sess.query(PDNSDomain).filter_by(account=str(access_user.nick))
	admindomains = sess.query(PostfixDomainAdmins).filter_by(username=str(request.user))
	maildomains = sess.query(PostfixDomain).filter(PostfixDomain.domain.in_([ad.domain for ad in admindomains]))
	mailboxes = sess.query(PostfixMailbox).filter(PostfixMailbox.domain.in_([md.domain for md in maildomains]))

	tpldef = {'errmessage':errmess, 
			  'accessuser':access_user,
			  'userdomains':userdomains,
			  'admindomains':admindomains,
			  'maildomains':maildomains, 
			  'mailboxes':mailboxes,
			  'aliases':None,
			  }

	request.run_hook('access.cl.tpldef', tpldef, request)

	return(tpldef)


@register_hook('access.cl.menu')
def _gen_menu(menu, req):
	loc = get_localizer(req)
	menu.append({
		'route' : 'postfix.cl.mail',
		'text'  : loc.translate(_('Mail Settings'))
	})
