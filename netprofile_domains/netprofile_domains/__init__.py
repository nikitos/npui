from __future__ import (
	unicode_literals,
	print_function,
	absolute_import,
	division
)

from netprofile.common.modules import ModuleBase
from .models import *

from pyramid.i18n import TranslationStringFactory

_ = TranslationStringFactory('netprofile_domains')

class Module(ModuleBase):
	def __init__(self, mmgr):
		self.mmgr = mmgr
		mmgr.cfg.add_translation_dirs('netprofile_domains:locale/')
		mmgr.cfg.scan()

	def get_models(self):
		return [
			Domain,
			DomainAlias,
			DomainTXTRecord,
			DomainHostLinkageType
		]

	@property
	def name(self):
		return _('Domains')
