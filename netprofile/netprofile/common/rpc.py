#!/usr/bin/env python
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-
#
# NetProfile: RPC API
# © Copyright 2014 Alex 'Unik' Unigovsky
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

import datetime as dt
import decimal
import translationstring
from dateutil.tz import tzlocal

from pyramid.settings import asbool
from pyramid.security import has_permission
from pyramid_rpc.xmlrpc import (
	XmlRpcError,
	xmlrpclib
)
from pyramid_rpc.jsonrpc import JsonRpcError
from pyramid.renderers import JSON

from netprofile import PY3
from netprofile.common.hooks import register_hook
from netprofile.common.factory import RootFactory
from netprofile.common import ipaddr

if PY3:
	from netprofile.db.enum3 import EnumSymbol
else:
	from netprofile.db.enum2 import EnumSymbol

_do_xmlrpc = False
_do_jsonrpc = False

class XmlRpcForbiddenError(XmlRpcError):
	faultCode = -31403
	faultString = 'client error; permission denied'

class JsonRpcForbiddenError(JsonRpcError):
	code = -31403
	message = 'permission denied'

xml_disp = xmlrpclib.Marshaller.dispatch

# XXX: crude/awful workaround
def _dump_nil(self, value, write):
	write('<value><nil/></value>')
xml_disp[type(None)] = _dump_nil

xml_disp[translationstring.TranslationString] = xml_disp[str]

def _dump_enum(self, value, write):
	write('<value><string>')
	write(xmlrpclib.escape(value.value))
	write('</string></value>\n')
xml_disp[EnumSymbol] = _dump_enum

def _gen_funcs(model, proto):
	mod = model
	name = mod.name
	fault = XmlRpcForbiddenError
	if proto == 'jsonrpc':
		fault = JsonRpcForbiddenError

	def _rpc_create(req, recs):
		cap = mod.cap_create
		if cap:
			rf = RootFactory(req)
			if not has_permission(cap, rf, req):
				raise fault
		return mod.create({ 'records' : recs }, req)

	def _rpc_read(req, params):
		cap = mod.cap_read
		if cap:
			rf = RootFactory(req)
			if not has_permission(cap, rf, req):
				raise fault
		return mod.read(params, req)

	def _rpc_update(req, recs):
		cap = mod.cap_edit
		if cap:
			rf = RootFactory(req)
			if not has_permission(cap, rf, req):
				raise fault
		return mod.update({ 'records' : recs }, req)

	def _rpc_delete(req, recs):
		cap = mod.cap_delete
		if cap:
			rf = RootFactory(req)
			if not has_permission(cap, rf, req):
				raise fault
		return mod.delete({ 'records' : recs }, req)

	return (
		_rpc_create,
		_rpc_read,
		_rpc_update,
		_rpc_delete
	)

@register_hook('np.model.load')
def _proc_model(mmgr, model):
	if (not _do_xmlrpc) and (not _do_jsonrpc):
		return
	name = model.name

	# TODO: swap USAGE for RPC-specific privilege (maybe?)
	if _do_xmlrpc:
		funcs = _gen_funcs(model, 'xmlrpc')
		mmgr.cfg.add_xmlrpc_method(funcs[0], endpoint='api.xmlrpc', permission='USAGE', method=('create' + name))
		mmgr.cfg.add_xmlrpc_method(funcs[1], endpoint='api.xmlrpc', permission='USAGE', method=('read' + name))
		mmgr.cfg.add_xmlrpc_method(funcs[2], endpoint='api.xmlrpc', permission='USAGE', method=('update' + name))
		mmgr.cfg.add_xmlrpc_method(funcs[3], endpoint='api.xmlrpc', permission='USAGE', method=('delete' + name))

	if _do_jsonrpc:
		funcs = _gen_funcs(model, 'jsonrpc')
		mmgr.cfg.add_jsonrpc_method(funcs[0], endpoint='api.jsonrpc', permission='USAGE', method=('create' + name))
		mmgr.cfg.add_jsonrpc_method(funcs[1], endpoint='api.jsonrpc', permission='USAGE', method=('read' + name))
		mmgr.cfg.add_jsonrpc_method(funcs[2], endpoint='api.jsonrpc', permission='USAGE', method=('update' + name))
		mmgr.cfg.add_jsonrpc_method(funcs[3], endpoint='api.jsonrpc', permission='USAGE', method=('delete' + name))

def includeme(config):
	"""
	RPC loader for Pyramid
	"""
	global _do_xmlrpc, _do_jsonrpc
	cfg = config.registry.settings
	_do_xmlrpc = asbool(cfg.get('netprofile.rpc.xmlrpc', True))
	_do_jsonrpc = asbool(cfg.get('netprofile.rpc.jsonrpc', True))

	if _do_xmlrpc:
		config.include('pyramid_rpc.xmlrpc')
		config.add_xmlrpc_endpoint('api.xmlrpc', '/api/xmlrpc')
	if _do_jsonrpc:
		config.include('pyramid_rpc.jsonrpc')
		renderer = JSON()

		def _json_datetime(obj, req):
			if obj.tzinfo is None:
				obj = obj.replace(tzinfo=tzlocal())
			return obj.isoformat()

		renderer.add_adapter(dt.datetime, _json_datetime)
		renderer.add_adapter(dt.date, lambda obj, req: obj.isoformat())
		renderer.add_adapter(dt.time, lambda obj, req: obj.isoformat())
		renderer.add_adapter(ipaddr.IPv4Address, lambda obj, req: int(obj))
		renderer.add_adapter(decimal.Decimal, lambda obj, req: str(obj))
		config.add_renderer('jsonrpc', renderer)
		config.add_jsonrpc_endpoint('api.jsonrpc', '/api/jsonrpc', default_renderer='jsonrpc')

	config.scan()

