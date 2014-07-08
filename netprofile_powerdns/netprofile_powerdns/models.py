#!/usr/bin/env python
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-
#
# NetProfile: PowerDNS module - Models
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

__all__ = [
'UserDomain',
'PDNSComment',
'PDNSCryptokey',
'PDNSDomainMetadata',
'PDNSDomain',
'PDNSRecord',
'PDNSSupermaster',
'PDNSTsigkey',
#'PDNSDomainType',
#'PDNSRecordType'
]

#we need a simple many-to-many table with 3 fields - id, domainname, access_entity.id 
#http://wiki.powerdns.com/trac/wiki/fields
import datetime

from sqlalchemy import (
	Column,
	Date,
	ForeignKey,
	Index,
	Sequence,
	TIMESTAMP,
	Unicode,
	UnicodeText,
	text,
	Text
)

from sqlalchemy.orm import (
	backref,
	relationship
)
from sqlalchemy.dialects.mysql import TINYINT

from sqlalchemy.ext.associationproxy import association_proxy

from netprofile.db.connection import Base
from netprofile.db.fields import (
	ASCIIString,
	ASCIIText,
	ASCIITinyText,
	DeclEnum,
	NPBoolean,
	UInt8,
	UInt16,
	UInt32,
	npbool
)
from netprofile.db.ddl import Comment
from netprofile.tpl import TemplateObject
from netprofile.ext.columns import MarkupColumn
from netprofile.ext.wizards import (
	SimpleWizard,
	Step,
	Wizard
)

from pyramid.i18n import (
	TranslationStringFactory,
	get_localizer
)

_ = TranslationStringFactory('netprofile_powerdns')


class PDNSRecordType(DeclEnum):
	"""
	PDNS Domain Record Types
	"""
	SOA = 'SOA', _('Start of Authority Record'), 10
	NS = 'NS', _('Name Server Record'), 20
	MX = 'MX', _('Mail Exchange Record'), 30
	A = 'A', _('Address Record'), 40
	AAAA = 'AAAA', _('IPv6 Address Record'), 50
	CNAME = 'CNAME', _('Canonical Name Record'), 60
	TXT = 'TXT', _('Text Record'), 70
	PTR = 'PTR', _('Pointer Record'), 80
	HINFO = 'HINFO', _('Hardware Info Record'), 90
	SRV = 'SRV', _('Service Locator'), 100 
	NAPTR = 'NAPTR', _('Naming Authority Pointer'), 110


class PDNSDomainType(DeclEnum):
	"""
	PDNS Domain Types
	"""
	native = 'NATIVE', _('NATIVE'), 10
	master = 'MASTER', _('MASTER'), 20  
	slave = 'SLAVE', _('SLAVE'), 30  
	superslave = 'SUPERSLAVE', _('SUPERSLAVE'), 40


class UserDomain(Base):
	"""
	A Domain-User Relation object.
	"""
	__tablename__ = 'userdomains'
	__table_args__ = (
		Comment('User Domains'),
		{
			'mysql_engine'  : 'InnoDB',
			'mysql_charset' : 'utf8',
			'info'          : {
				'cap_menu'      : 'BASE_DOMAINS',
				#'cap_read'      : 'DOMAINS_LIST',
				#'cap_create'    : 'DOMAINS_CREATE',
				#'cap_edit'      : 'DOMAINS_EDIT',
				#'cap_delete'    : 'DOMAINS_DELETE',
				'show_in_menu'  : 'modules',
				'menu_name'     : _('User Domains'),
				'menu_order'    : 50,
				'default_sort'  : ({ 'property': 'name' ,'direction': 'ASC' },),
				'grid_view'     : ('accessuser', 'domainname'
				),
				'form_view'		: ('accessuser', 'domainname'
				),
				'easy_search'   : ('domain','accessuser'),
				'detail_pane'   : ('netprofile_core.views', 'dpane_simple'),
				'create_wizard' : SimpleWizard(title=_('Add new user-domain relation'))
			}
		}
	)

	id = Column(
		'id',
		UInt32(),
		Sequence('domains_def_domainid_seq'),
		Comment('Domain Name ID'),
		primary_key=True,
		nullable=False,
		info={
			'header_string' : _('ID')
		}
	)
	accessuser = Column(
		'accessuserid',
		UInt32(),
		ForeignKey('entities_access.entityid', name='userdomains_fk_accessuserid', onupdate='CASCADE'),
		Comment('Access Entity ID'),
		nullable=False,
		info={
			'header_string' : _('User')
		}
	)
	domainname = Column(
		'domainname',
		Unicode(255),
		Comment('Domain name'),
		nullable=False,
		info={
			'header_string' : _('Domain Name')
		}
	)

	def __str__(self):
		return '%s:%s' % str(self.domainname, self.accessuser)


class PDNSComment(Base):
	"""
	A PowerDNS Comment object
	"""
	__tablename__ = 'pdns_comments'
	__table_args__ = (
		Comment('PowerDNS Comments'),
		{
			'mysql_engine'  : 'InnoDB',
			'mysql_charset' : 'utf8',
			'info'          : {
				'cap_menu'      : 'BASE_DOMAINS',
				#'cap_read'      : 'DOMAINS_LIST',
				#'cap_create'    : 'DOMAINS_CREATE',
				#'cap_edit'      : 'DOMAINS_EDIT',
				#'cap_delete'    : 'DOMAINS_DELETE',
				'show_in_menu'  : 'modules',
				'menu_name'     : _('PowerDNS Comments'),
				'menu_order'    : 50,
				'default_sort'  : ({ 'property': 'id' ,'direction': 'ASC' },),
				'grid_view'     : ('domain_id', 'name', 'domaintype', 'comment'
				),
				'form_view'		: ('domain_id', 'name', 'domaintype', 'modified', 'comment'
				),
				'easy_search'   : ('domain_id'),
				'detail_pane'   : ('netprofile_core.views', 'dpane_simple'),
				'create_wizard' : SimpleWizard(title=_('Add new comment'))
			}
		}
	)

	commentid = Column(
		'id',
		UInt16(),
		Sequence('pdns_comments_id_seq'),
		Comment('Comment ID'),
		primary_key=True,
		nullable=False,
		info={
			'header_string' : _('ID')
			}
		)
	domain_id = Column(
		'domain_id',
		UInt16(),
		Comment('Domain ID'),
		ForeignKey('pdns_domains.id', name='pdns_comments_fk_domain_id'),
		nullable=False,
		info={
			'header_string' : _('Domain ID')
			}
		)
	domainname = Column(
		'name',
		Unicode(255),
		Comment('Domain Name'),
		nullable=False,
		info={
			'header_string' : _('Domain Name')
			}
		)
	domaintype = Column(
		'type',
		Unicode(10),
		Comment('Domain Type'),
		nullable=True,
		default=None,
		info={
			'header_string' : _('Domain Type')
			}
		)
	modified = Column(
		'modified_at',
		TIMESTAMP(),
		Comment('Modification timestamp'),
		nullable=False,
		default=datetime.datetime.utcnow,
		info={
			'header_string' : _('Modified')
			}
		)
	account = Column(
		'account',
		Unicode(10),
		Comment('Account'),
		nullable=False,
		info={
			'header_string' : _('Account')
			}
		)
	comment = Column(
		'comment',
		UnicodeText(),
		nullable=False,
		info={
			'header_string' : _('Comment')
			}
		)
	
	def __str__(self):
		return '%s:%s:%s' % str(self.domainname, self.account, self.comment)


class PDNSCryptokey(Base):
	"""
	PowerDNS Cryptokey
	"""
	__tablename__ = 'pdns_cryptokeys'
	__table_args__ = (
		Comment('PowerDNS Cryptokeys'),
		{
			'mysql_engine'  : 'InnoDB',
			'mysql_charset' : 'utf8',
			'info'          : {
				'cap_menu'      : 'BASE_DOMAINS',
				#'cap_read'      : 'DOMAINS_LIST',
				#'cap_create'    : 'DOMAINS_CREATE',
				#'cap_edit'      : 'DOMAINS_EDIT',
				#'cap_delete'    : 'DOMAINS_DELETE',
				'menu_name'    : _('PowerDNS Cryptokeys'),
				'show_in_menu'  : 'modules',
				'menu_order'    : 30,
				'default_sort'  : ({ 'property': 'ip', 'direction': 'ASC' },),
				'grid_view'     : ('domain_id', 'flags', 'active', 'content'),
				'easy_search'   : ('domain_id', 'flags', 'active', 'content'),
				'detail_pane'   : ('netprofile_core.views', 'dpane_simple'),
				'create_wizard' : SimpleWizard(title=_('Add new cryptokey'))
			}
		}
	)
	id = Column(
		'id',
		UInt16(),
		Comment('Cryptokey ID'),
		primary_key=True,
		nullable=False,
		info={
			'header_string' : _('ID')
			}
		)
	domain_id = Column(
		'domain_id',
		UInt16(),
		Comment('Domain ID'),
		ForeignKey('pdns_domains.id', name='pdns_cryptokeys_fk_domain_id'),
		nullable=False,
		info={
			'header_string' : _('Domain ID')
			}
		)
	flags = Column(
		'flags',
		UInt16(),
		Comment('Flags'),
		nullable=False,
		info={
			'header_string' : _('Flags')
			}
		)
	active = Column(
		'active',
		UInt8(),
		nullable=True,
		default=None,
		info={
			'header_string' : _('Active')
			}
		)
	content = Column(
		'content',
		UnicodeText(),
		nullable=False,
		info={
			'header_string' : _('Content')
			}
		)

	def __str__(self):
		return '%s:%s' % (self.domain_id, self.content)


class PDNSDomainMetadata(Base):
	"""
	PowerDNS Domain Metadata
	"""
	__tablename__ = 'pdns_domainmetadata'
	__table_args__ = (
		Comment('PowerDNS Domain Metadata'),
		{
			'mysql_engine'  : 'InnoDB',
			'mysql_charset' : 'utf8',
			'info'          : {
				'cap_menu'      : 'BASE_DOMAINS',
				#'cap_read'      : 'DOMAINS_LIST',
				#'cap_create'    : 'DOMAINS_CREATE',
				#'cap_edit'      : 'DOMAINS_EDIT',
				#'cap_delete'    : 'DOMAINS_DELETE',
				'menu_name'    : _('PowerDNS Domain Metadata'),
				'show_in_menu'  : 'modules',
				'menu_order'    : 30,
				'default_sort'  : ({ 'property': 'id', 'direction': 'ASC' },),
				'grid_view'     : ('domain_id', 'kind', 'content'),
				'easy_search'   : ('domain_id', 'kind', 'content'),
				'detail_pane'   : ('netprofile_core.views', 'dpane_simple'),
				'create_wizard' : SimpleWizard(title=_('Add new domain metadata'))
			}
		}
	)

	id = Column(
		'id',
		UInt16(),
		Comment('Metadata ID'),
		primary_key=True,
		nullable=False,
		info={
			'header_string' : _('ID')
			}
		)
	domain_id = Column(
		'domain_id',
		UInt16(),
		Comment('Domain ID'),
		#ForeignKey
		ForeignKey('pdns_domains.id', name='pdns_domainmetadata_fk_domain_id'),
		nullable=False,
		info={
			'header_string' : _('Domain ID')
			}
		)
	kind = Column(
		'kind',
		Unicode(16),
		Comment('Kind of metadata'),
		nullable=True,
		default=None,
		info={
			'header_string' : _('Kind')
			}
		)
	content = Column(
		'content',
		UnicodeText(),
		nullable=False,
		info={
			'header_string' : _('Content')
			}
		)
	
	def __str__(self):
		return "%s:%s" % (self.domain_id, self.content)


class PDNSDomain(Base):
	"""
	PowerDNS Domain
	"""
	__tablename__ = 'pdns_domains'
	__table_args__ = (
		Comment('PowerDNS Domain Record'),
		{
			'mysql_engine'  : 'InnoDB',
			'mysql_charset' : 'utf8',
			'info'          : {
				'cap_menu'      : 'BASE_DOMAINS',
				#'cap_read'      : 'DOMAINS_LIST',
				#'cap_create'    : 'DOMAINS_CREATE',
				#'cap_edit'      : 'DOMAINS_EDIT',
				#'cap_delete'    : 'DOMAINS_DELETE',
				'menu_name'    : _('PowerDNS Domain Records'),
				'show_in_menu'  : 'modules',
				'menu_order'    : 30,
				'default_sort'  : ({ 'property': 'name', 'direction': 'ASC' },),
				'grid_view'     : ('name', 'dtype'),
				'easy_search'   : ('name', 'master', 'last_check', 'dtype', 'notified_serial'),
				'detail_pane'   : ('netprofile_core.views', 'dpane_simple'),
				'create_wizard' : SimpleWizard(title=_('Add new DNS domain'))
			}
		}
	)

	id = Column(
		'id',
		UInt16(),
		Comment('Domain ID'),
		primary_key=True,
		nullable=False,
		info={
			'header_string' : _('ID')
			}
		)
	name = Column(
		'name',
		Unicode(255),
		Comment('Name'),
		nullable=False,
		info={
			'header_string' : _('Name')
			}
		)
	master = Column(
		'master',
		Unicode(128),
		Comment('Master Nameserver'),
		nullable=True,
		default=None,
		info={
			'header_string' : _('Master')
			}
		)
	last_check = Column(
		'last_check',
		TIMESTAMP(),
		Comment('Last check timestamp'),
		nullable=True,
		default=None,
		info={
			'header_string' : _('Last Check')
			}
		)
	dtype = Column(
		'type',
		Unicode(10),
		Comment('Domain Type'),
		nullable=True,
		default=None,
		info={
			'header_string' : _('Type')
			}
		)
	notified_serial = Column(
		'notified_serial',
		UInt16(),
		Comment('Notified Serial'),
		nullable=True,
		default=None,
		info={
			'header_string' : _('Notified Serial')
			}
		)
	account = Column(
		'account',
		Unicode(40),
		Comment('Account'),
		nullable=True,
		default=None,
		info={
			'header_string' : _('Account')
			}
		)

	def __str__(self):
		return self.name
	

class PDNSRecord(Base):
	"""
	PowerDNS DNS Record
	"""
	__tablename__ = 'pdns_records'
	__table_args__ = (
		Comment('PowerDNS DNS Record'),
		{
			'mysql_engine'  : 'InnoDB',
			'mysql_charset' : 'utf8',
			'info'          : {
				'cap_menu'      : 'BASE_DOMAINS',
				#'cap_read'      : 'DOMAINS_LIST',
				#'cap_create'    : 'DOMAINS_CREATE',
				#'cap_edit'      : 'DOMAINS_EDIT',
				#'cap_delete'    : 'DOMAINS_DELETE',
				'menu_name'    : _('PowerDNS DNS Records'),
				'show_in_menu'  : 'modules',
				'menu_order'    : 30,
				'default_sort'  : ({ 'property': 'name', 'direction': 'ASC' },),
				'grid_view'     : ('name', 'rtype'),
				'easy_search'   : ('name', 'master', 'last_check', 'rtype', 'notified_serial'),
				'detail_pane'   : ('netprofile_core.views', 'dpane_simple'),
				'create_wizard' : SimpleWizard(title=_('Add new DNS record'))
			}
		}
	)

	id = Column(
		'id',
		UInt16(),
		Comment('Domain ID'),
		primary_key=True,
		nullable=False,
		info={
			'header_string' : _('ID')
			}
		)
	domain_id = Column(
		'domain_id',
		UInt16(),
		Comment('Domain ID'),
		#ForeignKey
		ForeignKey('pdns_domains.id', name='pdns_records_fk_domain_id'),
		nullable=False,
		info={
			'header_string' : _('Domain ID')
			}
		)
	name = Column(
		'name',
		Unicode(255),
		Comment('Name'),
		nullable=True,
		default=None,
		info={
			'header_string' : _('Name')
			}
		)
	rtype = Column(
		'type',
		Unicode(10),
		Comment('Record Type'),
		nullable=True,
		default=None,
		info={
			'header_string' : _('Record Type')
			}
		)
	content = Column(
		'content',
		UnicodeText(),
		Comment('Content'),
		nullable=True,
		default=None,
		info={
			'header_string' : _('Content')
			}
		)
	ttl = Column(
		'ttl',
		UInt16(),
		Comment('TTL'),
		nullable=True,
		default=None,
		info={
			'header_string' : _('TTL')
			}
		)
	prio = Column(
		'prio',
		UInt16(),
		Comment('Priority'),
		nullable=True,
		default=None,
		info={
			'header_string' : _('Priority')
			}
		)
	change_date = Column(
		'change_date',
		TIMESTAMP(),
		Comment('Change Date Timestamp'),
		nullable=True,
		default=None,
		info={
			'header_string' : _('Change Date')
			}
		)
	disabled = Column(
		'disabled',
		TINYINT(1),
		Comment('Disabled Flag'),
		nullable=False,
		default=0,
		info={
			'header_string' : _('Disabled')
			}
		)
	ordername = Column(
		'ordername',
		Unicode(255),
		Comment('Order Name'),
		nullable=True,
		default=None,
		info={
			'header_string' : _('Order Name')
			}
		) 
	auth = Column(
		'auth',
		TINYINT(1),
		Comment('Authoritative Zone Flag'),
		nullable=False,
		default=1,
		info={
			'header_string' : _('Authoritative Zone Flag')
			}
		)

	def __str__(self):
		return("{0} {1} {2} {3}".format(self.name, self.rtype, self.content, self.ttl))


class PDNSSupermaster(Base):
	"""
	PowerDNS Supermaster Record
	"""
	__tablename__ = 'pdns_supermasters'
	__table_args__ = (
		Comment('PowerDNS Supermaster record'),
		{
			'mysql_engine'  : 'InnoDB',
			'mysql_charset' : 'utf8',
			'info'          : {
				'cap_menu'      : 'BASE_DOMAINS',
				#'cap_read'      : 'DOMAINS_LIST',
				#'cap_create'    : 'DOMAINS_CREATE',
				#'cap_edit'      : 'DOMAINS_EDIT',
				#'cap_delete'    : 'DOMAINS_DELETE',
				'menu_name'    : _('PowerDNS Supermaster Record'),
				'show_in_menu'  : 'modules',
				'menu_order'    : 30,
				'default_sort'  : ({ 'property': 'ip', 'direction': 'ASC' },),
				'grid_view'     : ('ip', 'nameserver'),
				'easy_search'   : ('ip', 'nameserver'),
				'detail_pane'   : ('netprofile_core.views', 'dpane_simple'),
				'create_wizard' : SimpleWizard(title=_('Add new DNS supermaster record'))
			}
		}
	)
	id = Column(
		'id',
		UInt16(),
		Comment('Supermaster ID'),
		primary_key=True,
		nullable=False,
		info={
			'header_string' : _('ID')
			}
		)
	ip = Column(
		'ip',
		Unicode(64),
		Comment('IP Address'),
		nullable=False,
		info={
			'header_string' : _('IP Address')
			}
		)
	nameserver = Column(
		'nameserver',
		Unicode(255),
		Comment('Nameserver'),
		nullable=False,
		info={
			'header_string' : _('Nameserver')
			}
		)
	account = Column(
		'account',
		Unicode(40),
		Comment('Account'),
		nullable=True,
		default=None,
		info={
			'header_string' : _('Account')
			}
		)

	def __str__(self):
		return "%s:%s" % (self.ip, self.nameserver)


class PDNSTsigkey(Base):
	"""
	PowerDNS TSIG shared secrets
	"""
	__tablename__ = 'pdns_tsigkeys'
	__table_args__ = (
		Comment('PowerDNS TSIG shared secrets'),
		{
			'mysql_engine'  : 'InnoDB',
			'mysql_charset' : 'utf8',
			'info'          : {
				'cap_menu'      : 'BASE_DOMAINS',
				#'cap_read'      : 'DOMAINS_LIST',
				#'cap_create'    : 'DOMAINS_CREATE',
				#'cap_edit'      : 'DOMAINS_EDIT',
				#'cap_delete'    : 'DOMAINS_DELETE',
				#'menu_name'    : _('TSIG Shared Secrets'),
				'show_in_menu'  : 'modules',
				'menu_order'    : 30,
				'default_sort'  : ({ 'property': 'name', 'direction': 'ASC' },),
				'grid_view'     : ('name', 'algorithm', 'secret'),
				'easy_search'   : ('name', 'algorithm', 'secret'),
				'detail_pane'   : ('netprofile_core.views', 'dpane_simple'),
				'create_wizard' : SimpleWizard(title=_('Add new TSIG shared secret'))
				#'create_wizard' : SimpleWizard(title=_('Add new accounting destination set'))
			}
		}
	)
	id = Column(
		'id',
		UInt16(),
		Comment('Secret ID'),
		primary_key = True,
		nullable=False,
		info={
			'header_string' : _('ID')
		}
	)
	name = Column(
		'name',
		Unicode(255),
		Comment('Shared secret name'),
		nullable=True,
		default=None,
		info={
			'header_string' : _('Name')
		}
	)
	algorithm = Column(
		'algorithm',
		Unicode(50),
		nullable=True,
		default=None,
		info={
			'header_string' : _('Algorithm')
		}
	)
	secret = Column(
		'secret',
		Unicode(255),
		nullable=True,
		default=None,
		info={
			'header_string' : _('Secret')
		}
	)

	def __str__(self):
		return self.name
