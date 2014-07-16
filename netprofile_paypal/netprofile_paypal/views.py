#!/usr/bin/env python
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-
#
# NetProfile: Paypal module - Views
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

import math
import datetime as dt
from dateutil.parser import parse as dparse
from dateutil.relativedelta import relativedelta

from pyramid.view import view_config
from pyramid.settings import asbool
from pyramid.httpexceptions import (
	HTTPForbidden,
	HTTPSeeOther
)
from sqlalchemy import func
from sqlalchemy.orm.exc import NoResultFound
from netprofile import locale_neg

from netprofile.common.factory import RootFactory
from netprofile.common.hooks import register_hook
from netprofile.db.connection import DBSession
from netprofile_xop.models import (
	ExternalOperation,
	ExternalOperationProvider,
	ExternalOperationState
)
from netprofile_stashes.models import Stash
import paypalrestsdk

_ = TranslationStringFactory('netprofile_paypal')

class ClientRootFactory(RootFactory):
	def __getitem__(self, name):
		raise KeyError('Invalid URL')

@view_config(
	route_name='paypal.cl.accounts',
	name='',
	context=ClientRootFactory,
	permission='USAGE',
	renderer='netprofile_paypal:templates/client_paypal.mak'
)
def client_list(ctx, request):
	loc = get_localizer(request)
	tpldef = {
	}
	request.run_hook('access.cl.tpldef', tpldef, request)
	request.run_hook('access.cl.tpldef.accounts.list', tpldef, request)
	return tpldef

@view_config(route_name='paypal.cl.docc', renderer='netprofile_paypal:templates/client_cc.mak')
def cc_payment(request):
	loc = get_localizer(request)
	cur_locale = locale_neg(request)
	cfg = request.registry.settings
	must_recaptcha = asbool(cfg.get('netprofile.client.registration.recaptcha.enabled', False))

	csrf = request.POST.get('csrf', '')
	diff = request.POST.get('diff', '')
	stashid = request.POST.get('stashid', '')

	errors = {}

	if must_recaptcha:
		rc_private = cfg.get('netprofile.client.recaptcha.private_key')
		rc_public = cfg.get('netprofile.client.recaptcha.public_key')
		if (not rc_private) or (not rc_public):
			# TODO: log missing reCAPTCHA keys
			must_recaptcha = False
	
	if 'submit' in request.POST:
		sess = DBSession()
		if csrf != request.get_csrf():
			request.session.flash({
				'text' : loc.translate(_('Error submitting form')),
				'class' : 'danger'
			})
			return HTTPSeeOther(location=request.route_url('stashes.cl.accounts', traverse=()))
		xop = ExternalOperation()
		xop.stash_id = stashid
		xop.entity = request.user.parent
		#TODO: Add ID to config
		xop.provider_id = 3
		xop.difference = diff
		sess.add(xop)
		sess.flush()

		tpldef = {
			'cur_loc'        : cur_locale,
			'must_recaptcha' : must_recaptcha,
			'diff'			 : diff,
			'xopid'			 : xop.id,
			'errors'         : {err: loc.translate(errors[err]) for err in errors}
		}

		if must_recaptcha:
			tpldef['rc_public'] = rc_public
		request.run_hook('paypal.cl.tpldef.docc', tpldef, request)
		request.run_hook('access.cl.tpldef', tpldef, request)
		return tpldef

	if 'pay' in request.POST:
		sess = DBSession()
		if csrf != request.get_csrf():
			errors['csrf'] = _('Error submitting form')
		elif must_recaptcha:
			try:
				rcresp = verify_recaptcha(rc_private, request)
			except ValueError as e:
				errors['recaptcha'] = str(e)
			else:
				if rcresp and not rcresp.valid:
					errors['recaptcha'] = rcresp.text()
		if len(errors) == 0:
			type = request.POST.get('type', '')
			number1 = request.POST.get('number1', '')
			number2 = request.POST.get('number2', '')
			number3 = request.POST.get('number3', '')
			number4 = request.POST.get('number4', '')
			expire_month = request.POST.get('month', '')
			expire_year = request.POST.get('year', '')
			cvv2 = request.POST.get('cvv2', '')
			name_family = request.POST.get('name_family', '')
			name_given = request.POST.get('name_given', '')

			l = len(type)
			if (type != 'visa') and (type != 'mastercard') and (type != 'discover') and (type != 'amex'):
				errors['type'] = _('Select card type')

			number = number1 + number2 + number3 + number4
			l = len(number)
			print(number)
			if l != 16:
				errors['number'] = _('Invalid card number')
			l = len(cvv2)
			if (l < 3) or (l > 4):
				errors['cvv2'] = _('Invalid cvv2 number')
			l = len(name_family)
			if (l == 0) or (l > 254):
				errors['name_family'] = _('Invalid field length')
			l = len(name_given)
			if (l == 0) or (l > 254):
				errors['name_given'] = _('Invalid field length')
			l = int(expire_month)
			if (l < 1) or (l > 12):
				errors['date'] = _('Please select month')
			l = len(expire_year)
			if (l != 4):
				errors['date'] = _('Please select year')

		if len(errors) == 0:
			sess = DBSession()
			paypalmethod = 'classic'
			
			xopid = int(request.POST.get('xopid', ''))
			xop = sess.query(ExternalOperation).get(xopid)
			xop.istate = ExternalOperationState.pending

			if paypalmethod == 'classic':
				headers = {
						'X-PAYPAL-SECURITY-USERID': 'info_api1.itws.ru',
						'X-PAYPAL-SECURITY-PASSWORD': 'SEZFFE9TGHFQKUW2',
						'X-PAYPAL-SECURITY-SIGNATURE': 'AtRDzwgG4KvAkijtzeXQEyeXXrEzAJCl08WDb2RUBgvAKDGwn7U-PFvA',
						'X-PAYPAL-APPLICATION-ID': 'APP-80W284485P519543T',
						'X-PAYPAL-SERVICE-VERSION':'1.1.0',
						'X-PAYPAL-REQUEST-DATA-FORMAT':'NV',
						'X-PAYPAL-RESPONSE-DATA-FORMAT':'NV'
				}
				params = collections.OrderedDict()
				params['requestEnvelope.errorLanguage'] = 'en_US';
				params['requestEnvelope.detailLevel'] = 'ReturnAll';

			else:
				paypalrestsdk.configure({
					"mode": "sandbox", # sandbox or live
					"client_id": "",
					"client_secret": "" 
				})

				payment = paypalrestsdk.Payment({
					"intent": "sale",
					"payer": {
						"payment_method": "credit_card",
						"funding_instruments": [{
							"credit_card": {
								"type": type,
								"number": number,
								"expire_month": expire_month,
								"expire_year": expire_year,
								"cvv2": cvv2,
								"first_name": name_given,
								"last_name": name_family 
							}
						}]
					},
					"transactions": [{
						"item_list": {
							"items": [{
							"name": str(xop.provider.siotype),
							"price": str(round(xop.difference,2)),
							"currency": "RUB",
							"quantity": 1 
						}]
						},
						"amount": {
							"total": str(round(xop.difference,2)),
						    "currency": "RUB" 
						},
						"description": xop.id 
					}]
				})

			if payment.create():
				xop.external_id = payment.id
				xop.state = ExternalOperationState.cleared
				request.session.flash({
					'text' : loc.translate(_('Paymend successfuly recieved'))
				})
				return HTTPSeeOther(location=request.route_url('stashes.cl.accounts', traverse=()))
			else:
				xop.state = ExternalOperationState.canceled
				request.session.flash({
					'text' : payment.error,
					'class' : 'danger'
				})
				return HTTPSeeOther(location=request.route_url('stashes.cl.accounts', traverse=()))


	if 'cancel' in request.POST:
		sess = DBSession()
		if csrf != request.get_csrf():
			errors['csrf'] = _('Error submitting form')

		xopid = int(request.POST.get('xopid', ''))
		xop = sess.query(ExternalOperation).get(xopid)
		xop.state = ExternalOperationState.canceled
		request.session.flash({
			'text' : loc.translate(_('Paymend successfuly canceled'))
		})
		return HTTPSeeOther(location=request.route_url('stashes.cl.accounts', traverse=()))


	request.session.flash({
		'text' : loc.translate(_('Error submitting form')),
		'class' : 'danger'
	})


	return HTTPSeeOther(location=request.route_url('stashes.cl.accounts', traverse=()))


