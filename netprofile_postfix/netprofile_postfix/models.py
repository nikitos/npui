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
	"PostfixAdmin",
	"PostfixDomain",
	"PostfixDomainAdmins",
	"PostfixLog",
	"PostfixVacation",
	"PostfixAlias",
	"PostfixMailbox",
	]

import datetime

from sqlalchemy import (
	Column,
	Date,
	DateTime,
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

_ = TranslationStringFactory('netprofile_postfix')


class PostfixAdmin(Base):
	"""
	Admin Account class
	"""
	__tablename__ = 'postfix_admin'
	__table_args__ = (
		Comment('PostfixAdmin Admin Accounts'),
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
				'menu_name'     : _('Postfix Admins'),
				'menu_order'    : 50,
				'default_sort'  : ({ 'property': 'username' ,'direction': 'ASC' },),
				'grid_view'     : ('username', 'password', 'active'
								   ),
				'form_view'		: ('username', 'password', 'created', 'modified', 'active'
								   ),
				'easy_search'   : ('username',),
				'detail_pane'   : ('netprofile_core.views', 'dpane_simple'),
				'create_wizard' : SimpleWizard(title=_('Add new Postfix admin account'))
				}
			}
		)
	id = Column(
		'id',
		UInt32(),
		Sequence('postfix_admin_seq'),
		Comment("ID"),
		primary_key=True,
		nullable=False,
		default=0,
		info={
			'header_string' : _('ID')
			}
		)

	#Foreign Key To PDNS Users?
	username = Column(
		'username',
		Unicode(255),
		Comment("Admin Username"),
		nullable=False,
		default='',
		info={
			'header_string' : _('Username')
			}
		)
	password = Column(
		'password',
		Unicode(255),
		Comment("Admin Password"),
		nullable=False,
		default = '',
		info={
			'header_string' : _('Password')
			}
		)
	created = Column(
		'created',
		DateTime(),
		Comment("User Creation Timestamp"),
		nullable=False,
		default=datetime.datetime.utcnow(),
		info={
			'header_string' : _('Created')
			}
		)
	modified = Column(
		'modified',
		DateTime(),
		Comment("User Modification Timestamp"),
		nullable=False,
		default=datetime.datetime.utcnow(),
		info={
			'header_string' : _('Modified')
			}
		)
	active = Column(
		'active',
		UInt8(),
		Comment("Is User Active"),
		nullable=False,
		default=1,
		info={
			'header_string' : _('Is Active?')
			}
		)

	def __str__(self):
		return(self.username)

class PostfixDomain(Base):
	"""
	Postfix Domain class
	"""
	__tablename__ = 'postfix_domain'
	__table_args__ = (
		Comment('Postfix Domains'),
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
				'menu_name'     : _('Postfix Domains'),
				'menu_order'    : 50,
				'default_sort'  : ({ 'property': 'domain' ,'direction': 'ASC' },),
				'grid_view'     : ('domain', 'created', 'modified', 'active',
				),
				'form_view'		: ('domain', 'aliases', 'mailboxes', 
								   'maxquota', 'transport', 'backupmx', 
								   'created', 'modified', 'active',
								   'description',
				),
				'easy_search'   : ('domain', ),
				'detail_pane'   : ('netprofile_core.views', 'dpane_simple'),
				#We should not add domains here but in the pdns module
				'create_wizard' : SimpleWizard(title=_('Add new domain'))
			}
		}
	)
	id = Column(
		'id',
		UInt32(),
		Sequence('postfix_domain_seq'),
		Comment("ID"),
		primary_key=True,
		nullable=False,
		default=0,
		info={
			'header_string' : _('ID')
			}
		)
	domain = Column(
		'domain',
		Unicode(255),
		Comment("Postfix Domain"),
		nullable=False,
		default='',
		info={
			'header_string' : _('Domain')
			}
		)
	description = Column(
		'description',
		Unicode(255),
		Comment("Domain Description"),
		nullable=False,
		default='',
		info={
			'header_string' : _('Description')
			}
		)
	#Foreign key from aliases table
	aliases = Column(
		'aliases',
		UInt32(),
		Comment("Mailbox Aliases"),
		nullable=False,
		default=0,
		info={
			'header_string' : _('Aliases')
			}
		)
	#Foreign key from mailboxes table
	mailboxes = Column(
		'mailboxes',
		UInt32(),
		Comment("Mailboxes"),
		nullable=False,
		default=0,
		info={
			'header_string' : _('Mailboxes')
			}
		)
	maxquota = Column(
		'maxquota',
		UInt32(),
		Comment("Max Quota"),
		nullable=False,
		default=0,
		info={
			'header_string' : _('Max Quota')
			}
		)
	transport = Column(
		'transport',
		Unicode(255),
		Comment("Transport"),
		nullable=True,
		info={
			'header_string' : _('Transport')
			}
		)
	backupmx  = Column(
		'backupmx',
		UInt8(),
		Comment("Backup MX Server"),
		nullable=False,
		default=1,
		info={
			'header_string' : _('Backup MX Server')
			}
		)
	created = Column(
		'created',
		DateTime(),
		Comment("Domain Creation Timestamp"),
		nullable=False,
		default=datetime.datetime.utcnow(),
		info={
			'header_string' : _('Created')
			}
		)
	modified = Column(
		'modified',
		DateTime(),
		Comment("Domain Modification Timestamp"),
		nullable=False,
		default=datetime.datetime.utcnow(),
		info={
			'header_string' : _('Modified')
			}
		)
	active = Column(
		'active',
		UInt8(),
		Comment("Is Domain Active"),
		nullable=False,
		default=1,
		info={
			'header_string' : _('Is Active?')
			}
		)
	
	def __str__(self):
		return(self.domain)


class PostfixDomainAdmins(Base):
	"""
	Postfix Domain-Admin relation class
	"""
	__tablename__ = 'postfix_domain_admins'
	__table_args__ = (
		Comment('Postfix Domain Admins table'),
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
				'menu_name'     : _('User Domains'),
				'menu_order'    : 50,
				'default_sort'  : ({ 'property': 'username' ,'direction': 'ASC' },),
				'grid_view'     : ('username', 'domain'	),
				'form_view'		: ('username', 'domain', 'created', 'active'),
				'easy_search'   : ('username', 'domain',),
				'detail_pane'   : ('netprofile_core.views', 'dpane_simple'),
				'create_wizard' : SimpleWizard(title=_('Add new user-domain relation'))
				}
			}
		)
	
	id = Column(
		'id',
		UInt32(),
		Sequence('postfix_domain_admins_seq'),
		Comment("ID"),
		primary_key=True,
		nullable=False,
		default=0,
		info={
			'header_string' : _('ID')
			}
		)
	#Foreign key to postfix admins
	username = Column(
		'username',
		Unicode(255),
		Comment("Admin Username"),
		nullable=False,
		default='',
		info={
			'header_string' : _('Username')
			}
		)
	#Foreign key to postfix domains
	domain = Column(
		'domain',
		Unicode(255),
		Comment("Postfix Domain"),
		nullable=False,
		default='',
		info={
			'header_string' : _('Domain')
			}
		)
	created = Column(
		'created',
		DateTime(),
		Comment("Domain Admin Creation Timestamp"),
		nullable=False,
		default=datetime.datetime.utcnow(),
		info={
			'header_string' : _('Created')
			}
		)
	active = Column(
		'active',
		UInt8(),
		Comment("Is Domain Admin Active"),
		nullable=False,
		default=1,
		info={
			'header_string' : _('Is Active?')
			}
		)

	def __str__(self):
		return(self.username)


class PostfixLog(Base):
	"""
	Postfix Log class
	"""
	__tablename__ = 'postfix_log'
	__table_args__ = (
		Comment('Postfix Log'),
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
				'menu_name'     : _('Logs'),
				'menu_order'    : 50,
				'default_sort'  : ({ 'property': 'timestamp' ,'direction': 'DESC' },),
				'grid_view'     : ('username', 'timestamp', 'domain', 'action',
								   ),
				'form_view'		: ('username', 'timestamp', 'domain', 'action', 'data',
								   ),
				'easy_search'   : ('domain','username'),
				'detail_pane'   : ('netprofile_core.views', 'dpane_simple'),
				'create_wizard' : SimpleWizard(title=_('Add new user-domain relation'))
				}
			}
		)
	id = Column(
		'id',
		UInt32(),
		Sequence('postfix_log_seq'),
		Comment("ID"),
		primary_key=True,
		nullable=False,
		default=0,
		info={
			'header_string' : _('ID')
			}
		)
	#Maybe ID as a primary key here and to database?
	timestamp = Column(
		'timestamp',
		DateTime(),
		Comment("Log Timestamp"),
		nullable=False,
		default=datetime.datetime.utcnow(),
		info={
			'header_string' : _('Timestamp')
			}
		)
	#Foreign key to postfix admins
	username = Column(
		'username',
		Unicode(255),
		Comment("Admin Username"),
		nullable=False,
		default='',
		info={
			'header_string' : _('Username')
			}
		)
	#Foreign key to postfix domains
	domain = Column(
		'domain',
		Unicode(255),
		Comment("Postfix Domain"),
		nullable=False,
		default='',
		info={
			'header_string' : _('Domain')
			}
		)
	action = Column(
		'action',
		Unicode(255),
		Comment("Log Action"),
		nullable=False,
		default='',
		info={
			'header_string' : _('Action')
			}
		)
	data = Column(
		'data',
		Unicode(255),
		Comment("Log Data"),
		nullable=False,
		default='',
		info={
			'header_string' : _('Data')
			}
		)

	def __str__(self):
		return("{0}:{1}".format(self.username, self.timestamp))


class PostfixVacation(Base):
	"""
	Postfix Vacation Autoresponder class
	"""
	__tablename__ = 'postfix_vacation'
	__table_args__ = (
		Comment('Vacation Autoresponder'),
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
				'menu_name'     : _('Vacation Autoresponder'),
				'menu_order'    : 50,
				'default_sort'  : ({ 'property': 'created' ,'direction': 'DESC' },),
				'grid_view'     : ('domain', 'email', 'subject', 'created', 'active'),
				'form_view'		: ('domain', 'email', 'subject', 'body', 'cache', 'created', 'active'),
				'easy_search'   : ('domain','email'),
				'detail_pane'   : ('netprofile_core.views', 'dpane_simple'),
				'create_wizard' : SimpleWizard(title=_('Add new vacation message'))
				}
			}
		)
	id = Column(
		'id',
		UInt32(),
		Sequence('postfix_vacation_seq'),
		Comment("ID"),
		primary_key=True,
		nullable=False,
		default=0,
		info={
			'header_string' : _('ID')
			}
		)
	#Maybe ID as a primary key here and to database?
	email = Column(
		'email',
		Unicode(255),
		Comment("Email"),
		nullable=False,
		default='',
		info={
			'header_string' : _('Email')
			}
		)
	subject = Column(
		'subject',
		Unicode(255),
		Comment("Subject"),
		nullable=False,
		default='',
		info={
			'header_string' : _('Subject')
			}
		)
	body = Column(
		'body',
		UnicodeText(),
		Comment("Body"),
		nullable=False,
		default='',
		info={
			'header_string' : _('Body')
			}
		)
	cache = Column(
		'cache',
		UnicodeText(),
		Comment("Cache"),
		nullable=False,
		default='',
		info={
			'header_string' : _('Cache')
			}
		)
	domain = Column(
		'domain',
		Unicode(255),
		Comment("Postfix Domain"),
		nullable=False,
		default='',
		info={
			'header_string' : _('Domain')
			}
		)
	created = Column(
		'created',
		DateTime(),
		Comment("Vacation Message Creation Timestamp"),
		nullable=False,
		default=datetime.datetime.utcnow(),
		info={
			'header_string' : _('Created')
			}
		)
	active = Column(
		'active',
		UInt8(),
		Comment("Is Vacation Autoresponder Admin Active"),
		nullable=False,
		default=1,
		info={
			'header_string' : _('Is Active?')
			}
		)

	def __str__(self):
		return("{0}:{1}".format(self.email, self.subject))


class PostfixAlias(Base):
	"""
	Postfix Alias class
	"""
	__tablename__ = 'postfix_alias'
	__table_args__ = (
		Comment('Postfix Aliases'),
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
				'menu_name'     : _('Aliases'),
				'menu_order'    : 50,
				'default_sort'  : ({ 'property': 'created' ,'direction': 'DESC' },),
				'grid_view'     : ('address', 'goto', 'domain', 'active',),
				'form_view'		: ('address', 'goto', 'domain', 'created', 'modified', 'active',),
				'easy_search'   : ('address', 'domain'),
				'detail_pane'   : ('netprofile_core.views', 'dpane_simple'),
				'create_wizard' : SimpleWizard(title=_('Add new alias'))
				}
			}
		)
	id = Column(
		'id',
		UInt32(),
		Sequence('postfix_alias_seq'),
		Comment("ID"),
		primary_key=True,
		nullable=False,
		default=0,
		info={
			'header_string' : _('ID')
			}
		)
	#Maybe ID as a primary key here and to database?
	address = Column(
		'address',
		Unicode(255),
		Comment("Address"),
		nullable=False,
		default='',
		info={
			'header_string' : _('Address')
			}
		)
	goto = Column(
		'goto',
		UnicodeText(),
		Comment("Destination"),
		nullable=False,
		default='',
		info={
			'header_string' : _('Destination')
			}
		)
	#Foreign key?
	domain = Column(
		'domain',
		Unicode(255),
		Comment("Domain"),
		nullable=False,
		default='',
		info={
			'header_string' : _('Domain')
			}
		)
	created = Column(
		'created',
		DateTime(),
		Comment("Alias Creation Timestamp"),
		nullable=False,
		default=datetime.datetime.utcnow(),
		info={
			'header_string' : _('Created')
			}
		)
	modified = Column(
		'modified',
		DateTime(),
		Comment("Alias Modification Timestamp"),
		nullable=False,
		default=datetime.datetime.utcnow(),
		info={
			'header_string' : _('Modified')
			}
		)
	active = Column(
		'active',
		UInt8(),
		Comment("Is Alias Active"),
		nullable=False,
		default=1,
		info={
			'header_string' : _('Is Active?')
			}
		)

	def __str__(self):
		return("{0}:{1}".format(self.address, self.goto))


class PostfixMailbox(Base):
	"""
	Postfix Mailbox class
	"""
	__tablename__ = 'postfix_mailbox'
	__table_args__ = (
		Comment('Postfix Mailboxes'),
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
				'menu_name'     : _('Mailboxes'),
				'menu_order'    : 50,
				'default_sort'  : ({ 'property': 'created' ,'direction': 'DESC' },),
				'grid_view'     : ('name', 'domain', 'active', ),
				'form_view'		: ('name', 'domain', 'username', 
								   'password', 'maildir', 'quota', 
								   'created', 'modified', 'active', ),
				'easy_search'   : ('name', 'domain', 'username'),
				'detail_pane'   : ('netprofile_core.views', 'dpane_simple'),
				'create_wizard' : SimpleWizard(title=_('Add new mailbox'))
				}
			}
		)
	id = Column(
		'id',
		UInt32(),
		Sequence('postfix_mailbox_seq'),
		Comment("ID"),
		primary_key=True,
		nullable=False,
		default=0,
		info={
			'header_string' : _('ID')
			}
		)
	#primary key here?
	username  = Column(
		'username',
		Unicode(255),
		Comment("Username"),
		nullable=False,
		default='',
		info={
			'header_string' : _('Username')
			}
		)
	password = Column(
		'password',
		Unicode(255),
		Comment("Password"),
		nullable=False,
		default='',
		info={
			'header_string' : _('Password')
			}
		)
	name = Column(
		'name',
		Unicode(255),
		Comment("Mailbox Name"),
		nullable=False,
		default='',
		info={
			'header_string' : _('Mailbox Name')
			}
		)
	maildir = Column(
		'maildir',
		Unicode(255),
		Comment("Mail Directory"),
		nullable=False,
		default='',
		info={
			'header_string' : _('Mail Directory')
			}
		)
	quota = Column(
		'quota',
		UInt32(),
		Comment("Quota"),
		nullable=False,
		default=0,
		info={
			'header_string' : _('Quota')
			}
		)
	#Foreign key here?
	domain = Column(
		'domain',
		Unicode(255),
		Comment("Domain"),
		nullable=False,
		default='',
		info={
			'header_string' : _('Domain')
			}
		)
	created = Column(
		'created',
		DateTime(),
		Comment("Mailbox Creation Timestamp"),
		nullable=False,
		default=datetime.datetime.utcnow(),
		info={
			'header_string' : _('Created')
			}
		)
	modified = Column(
		'modified',
		DateTime(),
		Comment("Mailbox Modification Timestamp"),
		nullable=False,
		default=datetime.datetime.utcnow(),
		info={
			'header_string' : _('Modified')
			}
		)
	active = Column(
		'active',
		UInt8(),
		Comment("Is Mailbox Active"),
		nullable=False,
		default=1,
		info={
			'header_string' : _('Is Active?')
			}
		)

	def __str__(self):
		return(self.name)
