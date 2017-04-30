#!/usr/bin/env python
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-
#
# NetProfile: Geo module - Models
# © Copyright 2013 Nikita Andriyanov
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

__all__ = [
	'City',
	'District',
	'Street',
	'House',
	'Place',
	'HouseGroup',
	'HouseGroupMapping',
	'UserLocation',

	'AddrFormatCompactFunction',
	'AddrFormatFunction',
	'AddrGetFullFunction',
	'AddrListDistrictProcedure',
	'AddrListEntrProcedure',
	'AddrListStreetProcedure',

	'AddrCompactView',
	'AddrExtraView',
	'AddrFullView',
	'AddrStreetNamesView'
]

from collections import OrderedDict

from sqlalchemy import (
	CHAR,
	Column,
	ForeignKey,
	Index,
	Sequence,
	Unicode,
	UnicodeText,
	event,
	func,
	or_,
	text
)

from sqlalchemy.orm import (
	backref,
	contains_eager,
	relationship
)

from sqlalchemy.ext.associationproxy import association_proxy

from netprofile.db.connection import (
	Base,
	DBSession
)
from netprofile.db.fields import (
	Int16,
	NPBoolean,
	UInt8,
	UInt16,
	UInt32,
	npbool
)
from netprofile.ext.columns import MarkupColumn
from netprofile.ext.filters import CheckboxGroupFilter
from netprofile.ext.wizards import (
	SimpleWizard,
	Step,
	Wizard
)
from netprofile.db.ddl import (
	Comment,
	InArgument,
	SQLFunction,
	SQLFunctionArgument,
	View
)
from netprofile.db.util import populate_related_list

from netprofile_core.models import (
	AddressType,
	User
)
from netprofile_geo.filters import AddressFilter

from netprofile import vobject

from pyramid.threadlocal import get_current_request
from pyramid.i18n import TranslationStringFactory

_ = TranslationStringFactory('netprofile_geo')

def countries_alpha2(column, req):
	locale_cur = req.current_locale
	locale_en = req.locales['en']
	ret = dict()
	for code in locale_en.territories:
		if len(code) != 2:
			continue
		try:
			ret[code] = locale_cur.territories[code]
		except KeyError:
			ret[code] = locale_en.territories[code]

	return OrderedDict((k, v) for k, v in sorted(ret.items(), key=lambda x: x[1]))

class City(Base):
	"""
	City object.
	"""
	__tablename__ = 'addr_cities'
	__table_args__ = (
		Comment('Cities'),
		Index('addr_cities_u_name', 'name', unique=True),
		{
			'mysql_engine'  : 'InnoDB',
			'mysql_charset' : 'utf8',
			'info'          : {
				'cap_menu'      : 'BASE_GEO',
				'cap_read'      : 'GEO_LIST',
				'cap_create'    : 'GEO_CREATE',
				'cap_edit'      : 'GEO_EDIT',
				'cap_delete'    : 'GEO_DELETE',

				'show_in_menu'  : 'admin',
				'menu_name'     : _('Cities'),
				'default_sort'  : ({ 'property': 'name' ,'direction': 'ASC' },),
				'grid_view'     : ('cityid', 'name', 'prefix'),
				'grid_hidden'   : ('cityid',),
				'form_view'     : ('name', 'prefix', 'descr'),
				'easy_search'   : ('name',),
				'detail_pane'   : ('netprofile_core.views', 'dpane_simple'),

				'create_wizard' : SimpleWizard(title=_('Add new city'))
			}
		}
	)
	id = Column(
		'cityid',
		UInt32(),
		Sequence('addr_cities_cityid_seq'),
		Comment('City ID'),
		primary_key=True,
		nullable=False,
		info={
			'header_string' : _('ID')
		}
	)
	name = Column(
		Unicode(255),
		Comment('City name'),
		nullable=False,
		info={
			'header_string' : _('Name'),
			'column_flex'   : 3
		}
	)
	prefix = Column(
		Unicode(32),
		Comment('Contract prefix'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Prefix'),
			'column_flex'   : 1
		}
	)
	description = Column(
		'descr',
		UnicodeText(),
		Comment('City description'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Description')
		}
	)

	districts = relationship(
		'District',
		backref=backref('city', innerjoin=True),
		cascade='all, delete-orphan',
		passive_deletes=True
	)

	streets = relationship(
		'Street',
		cascade='all, delete-orphan',
		passive_deletes=True
	)

	def __str__(self):
		return str(self.name)

class District(Base):
	"""
	City district object.
	"""
	__tablename__ = 'addr_districts'
	__table_args__ = (
		Comment('Districts'),
		Index('addr_districts_u_name', 'name', unique=True),
		Index('addr_districts_i_cityid', 'cityid'),
		{
			'mysql_engine'  : 'InnoDB',
			'mysql_charset' : 'utf8',
			'info'          : {
				'cap_menu'      : 'BASE_GEO',
				'cap_read'      : 'GEO_LIST',
				'cap_create'    : 'GEO_CREATE',
				'cap_edit'      : 'GEO_EDIT',
				'cap_delete'    : 'GEO_DELETE',

				'show_in_menu'  : 'admin',
				'menu_name'     : _('Districts'),
				'default_sort'  : ({ 'property': 'name' ,'direction': 'ASC' },),
				'grid_view'     : ('districtid', 'city', 'name', 'prefix'),
				'grid_hidden'   : ('districtid',),
				'form_view'     : ('name', 'prefix', 'descr'),
				'easy_search'   : ('name',),
				'detail_pane'   : ('netprofile_core.views', 'dpane_simple'),

				'create_wizard' : SimpleWizard(title=_('Add new district'))
			}
		}
	)
	id = Column(
		'districtid',
		UInt32(),
		Sequence('addr_districts_districtid_seq'),
		Comment('District ID'),
		primary_key=True,
		nullable=False,
		info={
			'header_string' : _('ID')
		}
	)
	city_id = Column(
		'cityid',
		UInt32(),
		ForeignKey('addr_cities.cityid', name='addr_districts_fk_cityid', ondelete='CASCADE', onupdate='CASCADE'),
		Comment('City ID'),
		nullable=False,
		info={
			'header_string' : _('City'),
			'filter_type'   : 'nplist',
			'column_flex'   : 1
		}
	)
	name = Column(
		Unicode(255),
		Comment('District name'),
		nullable=False,
		info={
			'header_string' : _('Name'),
			'column_flex'   : 3
		}
	)
	prefix = Column(
		Unicode(32),
		Comment('Contract prefix'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Prefix'),
			'column_flex'   : 1
		}
	)
	description = Column(
		'descr',
		UnicodeText(),
		Comment('District description'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Description')
		}
	)

	streets = relationship(
		'Street',
		backref='district',
		passive_deletes=True
	)
	houses = relationship(
		'House',
		backref='district',
		passive_deletes=True
	)

	def __str__(self):
		return str(self.name)

class Street(Base):
	"""
	Street object.
	"""
	__tablename__ = 'addr_streets'
	__table_args__ = (
		Comment('Streets'),
		Index('addr_streets_u_street', 'cityid', 'name', 'prefix', 'suffix', unique=True),
		Index('addr_streets_i_districtid', 'districtid'),
		Index('addr_streets_i_name', 'name'),
		{
			'mysql_engine'  : 'InnoDB',
			'mysql_charset' : 'utf8',
			'info'          : {
				'cap_menu'      : 'BASE_GEO',
				'cap_read'      : 'GEO_LIST',
				'cap_create'    : 'GEO_CREATE',
				'cap_edit'      : 'GEO_EDIT',
				'cap_delete'    : 'GEO_DELETE',

				'show_in_menu'  : 'admin',
				'menu_name'     : _('Streets'),
				'default_sort'  : ({ 'property': 'name' ,'direction': 'ASC' },),
				'grid_view'     : ('streetid', 'city', 'district', 'name', 'prefix', 'suffix'),
				'grid_hidden'   : ('streetid',),
				'form_view'     : ('city', 'district', 'name', 'prefix', 'suffix', 'descr'),
				'easy_search'   : ('name',),
				'detail_pane'   : ('netprofile_core.views', 'dpane_simple'),

				'create_wizard' : SimpleWizard(title=_('Add new street'))
			}
		}
	)
	id = Column(
		'streetid',
		UInt32(),
		Sequence('addr_streets_streetid_seq'),
		Comment('Street ID'),
		primary_key=True,
		nullable=False,
		info={
			'header_string' : _('ID')
		}
	)
	city_id = Column(
		'cityid',
		UInt32(),
		ForeignKey('addr_cities.cityid', name='addr_streets_fk_cityid', ondelete='CASCADE', onupdate='CASCADE'),
		Comment('City ID'),
		nullable=False,
		info={
			'header_string' : _('City'),
			'filter_type'   : 'nplist',
			'column_flex'   : 1
		}
	)
	district_id = Column(
		'districtid',
		UInt32(),
		ForeignKey('addr_districts.districtid', name='addr_streets_fk_districtid', ondelete='SET NULL', onupdate='CASCADE'),
		Comment('District ID'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('District'),
			'filter_type'   : 'nplist',
			'column_flex'   : 1
		}
	)
	name = Column(
		Unicode(255),
		Comment('Street name'),
		nullable=False,
		info={
			'header_string' : _('Name'),
			'column_flex'   : 2
		}
	)
	prefix = Column(
		Unicode(8),
		Comment('Street name prefix'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Prefix')
		}
	)
	suffix = Column(
		Unicode(8),
		Comment('Street name suffix'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Suffix')
		}
	)
	description = Column(
		'descr',
		UnicodeText(),
		Comment('Street description'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Description')
		}
	)

	city = relationship(
		'City',
		innerjoin=True
	)
	houses = relationship(
		'House',
		backref=backref('street', innerjoin=True),
		cascade='all, delete-orphan',
		passive_deletes=True
	)

	def __str__(self):
		l = []
		if self.prefix:
			l.append(self.prefix)
		l.append(self.name)
		if self.suffix:
			l.append(self.suffix)
		return ' '.join(l)

class House(Base):
	"""
	House object. Used for anything with an exact address.
	"""

	@classmethod
	def _filter_hgroup(cls, query, value):
		if not isinstance(value, list):
			value = [value]
		return query.filter(House.id.in_(
			DBSession().query(HouseGroupMapping.house_id)\
				.filter(HouseGroupMapping.group_id.in_(value))
		))

	@classmethod
	def _filter_address(cls, query, value):
		if not isinstance(value, dict):
			return query
		if 'streetid' in value:
			val = int(value['streetid'])
			if val > 0:
				query = query.filter(House.street_id == val)
		elif 'districtid' in value:
			val = int(value['districtid'])
			if val > 0:
				query = query.join(House.street).filter(or_(
					Street.district_id == val,
					House.district_id == val
				))
		elif 'cityid' in value:
			val = int(value['cityid'])
			if val > 0:
				query = query.join(House.street).filter(Street.city_id == val)
		return query

	__tablename__ = 'addr_houses'
	__table_args__ = (
		Comment('Houses'),
		Index('addr_houses_u_house', 'streetid', 'number', 'num_slash', 'num_suffix', 'building', unique=True),
		Index('addr_houses_i_districtid', 'districtid'),
		{
			'mysql_engine'  : 'InnoDB',
			'mysql_charset' : 'utf8',
			'info'          : {
				'cap_menu'      : 'BASE_GEO',
				'cap_read'      : 'GEO_LIST',
				'cap_create'    : 'GEO_CREATE',
				'cap_edit'      : 'GEO_EDIT',
				'cap_delete'    : 'GEO_DELETE',

				'show_in_menu'  : 'admin',
				'menu_name'     : _('Houses'),
				'default_sort'  : (
					{ 'property' : 'streetid', 'direction' : 'ASC' },
					{ 'property' : 'number', 'direction' : 'ASC' },
					{ 'property' : 'num_slash', 'direction' : 'ASC' },
					{ 'property' : 'num_suffix', 'direction' : 'ASC' },
					{ 'property' : 'building', 'direction' : 'ASC' }
				),
				'grid_view'     : (
					'houseid',
					'street', 'number', 'num_slash', 'num_suffix', 'building',
					'entrnum', 'postindex'
				),
				'grid_hidden'   : ('houseid',),
				'form_view'     : (
					'street', 'number', 'num_slash', 'num_suffix', 'building',
					'district', 'house_groups', 'entrnum', 'postindex', 'descr'
				),
				'easy_search'   : ('number',),
				'detail_pane'   : ('netprofile_core.views', 'dpane_simple'),
				'extra_search'  : (
					CheckboxGroupFilter('hg', _filter_hgroup,
						title=_('House Group'),
						data='NetProfile.store.geo.HouseGroup',
						value_field='ahgid',
						display_field='name'
					),
					AddressFilter('address', _filter_address,
						title=_('Address'),
						show_houses=False
					)
				),

				'create_wizard' : Wizard(
					Step('street', 'number', 'num_slash', 'num_suffix', 'building', title=_('Basic house data')),
					Step('house_groups', 'entrnum', 'postindex', title=_('Additional house data')),
					title=_('Add new house')
				)
			}
		}
	)
	id = Column(
		'houseid',
		UInt32(),
		Sequence('addr_houses_houseid_seq'),
		Comment('House ID'),
		primary_key=True,
		nullable=False,
		info={
			'header_string' : _('ID')
		}
	)
	street_id = Column(
		'streetid',
		UInt32(),
		ForeignKey('addr_streets.streetid', name='addr_houses_fk_streetid', ondelete='CASCADE', onupdate='CASCADE'),
		Comment('Street ID'),
		nullable=False,
		info={
			'header_string' : _('Street'),
			'filter_type'   : 'nplist',
			'column_flex'   : 1
		}
	)
	district_id = Column(
		'districtid',
		UInt32(),
		ForeignKey('addr_districts.districtid', name='addr_houses_fk_districtid', ondelete='SET NULL', onupdate='CASCADE'),
		Comment('District ID'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('District'),
			'filter_type'   : 'nplist',
			'column_flex'   : 1
		}
	)
	number = Column(
		UInt16(),
		Comment('House number'),
		nullable=False,
		default=0,
		server_default=text('0'),
		info={
			'header_string' : _('Number')
		}
	)
	building = Column(
		UInt16(),
		Comment('House building'),
		nullable=False,
		default=0,
		server_default=text('0'),
		info={
			'header_string' : _('Building')
		}
	)
	second_number = Column(
		'num_slash',
		UInt16(),
		Comment('Second house number'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Second Num.')
		}
	)
	number_suffix = Column(
		'num_suffix',
		Unicode(32),
		Comment('House number suffix'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Num. Suffix')
		}
	)
	entrances = Column(
		'entrnum',
		UInt8(),
		Comment('Number of entrances'),
		nullable=False,
		default=1,
		server_default=text('1'),
		info={
			'header_string' : _('Entr. #')
		}
	)
	postal_code = Column(
		'postindex',
		Unicode(8),
		Comment('Postal code'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Postal Code')
		}
	)
	description = Column(
		'descr',
		UnicodeText(),
		Comment('House description'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Description')
		}
	)

	places = relationship(
		'Place',
		backref=backref('house', innerjoin=True),
		cascade='all, delete-orphan',
		passive_deletes=True
	)
	house_groupmap = relationship(
		'HouseGroupMapping',
		backref=backref('house', innerjoin=True),
		cascade='all, delete-orphan',
		passive_deletes=True
	)
	user_locations = relationship(
		'UserLocation',
		backref='house',
		cascade='all, delete-orphan',
		passive_deletes=True
	)

	house_groups = association_proxy(
		'house_groupmap',
		'group',
		creator=lambda v: HouseGroupMapping(group=v)
	)

	@classmethod
	def __augment_query__(cls, sess, query, params, req):
		flist = []
		if '__filter' in params:
			flist.extend(params['__filter'])
		if '__ffilter' in params:
			flist.extend(params['__ffilter'])
		for flt in flist:
			prop = flt.get('property', None)
			oper = flt.get('operator', None)
			value = flt.get('value', None)
			if prop == 'xdistrictid':
				if oper in ('eq', '=', '==', '==='):
					query = query.join(House.street).options(contains_eager(House.street))
					query = query.filter(or_(
						House.district_id == int(value),
						Street.district_id == int(value)
					))
			if prop == 'cityid':
				if oper in ('eq', '=', '==', '==='):
					query = query.join(House.street).options(contains_eager(House.street))
					query = query.filter(Street.city_id == int(value))
		return query

	@classmethod
	def __augment_result__(cls, sess, res, params, req):
		populate_related_list(
			res, 'id', 'house_groupmap', HouseGroupMapping,
			sess.query(HouseGroupMapping),
			None, 'house_id'
		)
		return res

	def __str__(self):
		loc = str
		req = getattr(self, '__req__', None)
		if req:
			loc = req.localizer.translate

		l = [str(self.street), str(self.number)]
		if self.number_suffix:
			l.append(self.number_suffix)
		if self.second_number:
			l.append('/' + str(self.second_number))
		if self.building:
			l.append(loc(_('bld.')))
			l.append(str(self.building))
		return ' '.join(l)

class Place(Base):
	"""
	Place object. Used for any container, shelf or storage space.
	"""

	@classmethod
	def _filter_hgroup(cls, query, value):
		if not isinstance(value, list):
			value = [value]
		return query.filter(Place.house_id.in_(
			DBSession().query(HouseGroupMapping.house_id)\
				.filter(HouseGroupMapping.group_id.in_(value))
		))

	@classmethod
	def _filter_address(cls, query, value):
		if not isinstance(value, dict):
			return query
		if 'houseid' in value:
			val = int(value['houseid'])
			if val > 0:
				query = query.filter(Place.house_id == val)
		elif 'streetid' in value:
			val = int(value['streetid'])
			if val > 0:
				query = query.join(Place.house).filter(House.street_id == val)
		elif 'districtid' in value:
			val = int(value['districtid'])
			if val > 0:
				query = query.join(Place.house).join(House.street).filter(or_(
					Street.district_id == val,
					House.district_id == val
				))
		elif 'cityid' in value:
			val = int(value['cityid'])
			if val > 0:
				query = query.join(Place.house).join(House.street).filter(Street.city_id == val)
		return query

	__tablename__ = 'addr_places'
	__table_args__ = (
		Comment('Places'),
		Index('addr_places_u_number', 'number', unique=True),
		Index('addr_places_i_houseid', 'houseid'),
		{
			'mysql_engine'  : 'InnoDB',
			'mysql_charset' : 'utf8',
			'info'          : {
				'cap_menu'      : 'BASE_GEO',
				'cap_read'      : 'GEO_LIST',
				'cap_create'    : 'GEO_CREATE',
				'cap_edit'      : 'GEO_EDIT',
				'cap_delete'    : 'GEO_DELETE',

				'show_in_menu'  : 'admin',
				'menu_name'     : _('Places'),
				'default_sort'  : ({ 'property' : 'number', 'direction' : 'ASC' },),
				'grid_view'     : ('placeid', 'house', 'number', 'name', 'entrance', 'floor', 'descr'),
				'grid_hidden'   : ('placeid',),
				'easy_search'   : ('number',),
				'detail_pane'   : ('netprofile_core.views', 'dpane_simple'),
				'extra_search'  : (
					CheckboxGroupFilter('hg', _filter_hgroup,
						title=_('House Group'),
						data='NetProfile.store.geo.HouseGroup',
						value_field='ahgid',
						display_field='name'
					),
					AddressFilter('address', _filter_address,
						title=_('Address')
					)
				),

				'create_wizard' : SimpleWizard(title=_('Add new place'))
			}
		}
	)

	id = Column(
		'placeid',
		UInt32(),
		Sequence('addr_places_placeid_seq'),
		Comment('Place ID'),
		primary_key=True,
		nullable=False,
		info={
			'header_string' : _('ID')
		}
	)
	house_id = Column(
		'houseid',
		UInt32(),
		ForeignKey('addr_houses.houseid', name='addr_places_fk_houseid', ondelete='CASCADE', onupdate='CASCADE'),
		Comment('House ID'),
		nullable=False,
		info={
			'header_string' : _('House'),
			'filter_type'   : 'none',
			'column_flex'   : 2
		}
	)
	number = Column(
		UInt16(),
		Comment('Place number'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Number')
		}
	)
	name = Column(
		Unicode(255),
		Comment('Place name'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Name'),
			'column_flex'   : 2
		}
	)
	entrance = Column(
		UInt8(),
		Comment('Entrance number'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Entr. #')
		}
	)
	floor = Column(
		UInt8(),
		Comment('Floor number'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Floor #')
		}
	)
	description = Column(
		'descr',
		UnicodeText(),
		Comment('Place description'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Description'),
			'column_flex'   : 1
		}
	)

	def __str__(self):
		if self.number:
			fmt = _('#%s')
			req = getattr(self, '__req__', None)
			if req:
				fmt = req.localizer.translate(fmt)
			return fmt % (str(self.number),)
		return str(self.name)

class HouseGroup(Base):
	"""
	Used for grouping arbitrary houses. Each house can be part of any
	number of groups.
	"""
	__tablename__ = 'addr_hgroups_def'
	__table_args__ = (
		Comment('House groups'),
		Index('addr_hgroups_def_u_name', 'name', unique=True),
		{
			'mysql_engine'  : 'InnoDB',
			'mysql_charset' : 'utf8',
			'info'          : {
				'cap_menu'      : 'BASE_GEO',
				'cap_read'      : 'GEO_LIST',
				'cap_create'    : 'GEO_CREATE',
				'cap_edit'      : 'GEO_EDIT',
				'cap_delete'    : 'GEO_DELETE',

				'show_in_menu'  : 'admin',
				'menu_name'     : _('House Groups'),
				'default_sort'  : ({ 'property': 'name' ,'direction': 'ASC' },),
				'grid_view'     : ('ahgid', 'name', 'descr'),
				'grid_hidden'   : ('ahgid',),
				'easy_search'   : ('name',),
				'detail_pane'   : ('netprofile_core.views', 'dpane_simple'),

				'create_wizard' : SimpleWizard(title=_('Add new house group'))
			}
		}
	)

	id = Column(
		'ahgid',
		UInt32(),
		Sequence('addr_hgroups_def_ahgid_seq'),
		Comment('House group ID'),
		primary_key=True,
		nullable=False,
		info={
			'header_string' : _('ID')
		}
	)
	name = Column(
		Unicode(255),
		Comment('House group name'),
		nullable=False,
		info={
			'header_string' : _('Name'),
			'column_flex'   : 1
		}
	)
	description = Column(
		'descr',
		UnicodeText(),
		Comment('House group description'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Description'),
			'column_flex'   : 1
		}
	)
	mappings = relationship(
		'HouseGroupMapping',
		backref=backref('group', innerjoin=True, lazy='joined'),
		cascade='all, delete-orphan',
		passive_deletes=True
	)

	houses = association_proxy(
		'mappings',
		'house'
	)

	def __str__(self):
		return str(self.name)

class HouseGroupMapping(Base):
	"""
	Mapping between houses and house groups.
	"""
	__tablename__ = 'addr_hgroups_houses'
	__table_args__ = (
		Comment('House group memberships'),
		Index('addr_hgroups_houses_u_member', 'ahgid', 'houseid', unique=True),
		Index('addr_hgroups_houses_i_houseid', 'houseid'),
		{
			'mysql_engine'  : 'InnoDB',
			'mysql_charset' : 'utf8',
			'info'          : {
				'menu_name'    : _('House Groups'),

				'cap_menu'     : 'BASE_GEO',
				'cap_read'     : 'GEO_LIST',
				'cap_create'   : 'GEO_CREATE',
				'cap_edit'     : 'GEO_EDIT',
				'cap_delete'   : 'GEO_DELETE',

				'default_sort' : (),
				'grid_view'    : ('group', 'house'),
				'detail_pane'  : ('netprofile_core.views', 'dpane_simple')
			}
		}
	)

	id = Column(
		'ahghid',
		UInt32(),
		Sequence('addr_hgroups_houses_ahghid_seq'),
		Comment('House group membership ID'),
		primary_key=True,
		nullable=False,
		info={
			'header_string' : _('ID')
		}
	)
	group_id = Column(
		'ahgid',
		UInt32(),
		ForeignKey('addr_hgroups_def.ahgid', name='addr_hgroups_houses_fk_ahgid', ondelete='CASCADE', onupdate='CASCADE'),
		Comment('House group ID'),
		nullable=False,
		info={
			'header_string' : _('Group')
		}
	)
	house_id = Column(
		'houseid',
		UInt32(),
		ForeignKey('addr_houses.houseid', name='addr_hgroups_houses_fk_houseid', ondelete='CASCADE', onupdate='CASCADE'),
		Comment('House ID'),
		nullable=False,
		info={
			'header_string' : _('House')
		}
	)

class UserLocation(Base):
	"""
	Users' addresses.
	"""
	__tablename__ = 'users_locations'
	__table_args__ = (
		Comment('User locations'),
		Index('users_locations_i_uid', 'uid'),
		Index('users_locations_i_houseid', 'houseid'),
		{
			'mysql_engine'  : 'InnoDB',
			'mysql_charset' : 'utf8',
			'info'          : {
				'cap_read'      : 'USERS_LIST',
				'cap_create'    : 'USERS_EDIT',
				'cap_edit'      : 'USERS_EDIT',
				'cap_delete'    : 'USERS_EDIT',

				'menu_name'     : _('User Addresses'),
				'default_sort'  : ({ 'property': 'atype' ,'direction': 'ASC' },),
				'grid_view'     : (
					'ulocid', 'user', 'primary', 'atype',
					MarkupColumn(
						header_string=_('Address'),
						column_flex=3,
						template='{__str__:htmlEncode}'
					)
				),
				'grid_hidden'   : ('ulocid',),
				'form_view'     : (
					'user', 'primary', 'atype', 'house',
					'country', 'stprov', 'city', 'addr',
					'entrance', 'floor', 'flat', 'room',
					'entrycode', 'postindex', 'descr'
				),
				'detail_pane'   : ('netprofile_core.views', 'dpane_simple'),
				'create_wizard' : SimpleWizard(title=_('Add new user address'))
			}
		}
	)
	id = Column(
		'ulocid',
		UInt32(),
		Sequence('users_locations_ulocid_seq'),
		Comment('User location ID'),
		primary_key=True,
		nullable=False,
		info={
			'header_string' : _('ID')
		}
	)
	user_id = Column(
		'uid',
		UInt32(),
		ForeignKey('users.uid', name='users_locations_fk_uid', ondelete='CASCADE', onupdate='CASCADE'),
		Comment('User ID'),
		nullable=False,
		info={
			'header_string' : _('User'),
			'filter_type'   : 'none'
		}
	)
	primary = Column(
		NPBoolean(),
		Comment('Primary flag'),
		nullable=False,
		default=False,
		server_default=npbool(False),
		info={
			'header_string' : _('Primary')
		}
	)
	type = Column(
		'atype',
		AddressType.db_type(),
		Comment('Address type'),
		nullable=False,
		default=AddressType.work,
		server_default=AddressType.work,
		info={
			'header_string' : _('Type'),
			'column_flex'   : 1
		}
	)
	country = Column(
		CHAR(2),
		Comment('ISO 3166-1 alpha-2 country code'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Country'),
			'choices'       : countries_alpha2
		}
	)
	state_or_province = Column(
		'stprov',
		Unicode(255),
		Comment('State or province name'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('State/province')
		}
	)
	city = Column(
		Unicode(255),
		Comment('City name'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('City')
		}
	)
	address = Column(
		'addr',
		Unicode(255),
		Comment('Freeform address'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Address')
		}
	)
	house_id = Column(
		'houseid',
		UInt32(),
		ForeignKey('addr_houses.houseid', name='users_locations_fk_houseid', ondelete='CASCADE', onupdate='CASCADE'),
		Comment('House ID'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('House'),
			'filter_type'   : 'none',
			'column_flex'   : 1
		}
	)
	entrance = Column(
		UInt8(),
		Comment('Entrance number'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Entr.')
		}
	)
	floor = Column(
		Int16(),
		Comment('Floor number'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Floor')
		}
	)
	flat = Column(
		UInt16(),
		Comment('Flat/office number'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Flat')
		}
	)
	room = Column(
		Unicode(8),
		Comment('Room identifier'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Room')
		}
	)
	entry_code = Column(
		'entrycode',
		Unicode(8),
		Comment('Entry code'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Entry Code')
		}
	)
	postal_code = Column(
		'postindex',
		Unicode(8),
		Comment('Postal code'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Postal Code')
		}
	)
	description = Column(
		'descr',
		UnicodeText(),
		Comment('Address description'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Description'),
			'column_flex'   : 2
		}
	)

	user = relationship(
		'User',
		innerjoin=True,
		backref=backref(
			'locations',
			cascade='all, delete-orphan',
			passive_deletes=True
		)
	)

	def __str__(self):
		req = self.__req__ or get_current_request()
		loc = req.localizer
		locale_cur = req.current_locale
		locale_en = req.locales['en']

		ret = []
		bit = self.country
		if bit:
			if bit in locale_cur.territories:
				bit = locale_cur.territories[bit]
			elif bit in locale_en.territories:
				bit = locale_en.territories[bit]
			ret.append(bit + ',')
		bit = self.city_address
		if bit:
			ret.append(bit + ',')
		bit = self.street_address
		if bit:
			ret.append(bit)
		if self.entrance:
			ret.extend((
				loc.translate(_('entr.')),
				str(self.entrance)
			))
		if self.floor:
			ret.extend((
				loc.translate(_('fl.')),
				str(self.floor)
			))
		if self.flat:
			pfx = _('app.')
			if self.type == AddressType.work:
				pfx = _('office')
			ret.extend((
				loc.translate(pfx),
				str(self.flat)
			))

		return ' '.join(ret)

	def add_to_vcard(self, card):
		data = dict()
		if self.country:
			data['country'] = self.country
		if self.state_or_province:
			data['region'] = self.state_or_province
		if self.postal_code:
			data['box'] = self.postal_code
		bit = self.city_address
		if bit:
			data['city'] = bit
		bit = self.street_address
		if bit:
			data['street'] = bit
		if len(data) > 0:
			obj = card.add('adr')
			obj.value = vobject.vcard.Address(**data)
			objtype = list(AddressType.vcard_types(self.type))
			if self.primary:
				objtype.append('pref')
			obj.type_paramlist = objtype

	@property
	def city_address(self):
		if self.house and self.house.street:
			return str(self.house.street.city)
		return self.city

	@property
	def street_address(self):
		if self.house:
			return str(self.house)
		return self.address

def _mod_userloc(mapper, conn, tgt):
	try:
		from netprofile_ldap.ldap import store
	except ImportError:
		return
	user = tgt.user
	user_id = tgt.user_id
	if (not user) and user_id:
		user = DBSession().query(User).get(user_id)
	if user:
		user.vcard = None
		store(user)

event.listen(UserLocation, 'after_delete', _mod_userloc)
event.listen(UserLocation, 'after_insert', _mod_userloc)
event.listen(UserLocation, 'after_update', _mod_userloc)

AddrFormatCompactFunction = SQLFunction(
	'addr_format_compact',
	args=(
		SQLFunctionArgument('streetname', Unicode(255)),
		SQLFunctionArgument('num', UInt16()),
		SQLFunctionArgument('num_slash', UInt16()),
		SQLFunctionArgument('num_suffix', Unicode(32)),
		SQLFunctionArgument('bld', UInt16()),
		SQLFunctionArgument('fl', UInt16())
	),
	returns=Unicode(255),
	comment='Format compact address',
	reads_sql=False,
	writes_sql=False
)

AddrFormatFunction = SQLFunction(
	'addr_format',
	args=(
		SQLFunctionArgument('streetname', Unicode(255)),
		SQLFunctionArgument('prefix', Unicode(8)),
		SQLFunctionArgument('suffix', Unicode(8)),
		SQLFunctionArgument('num', UInt16()),
		SQLFunctionArgument('num_slash', UInt16()),
		SQLFunctionArgument('num_suffix', Unicode(32)),
		SQLFunctionArgument('bld', UInt16()),
		SQLFunctionArgument('fl', UInt16())
	),
	returns=Unicode(255),
	comment='Format full address',
	reads_sql=False,
	writes_sql=False
)

AddrGetFullFunction = SQLFunction(
	'addr_get_full',
	args=(
		SQLFunctionArgument('hid', UInt32()),
	),
	returns=Unicode(255),
	comment='Get full address of a house by its ID',
	writes_sql=False
)

AddrListDistrictProcedure = SQLFunction(
	'addr_list_district',
	args=(
		InArgument('did', UInt32()),
	),
	comment='List all houses in a given district',
	writes_sql=False,
	is_procedure=True
)

AddrListEntrProcedure = SQLFunction(
	'addr_list_entr',
	args=(
		InArgument('minentr', UInt8()),
	),
	comment='List all houses which have at least given number of entries',
	writes_sql=False,
	is_procedure=True
)

AddrListStreetProcedure = SQLFunction(
	'addr_list_street',
	args=(
		InArgument('sid', UInt32()),
	),
	comment='List all houses on a given street',
	writes_sql=False,
	is_procedure=True
)

AddrCompactView = View('addr_compact', DBSession.query(
	House.id.label('houseid'),
	House.street_id.label('streetid'),
	Street.district_id.label('districtid'),
	City.id.label('cityid'),
	City.name.label('city'),
	func.addr_format_compact(Street.name, House.number, House.second_number, House.number_suffix, House.building, None).label('address'),
	House.entrances.label('entrnum'),
	House.postal_code.label('postindex')
).select_from(House).join(Street).join(Street.city).order_by(City.name, Street.name, House.number, House.second_number, House.number_suffix, House.building))

AddrExtraView = View('addr_extra', DBSession.query(
	House.id.label('houseid'),
	House.street_id.label('streetid'),
	Street.district_id.label('districtid'),
	City.id.label('cityid'),
	func.concat_ws(' ',
		func.concat(City.name, ','),
		func.concat(District.name, ','),
		func.addr_format(Street.name, Street.prefix, Street.suffix, House.number, House.second_number, House.number_suffix, House.building, None)
	).label('address'),
	House.entrances.label('entrnum'),
	House.postal_code.label('postindex')
).select_from(House).join(Street).outerjoin(District).join(Street.city).order_by(City.name, District.name, Street.name, House.number, House.second_number, House.number_suffix, House.building))

AddrFullView = View('addr_full', DBSession.query(
	House.id.label('houseid'),
	House.street_id.label('streetid'),
	Street.district_id.label('districtid'),
	City.id.label('cityid'),
	City.name.label('city'),
	func.addr_format(Street.name, Street.prefix, Street.suffix, House.number, House.second_number, House.number_suffix, House.building, None).label('address'),
	House.entrances.label('entrnum'),
	House.postal_code.label('postindex')
).select_from(House).join(Street).join(Street.city).order_by(City.name, Street.name, House.number, House.second_number, House.number_suffix, House.building))

AddrStreetNamesView = View('addr_streetnames', DBSession.query(
	Street.id.label('streetid'),
	District.id.label('districtid'),
	City.id.label('cityid'),
	City.name.label('city'),
	District.name.label('district'),
	func.addr_format(Street.name, Street.prefix, Street.suffix, None, None, None, None, None).label('fullname')
).select_from(Street).outerjoin(District).join(Street.city).order_by(City.name, District.name, Street.name))

