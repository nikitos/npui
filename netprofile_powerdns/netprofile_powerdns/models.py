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
'PDNSFieldType',
'PDNSTemplateType',
'PDNSTemplate'
]

import datetime
import json

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
	Text,
	PrimaryKeyConstraint
)

from sqlalchemy.orm import (
	backref,
	relationship
)

from sqlalchemy.dialects.mysql import TINYINT

from sqlalchemy.ext.associationproxy import association_proxy
from pyramid.threadlocal import get_current_registry

from netprofile.db.connection import Base, DBSession
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
from netprofile.common.hooks import register_hook
from netprofile.ext.wizards import (
	SimpleWizard,
	Step,
	Wizard
)
from netprofile.ext.data import ExtModel

from pyramid.i18n import (
	TranslationStringFactory,
	get_localizer
)

_ = TranslationStringFactory('netprofile_powerdns')

@register_hook('np.wizard.init.powerdns.PDNSTemplate')
def _wizcb_pdnstemplate_submit(wiz, step, act, val, req):
	sess = DBSession()
	cfg = get_current_registry().settings

	fieldIDs = json.loads(val['field_id'])
	fieldlist = val['field']
	templateName = val['template']
	templId = val['templ_id']
	print(val)
	for fid in fieldIDs:
		resvalue = {'templ_id':templId, 'field_id':fid, 'template':templateName, 'field': sess.query(PDNSFieldType).filter(PDNSFieldType.id==fid).first()}
		em = ExtModel(PDNSTemplate)
		obj = PDNSTemplate()
		em.set_values(obj, resvalue, req, True)
		sess.add(obj)
		sess.flush()

	return {
		'do'     : 'close',
		'reload' : True
		}



class PDNSFieldType(Base):
	"""
	PDNS Template Field Types
	"""
	__tablename__ = 'pdns_recordtypes'
	__table_args__ = (
		Comment('PowerDNS Field Types'),
		{
			'mysql_engine'  : 'InnoDB',
			'mysql_charset' : 'utf8',
			'info'          : {
				'cap_menu'      : 'BASE_DOMAINS',
				#'cap_read'      : 'DOMAINS_LIST',
				#'cap_create'    : 'DOMAINS_CREATE',
				#'cap_edit'      : 'DOMAINS_EDIT',
				#'cap_delete'    : 'DOMAINS_DELETE',
				'show_in_menu'  : 'admin',
				'menu_name'     : _('PDNS Record Types'),
				'menu_order'    : 50,
				'default_sort'  : ({ 'property': 'name' ,'direction': 'ASC' },),
				'grid_view'     : ('name', 'defaultvalue'
				),
				'form_view'		: ('name', 'defaultvalue', 'descr'
				),
				'easy_search'   : ('name',),
				'detail_pane'   : ('netprofile_core.views', 'dpane_simple'),
				'create_wizard' : SimpleWizard(title=_('Add new domain record type'))
			}
		}
	)

	id = Column(
		'id',
		UInt32(),
		Sequence('pdns_recordtypes_recordidid_seq'),
		Comment('Record Type ID'),
		primary_key=True,
		nullable=False,
		info={
			'header_string' : _('ID')
			}
		)
	name = Column(
		'name',
		Unicode(255),
		Comment('Type name'),
		nullable=False,
		info={
			'header_string' : _('Type Name')
			}
		)
	descr = Column(
        'descr',
        UnicodeText(),
        Comment('Record type description'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string' : _('Description')
        }
    )
	defaultvalue = Column(
		'defaultvalue',
		Unicode(255),
		Comment('Field default value'),
		nullable=True,
		default=None,
		info={
			'header_string' : _('Default Value')
			}
		)
	def __str__(self):
		return self.name


class PDNSTemplateType(Base):
	"""
	PowerDNS Service Template  Typeclass
	"""
	__tablename__ = 'pdns_templatetypes'
	__table_args__ = (
		Comment('PowerDNS Template Types'),
		{
			'mysql_engine'  : 'InnoDB',
			'mysql_charset' : 'utf8',
			'info'          : {
				'cap_menu'      : 'BASE_DOMAINS',
				#'cap_read'      : 'DOMAINS_LIST',
				#'cap_create'    : 'DOMAINS_CREATE',
				#'cap_edit'      : 'DOMAINS_EDIT',
				#'cap_delete'    : 'DOMAINS_DELETE',
				'show_in_menu'  : 'admin',
				'menu_name'     : _('PDNS Template Types'),
				'menu_order'    : 50,
				'default_sort'  : ({ 'property': 'name' ,'direction': 'ASC' },),
				'grid_view'     : ('name', 'descr'
				),
				'form_view'		: ('name', 'descr'
				),
				'easy_search'   : ('name',),
				'detail_pane'   : ('netprofile_core.views', 'dpane_simple'),
				'create_wizard' : SimpleWizard(title=_('Add new template type'))
			}
		}
	)
	id = Column(
		'id',
		UInt32(),
		Sequence('pdns_templatetypes_templateid_seq'),
		Comment('Template Type ID'),
		primary_key=True,
		nullable=False,
		info={
			'header_string' : _('ID')
			}
		)
	name = Column(
		'name',
		Unicode(255),
		Comment('Template Type'),
		nullable=False,
		info={
			'header_string' : _('Template Type')
			}
		)
	descr = Column(
        'descr',
        UnicodeText(),
        Comment('Description'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string' : _('Description')
        }
    )
	fields = association_proxy('template_fields', 'field')#relationship('PDNSFieldType')
	
	def __str__(self):
		return self.name


class PDNSTemplate(Base):
	"""
	PDNS Association table for both template and field types
	"""
	__tablename__ = 'pdns_templates'
	__table_args__ = (
		Comment('PowerDNS Template-Field Association Table'),
		{
			'mysql_engine'  : 'InnoDB',
			'mysql_charset' : 'utf8',
			'info'          : {
				'cap_menu'      : 'BASE_DOMAINS',
				#'cap_read'      : 'DOMAINS_LIST',
				#'cap_create'    : 'DOMAINS_CREATE',
				#'cap_edit'      : 'DOMAINS_EDIT',
				#'cap_delete'    : 'DOMAINS_DELETE',
				'show_in_menu'  : 'admin',
				'menu_name'     : _('PDNS Templates'),
				'menu_order'    : 50,
				'grid_view'     : ('template', 'field', 'defaultvalues'
				),
				'form_view'		: ('template', 'field', 'defaultvalues'
				),
				'easy_search'   : ('template',),
				'detail_pane'   : ('netprofile_core.views', 'dpane_simple'),
				'create_wizard' : Wizard(
					Step(
						'template', 'field',
						id='generic', title=_('Add new template'),
						on_submit=_wizcb_pdnstemplate_submit
						)
					)
				}
			}
		)
	id = Column(
		'relationid',
		UInt32(),
		Sequence('pdns_templates_relationid_seq'),
		Comment('ID'),
		primary_key=True,
		nullable=False,
		info={
			'header_string' : _('ID')
		}
	)
	templateid = Column(
		'templ_id', 
		UInt32(),
		ForeignKey('pdns_templatetypes.id'),
		info={
			'header_string' : _('Template')
			}
		)
	fieldid = Column(
		'field_id',
		UInt32(),
		ForeignKey('pdns_recordtypes.id'),
		info={
			'header_string' : _('Record'),
			'editor_xtype'  : 'multimodelselect'
			}
		)
	defaultvalues = Column(
		'defvalues',
		Unicode(255),
		Comment('Default Values'),
		nullable=True,
		default=None,
		info={
			'header_string' : _('Default Values')
		}
	)
	template = relationship("PDNSTemplateType", backref=backref('template_fields', cascade="all, delete-orphan"))
	field = relationship("PDNSFieldType")

	def __str__(self):
		return '%s %s Record' % (self.template.name, self.field.name)
 

#don't need it for now 
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

	domainrecords = relationship("PDNSRecord", cascade='all, delete-orphan')

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
		ForeignKey('pdns_domains.id', name='pdns_records_fk_domain_id',ondelete='CASCADE', onupdate='CASCADE'),
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
		UInt32(),
		Comment('TTL'),
		nullable=True,
		default=None,
		info={
			'header_string' : _('TTL')
			}
		)
	prio = Column(
		'prio',
		UInt32(),
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
	domain = relationship(
        'PDNSDomain',
        innerjoin=True,
		backref=backref(
			'records',
			cascade='all, delete-orphan',
			passive_deletes=True
		)
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


