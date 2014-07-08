#!/usr/bin/env python
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-
#
# NetProfile: PowerDNS integration module - Views
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

from .models import UserDomain, PDNSDomain, PDNSRecord

_ = TranslationStringFactory('netprofile_powerdns')

@view_config(
	route_name='pdns.cl.delete',
	request_method='POST',
	permission='USAGE',
	#renderer='netprofile_powerdns:templates/client_pdns.mak'
)
def delete_record(request):
	#if d in GET, delete domain
	#if r in GET, delete record
	#before delete check if this record exists and belongs to auth_user
	#delete and redirect to main module page 
	#use _query to add aditional params when redirecting 
	loc = get_localizer(request)
	cfg = request.registry.settings
	sess = DBSession()
	csrf = request.POST.get('csrf', '')
	access_user = sess.query(AccessEntity).filter_by(nick=str(request.user)).first()
	user_domains = [d.id for d in sess.query(PDNSDomain).filter_by(account=str(request.user))]
	
	if csrf != request.get_csrf():
		request.session.flash({
				'text' : loc.translate(_('Error submitting form')),
				'class' : 'danger'
				})
		return HTTPSeeOther(location=request.route_url('pdns.cl.domains'), _query=(('error', 'asc'),))
	else:
		domainid = request.POST.get('domainid', None)
		recid = request.POST.get('recordid', None)
		if domainid and not recid:
			domain = sess.query(PDNSDomain).filter_by(id=int(request.POST.get('domainid', None))).first()
			if domain.id in user_domains:
				sess.delete(domain)
				sess.flush()

		elif recid:
			record = sess.query(PDNSRecord).filter_by(id=int(request.POST.get('recordid', None))).first()
			if record.domain_id in user_domains:
				sess.delete(record)			
				sess.flush()
	
		return HTTPSeeOther(location=request.route_url('pdns.cl.domains'))

@view_config(
	route_name='pdns.cl.edit',
	request_method='POST',
	permission='USAGE',
)
def edit_record(request):
	loc = get_localizer(request)
	cfg = request.registry.settings
	sess = DBSession()
	csrf = request.POST.get('csrf', '')
	access_user = sess.query(AccessEntity).filter_by(nick=str(request.user)).first()
	user_domains = [d.id for d in sess.query(PDNSDomain).filter_by(account=str(request.user))]
	
	if csrf != request.get_csrf():
		request.session.flash({
				'text' : loc.translate(_('Error submitting form')),
				'class' : 'danger'
				})
		return HTTPSeeOther(location=request.route_url('pdns.cl.domains'))
	else:
		rectype = request.POST.get('type', None)
		if rectype == "domain":
			domain = sess.query(PDNSDomain).filter_by(id=int(request.POST.get('domainid', None))).first()
			if domain.id in user_domains:
				domain.name = request.POST.get('hostName', None)
				domain.dtype = request.POST.get('hostType', None)
				domain.master = request.POST.get('hostValue', None)

		elif rectype == "record":
			record = sess.query(PDNSRecord).filter_by(id=int(request.POST.get('recordid', None))).first()
			if record.domain_id in user_domains:
				record.name = request.POST.get('name', None)
				record.content = request.POST.get('content', None)
				record.rtype = request.POST.get('type', None)
				record.ttl = int(request.POST.get('ttl', None))
				record.prio = int(request.POST.get('prio', None))
	sess.flush()
	return HTTPSeeOther(location=request.route_url('pdns.cl.domains', _query=(('sort', 'asc'),)))

@view_config(
	route_name='pdns.cl.create',
	request_method='POST',
	permission='USAGE',
	#renderer='netprofile_powerdns:templates/client_pdns.mak'
)
def create_record(request):
	loc = get_localizer(request)
	cfg = request.registry.settings
	sess = DBSession()
	csrf = request.POST.get('csrf', '')
	if csrf != request.get_csrf():
		request.session.flash({
				'text' : loc.translate(_('Error submitting form')),
				'class' : 'danger'
				})
		return HTTPSeeOther(location=request.route_url('pdns.cl.domains'))
	else:
		rectype = request.POST.get('type', None)
		if rectype == "domain":
			newdomain = PDNSDomain(name=request.POST.get('hostName', None), master=request.POST.get('hostValue', None), dtype=request.POST.get('hostType', None), account=request.POST.get('user', None))
			sess.add(newdomain)
			sess.flush()
		elif rectype == "record":
			newrecord = PDNSRecord(domain_id=int(request.POST.get('domainid', None)), name=request.POST.get('name', None), rtype=request.POST.get('type', None), content=request.POST.get('content', None), ttl=int(request.POST.get('ttl', None)), prio=int(request.POST.get('prio', None)))
			sess.add(newrecord)
			sess.flush()
		
	return HTTPSeeOther(location=request.route_url('pdns.cl.domains', _query=(('created', 1),)))


@view_config(
	route_name='pdns.cl.domains',
	permission='USAGE',
	renderer='netprofile_powerdns:templates/client_pdns.mak'
)
def list_domains(request):
	loc = get_localizer(request)
	cfg = request.registry.settings
	sess = DBSession()
	errmess = None
	csrf = request.POST.get('csrf', '')
	tpldef = {'errmessage':errmess}
	request.run_hook('access.cl.tpldef', tpldef, request)

	#if request.POST:
	#check csrf
	if 'submit' in request.POST:
		if csrf != request.get_csrf():
			request.session.flash({
					'text' : loc.translate(_('Error submitting form')),
					'class' : 'danger'
					})
			return HTTPSeeOther(location=request.route_url('pdns.cl.domains'))

	access_user = sess.query(AccessEntity).filter_by(nick=str(request.user)).first()
	user_domains = sess.query(PDNSDomain).filter_by(account=str(request.user))
	records = []
	for d in user_domains:
		recs = sess.query(PDNSRecord).filter_by(domain_id=d.id)
		for r in recs:
			records.append(r)
		
		
	tpldef.update({
			'req':request,
			'formdata':request.POST,
			'getparams':request.GET,
			'accessuser':access_user,
			'userdomains':user_domains,
			'domainrecords':records,
			'domain':None
			})
		
	return tpldef


@register_hook('access.cl.menu')
def _gen_menu(menu, req):
	loc = get_localizer(req)
	menu.append({
		'route' : 'pdns.cl.domains',
		'text'  : loc.translate(_('Domain Names'))
	}
)

