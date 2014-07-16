#!/usr/bin/env python
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-
#
# NetProfile: Paypal module - Models
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

__all__ = [
]

from netprofile.db.connection import DBSession
from netprofile_xop.models import (
    ExternalOperation,
	ExternalOperationProvider,
	ExternalOperationState
)
from netprofile_entities.models import PhysicalEntity
import urllib
from pyramid.response import Response
#from pyramid.request import Request
#from urllib2 import urlopen, Request


class PayPalIPN:
	
	def __init__(self, provider):
		self.provider = provider
	
	def process_request(self, request, sess):
#		sess = DBSession()

		payment_type = request.POST.get('payment_type', '')
		payment_date = request.POST.get('payment_date', '')
		payment_status = request.POST.get('payment_status', '')

		address_status = request.POST.get('address_status', '')
		payer_status = request.POST.get('payer_status', '')
		first_name = request.POST.get('first_name', '')
		last_name = request.POST.get('last_name', '')
		payer_email = request.POST.get('payer_email', '')
		payer_id = request.POST.get('payer_id', '')

		address_name = request.POST.get('address_name', '')
		address_country = request.POST.get('address_country', '')
		address_country_code = request.POST.get('address_country_code', '')
		address_zip = request.POST.get('address_zip', '')
		address_state = request.POST.get('address_state', '')
		address_city = request.POST.get('address_city', '')
		address_street = request.POST.get('address_street', '')

		business = request.POST.get('business', '')
		receiver_email = request.POST.get('receiver_email', '')
		receiver_id = request.POST.get('receiver_id', '')
		residence_country = request.POST.get('residence_country', '')

		item_name = request.POST.get('item_name', '')
		item_number = request.POST.get('item_number', '')
		quantity = request.POST.get('quantity', '')
		shipping = request.POST.get('shipping','')
		tax = request.POST.get('tax', '')

		mc_currency = request.POST.get('mc_currency', '')
		mc_fee = request.POST.get('mc_fee', '')
		mc_gross = request.POST.get('mc_gross', '')
		mc_handling = request.POST.get('mc_handling', '')
		mc_shipping = request.POST.get('mc_shipping', '')

		txn_type = request.POST.get('txn_type', '')
		txn_id = request.POST.get('txn_id', None)
		notify_version = request.POST.get('notify_version', '')

		custom = request.POST.get('custom', '')
		invoice = request.POST.get('invoice', '')
		
		#TODO: add some vars checks
		if custom is None:
			xop = ExternalOperation()
			
			xop.external_id = txn_id
			xop.external_account = payer_id
			xop.provider = self.provider
	
			entities = sess.query(PhysicalEntity).filter(PhysicalEntity.email == payer_email)
	
			xop.entity = entities[0]
			xop.stash = xop.entity.stashes[0]
			xop.difference = mc_gross

			post = request.POST
			post['cmd'] = '_notify-validate'
			params = urllib.urlencode(post)
			req = Request("""https://www.sandbox.paypal.com/cgi-bin/webscr""", params)
			req.add_header("Content-type", "application/x-www-form-urlencoded")
			response = urllib.urlopen(req)
			status = response.read()

			if not status == "VERIFIED":
				xop.state = ExternalOperationState.canceled
				return (xop)
			
			xop.state = ExternalOperationState.confirmed

		elif txn_id:
			xop = sess.query(ExternalOperation).filter(ExternalOperation.external_id == txn_id).one()
			xop.state = ExternalOperationState.confirmed

		xop.state = ExternalOperationState.cleared
		return [xop]

	def generate_response(self, request, xoplist):
		resp = Response(status='200 OK', content_type='text/plain', charset='UTF-8')
		return resp
