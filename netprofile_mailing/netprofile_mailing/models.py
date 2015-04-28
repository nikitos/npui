#!/usr/bin/env python
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-
#
# NetProfile: Mailing module - Models
# © Copyright 2013-2015 Alex 'Unik' Unigovsky
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
	'MailingTemplate',
	'MailingLog'
	'MailingSubscription',
]

import hashlib
import datetime
import json 
import transaction

from pyramid_mailer import get_mailer
from pyramid_mailer.message import (
	Attachment,
	Message
)
from pyramid.threadlocal import get_current_registry

from sqlalchemy import (
	Column,
	DateTime,
	FetchedValue,
	ForeignKey,
	Index,
	Sequence,
	TIMESTAMP,
	Unicode,
	UnicodeText
)

from sqlalchemy.orm import (
	backref,
	relationship
)

from sqlalchemy.ext.associationproxy import association_proxy

from sqlalchemy.ext.hybrid import hybrid_property

from netprofile.db.connection import (
	Base,
	DBSession
)
from netprofile.db.fields import (
	ASCIIString,
	NPBoolean,
	UInt8,
	UInt16,
	UInt32,
	npbool,
	IPv4Address,
	IPv6Address,
	IPv6Offset
)
from netprofile.db.ddl import (
	Comment,
	Trigger
)
from netprofile.tpl import TemplateObject
from netprofile.ext.columns import MarkupColumn
from netprofile.common.hooks import register_hook
from netprofile.ext.data import (
	ExtModel,
	_name_to_class
)
from netprofile.ext.wizards import (
	ExternalWizardField,
	SimpleWizard,
	Step,
	Wizard
)
from pyramid.i18n import (
	TranslationStringFactory,
	get_localizer
)

from netprofile_access.models import AccessEntity

_ = TranslationStringFactory('netprofile_mailing')

@register_hook('np.wizard.init.mailing.MailingLog')
def _wizcb_maillog_submit(wiz, step, act, val, req):
	sess = DBSession()
	cfg = get_current_registry().settings
	mailer = get_mailer(req)

	

	userIDs = json.loads(val['userid'])
	userlist = val['user']
	templateName = val['template']
	templId = val['templid']
	receiver = None
	sender = cfg.get('netprofile.mailing.sender', 'admin@mysite.com')
	sendername = cfg.get('sender.name', 'localadmin')
	mailhost = cfg.get('mail.host', 'localhost')

	for userid in userIDs:
		resvalue = {'userid' : userid}
		user = sess.query(AccessEntity).filter(AccessEntity.id==userid).first()
		subscr = sess.query(MailingSubscription).filter(MailingSubscription.userid==userid).first()
		print("########################## SUBSCR ###########################")
		
		#a long try-except statement to check if user is in mailing list
		try:
			if subscr.issubscribed is True:
				templateBody = sess.query(MailingTemplate).filter(MailingTemplate.id==templId).first().body
				resvalue['user'] = user
				resvalue['template'] = templateBody
				resvalue['templid'] = templId
		
				if user.parent:
					try:
						receiver = user.parent.email
					except AttributeError:
						print("################### USER'S PARENT HAVE NO EMAIL ATTRIBUTE #######################")
	
				if receiver is not None:
					msg_text = Attachment(data=templateBody,
										  content_type='text/plain; charset=\'utf-8\'',
										  disposition='inline',
										  transfer_encoding='quoted-printable'
										  )
					msg_html = Attachment(data=templateBody,
										  content_type='text/html; charset=\'utf-8\'',
										  disposition='inline',
										  transfer_encoding='quoted-printable'
										  )
					message = Message(
						subject=(templateName),
						sender=sender,
						recipients=(receiver,),
						body=msg_text,
						html=msg_html
						)

					mailer.send(message)
					resvalue['letteruid'] = hashlib.md5((templateBody + user.nick + str(datetime.datetime.now())).encode()).hexdigest()
					em = ExtModel(MailingLog)
					obj = MailingLog()
					em.set_values(obj, resvalue, req, True)
					sess.add(obj)
					sess.flush()
				else:
					print("################### USER HAVE NO EMAIL #######################")

		except AttributeError:
			print("########################## USER NOT IN SUBSCR LIST ###########################")

	return {
		'do'     : 'close',
		'reload' : True
		}


class MailingTemplate(Base):
	"""
	Mailing Template object
	"""
	__tablename__ = 'mailing_templates'
	__table_args__ = (
		Comment('Mailing Templates'),
		Index('mailing_templates_u_name', 'name', unique=True),
		{
			'mysql_engine'  : 'InnoDB',
			'mysql_charset' : 'utf8',
			'info'          : {
				#CORRECT PRIVLIEGES
				'cap_menu'      : 'BASE_NETS',
				'cap_read'      : 'NETS_LIST',
				'cap_create'    : 'NETS_CREATE',
				'cap_edit'      : 'NETS_EDIT',
				'cap_delete'    : 'NETS_DELETE',
				'menu_name'     : _('Mail Templates'),
				'show_in_menu'  : 'admin',
				'menu_order'    : 10,
				'menu_main'     : False,
				'default_sort'  : ({ 'property': 'name', 'direction': 'ASC' },),
				'grid_view'     : (
					'name', 'body'
				),
				'form_view'     : (
					'name', 'body'
				),
				'easy_search'   : ('name',),
				'detail_pane'   : ('netprofile_core.views', 'dpane_simple'),
				'create_wizard' : SimpleWizard(title=_('Add new mailing template'))
			}
		}
	)
	id = Column(
		'templid',
		UInt32(),
		Sequence('mailing_templates_templ_seq'),
		Comment('Template ID'),
		primary_key=True,
		nullable=False,
		info={
			'header_string' : _('ID')
		}
	)
	name = Column(
		Unicode(255),
		Comment('Template Name'),
		nullable=False,
		info={
			'header_string' : _('Name')
		}
	)
	body = Column(
		UnicodeText(),
		Comment('Template body'),
		nullable=False,
		info={
			'header_string' : _('Template Body'),
			'editor_xtype'  : 'tinymce_field',
			'editor_config' : {
				'tinyMCEConfig' : {
					'theme'                             : 'advanced',
					'skin'                              : 'extjs',
					'inlinepopups_skin'                 : 'extjs',
					'theme_advanced_row_height'         : 27,
					'delta_height'                      : 1,
					'schema'                            : 'html5',
					'plugins'                           : 'lists,pagebreak,style,layer,table,save,advhr,advimage,advlink,iespell,inlinepopups,insertdatetime,preview,media,searchreplace,print,contextmenu,paste,directionality,fullscreen,noneditable,visualchars,visualblocks,nonbreaking,xhtmlxtras,template,wordcount,advlist',

					'theme_advanced_buttons1'           : 'bold,italic,underline,strikethrough,|,justifyleft,justifycenter,justifyright,justifyfull,styleselect,formatselect,fontselect,fontsizeselect',
					'theme_advanced_buttons2'           : 'cut,copy,paste,pastetext,pasteword,|,search,replace,|,bullist,numlist,|,outdent,indent,blockquote,|,undo,redo,|,link,unlink,anchor,image,cleanup,help,code,|,insertdate,inserttime,preview,|,forecolor,backcolor',
					'theme_advanced_buttons3'           : 'tablecontrols,|,hr,removeformat,visualaid,|,sub,sup,|,charmap,emotions,iespell,media,advhr,|,print,|,ltr,rtl,|,fullscreen',
					'theme_advanced_buttons4'           : 'insertlayer,moveforward,movebackward,absolute,|,styleprops,|,cite,abbr,acronym,del,ins,attribs,|,visualchars,visualblocks,nonbreaking,template,pagebreak,restoredraft',

					'theme_advanced_toolbar_location'   : 'top',
					'theme_advanced_toolbar_align'      : 'left',
					'theme_advanced_statusbar_location' : 'bottom',

					'extended_valid_elements'           : '+tpl[if|elsif|else|for|foreach|switch|case|default]',
					'custom_elements'                   : '~tpl',
					'valid_children'                    : '+*[tpl],+tpl[*],+tbody[tpl],+body[tpl],+table[tpl],+tpl[table|tr|tpl|#text]'

					}
				}
			}
		)
	def __str__(self):
		return self.name

class MailingLog(Base):
	__tablename__ = 'mailing_log'
	__table_args__ = (
		Comment('Mailing Logs'),
		Index('mailing_log_u_letteruid', 'letteruid', unique=True),
		{
			'mysql_engine'  : 'InnoDB',
			'mysql_charset' : 'utf8',
			'info'          : {
				#REVIEW PRIVILEGES
				'cap_menu'      : 'BASE_NETS',
				'cap_read'      : 'NETS_LIST',
				'cap_create'    : 'NETS_CREATE',
				'cap_edit'      : 'NETS_EDIT',
				'cap_delete'    : 'NETS_DELETE',
				'menu_name'     : _('Mailing Logs'),
				'show_in_menu'  : 'admin',
				'menu_order'    : 20,
				'menu_main'     : False,
				'default_sort'  : ({ 'property': 'senttime', 'direction': 'ASC' },),
				'grid_view'     : (
					'senttime', 'user', 'isread', 'letteruid'
				),
				'form_view'     : (
					'senttime', 'readtime', 'user', 'isread', 'letteruid'
				),
				'easy_search'   : ('user'),
				'detail_pane'   : ('netprofile_core.views', 'dpane_simple'),
				'create_wizard' : Wizard(
					Step(
						'user', 'template',
						id='generic', title=_('Send new mail'),
						on_submit=_wizcb_maillog_submit
						)
					)
				}
			}
		)
	id = Column(
		'logid',
		UInt32(),
		Sequence('mailing_log_logid_seq'),
		Comment('Log ID'),
		primary_key=True,
		nullable=False,
		info={
			'header_string' : _('ID')
		}
	)
	senttime = Column(
		'senttime',
		TIMESTAMP(),
		Comment('Sending timestamp'),
		nullable=True,
		default=None,
		server_default=FetchedValue(),
		info={
			'header_string' : _('Sent at'),
			'read_only'     : True
		}
	)
	readtime = Column(
		'readtime',
		TIMESTAMP(),
		Comment('Read timestamp'),
		nullable=True,
		default=None,
		server_default=FetchedValue(),
		info={
			'header_string' : _('Read at'),
			'read_only'     : True
		}
	)
	userid = Column(
		'userid',
		UInt32(),
		ForeignKey('entities_access.entityid', name='mailing_log_fk_userid', ondelete='CASCADE', onupdate='CASCADE'),
		Comment('Access Entity ID'),
		nullable=False,
		info={
			'header_string' : _('User'),
			'editor_xtype'  : 'multimodelselect'
		}
	)
	templid = Column(
		'templid',
		UInt32(),
		ForeignKey('mailing_templates.templid', name='mailing_log_fk_templid', ondelete='CASCADE', onupdate='CASCADE'),
		Comment('Template ID'),
		nullable=False,
		info={
			'header_string' : _('Template')
		}
	)
	letteruid = Column(
		Unicode(255),
		Comment('Letter UID'),
		nullable=False,
		info={
			'header_string' : _('Letter ID'),
			}
		)
	isread = Column(
		'isread',
		NPBoolean(),
		Comment('Is letter read?'),
		nullable=False,
		default=False,
		server_default=npbool(False),
		info={
			'header_string' : _('Is letter read?')
		}
	)
	user = relationship(
		'AccessEntity',
		primaryjoin='MailingLog.userid == AccessEntity.id'
	)
	template = relationship(
		'MailingTemplate',
	)


#add a trigger to access entity, when create new access entity user, automatically subscribe
class MailingSubscription(Base):
	"""
	Mailing subscription settings
	"""
	__tablename__ = 'mailing_settings'
	__table_args__ = (
		Comment('Mailing Settings'),
		Index('mailing_settings_u_userid', 'userid', unique=True),
		{
			'mysql_engine'  : 'InnoDB',
			'mysql_charset' : 'utf8',
			'info'          : {
				#'cap_menu'      : 'BASE_ENTITIES',
				#'cap_read'      : 'NETS_LIST',
				#'cap_create'    : 'NETS_CREATE',
				#'cap_edit'      : 'NETS_EDIT',
				#'cap_delete'    : 'NETS_DELETE',
				'menu_name'     : _('Mailing Settings'),
				'show_in_menu'  : 'admin',
				'menu_order'    : 30,
				'menu_main'     : False,
				'default_sort'  : ({ 'property': 'user', 'direction': 'ASC' },),
				'grid_view'     : (
					'user', 'issubscribed'
				),
				'form_view'     : (
					'user', 'issubscribed'
				),
				'easy_search'   : ('user'),
				'detail_pane'   : ('netprofile_core.views', 'dpane_simple'),
				'create_wizard' : SimpleWizard(title=_('Add new user subscription'))
			}
		}
	)
	id = Column(
		'id',
		UInt32(),
		Comment('Setting ID'),
		primary_key=True,
		nullable=False,
		info={
			'header_string' : _('ID')
		}
	)
	
	userid = Column(
		'userid',
		UInt32(),
		ForeignKey('entities_access.entityid', name='mailing_settings_fk_userid', ondelete='CASCADE', onupdate='CASCADE'),
		Comment('Access Entity ID'),
		nullable=False,
		info={
			'header_string' : _('User ID')
		}
	)
	issubscribed = Column(
		'issubscribed',
		NPBoolean(),
		Comment('Is letter read?'),
		nullable=False,
		default=True,
		server_default=npbool(True),
		info={
			'header_string' : _('Is user subscripted?')
		}
	)
	user = relationship(
		'AccessEntity',
		backref='subscription_entities',
		primaryjoin='MailingSubscription.userid == AccessEntity.id'
	)

