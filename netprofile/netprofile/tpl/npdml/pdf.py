#!/usr/bin/env python
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-
#
# NetProfile: NPDML parser - PDF output
# © Copyright 2017 Alex 'Unik' Unigovsky
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

import io
import re

from netprofile import PY3
if PY3:
	from html import escape as html_escape
else:
	from cgi import escape as html_escape

from reportlab.platypus import (
	Indenter,
	NextPageTemplate,
	PageBreak,
	Paragraph,
	Spacer,
	Table,
	TableStyle
)
from reportlab.lib.units import (
	cm, mm,
	inch, pica
)

from netprofile.pdf import (
	DefaultDocTemplate,
	DefaultTableStyle
)
from netprofile.tpl.npdml import *

_re_units = re.compile(r'^(\d*(?:\.\d+)?)\s*(pt|in|inch|mm|cm|pc|pica|px)?$')

def _conv_length(length_str):
	if length_str is None:
		return None
	m = _re_units.match(length_str)
	if m is None:
		return None
	amount = float(m.group(1))
	unit = m.group(2)
	if unit in ('in', 'inch'):
		amount *= inch
	elif unit == 'mm':
		amount *= mm
	elif unit == 'cm':
		amount *= cm
	elif unit in ('pc', 'pica'):
		amount *= pica
	elif unit == 'px':
		# We use conventional DPI of 96
		amount *= 0.75
	return amount

def _attr_str(attrs):
	return ' '.join(('%s="%s"' % (k, html_escape(v))) for k, v in attrs.items())

class NPDMLTableStyle(TableStyle):
	pass

class NPDMLDocTemplate(DefaultDocTemplate):
	pass

class PDFParseTarget(NPDMLParseTarget):
	def __init__(self, req, buf=None, pagesize='a4', orientation='portrait'):
		super(PDFParseTarget, self).__init__()
		self.req = req
		if buf is None:
			buf = io.BytesIO()
		self.buf = buf
		self.story = []
		self._pagesz = pagesize
		self._orient = orientation
		self._doc = None
		self._title = None
		self._first_page_tpl = None

	@property
	def doc(self):
		if self._doc is None:
			# FIXME: unhardcode margins
			self._doc = NPDMLDocTemplate(
				self.buf,
				request=self.req,
				pagesize=self._pagesz,
				orientation=self._orient,
				topMargin=2.0 * cm,
				leftMargin=1.8 * cm,
				rightMargin=1.8 * cm,
				bottomMargin=2.0 * cm,
				title=self._title
			)
			if self._first_page_tpl:
				for idx, ptpl in enumerate(self._doc.pageTemplates):
					if ptpl.id == self._first_page_tpl:
						self._doc._firstPageTemplateIndex = idx
		return self._doc

	def start(self, tag, attrs):
		# Need to get parent before inserting context.
		parent = self.parent
		curctx = super(PDFParseTarget, self).start(tag, attrs)
		ss = self.req.pdf_styles

		if isinstance(curctx, NPDMLBlock) and isinstance(parent, NPDMLBlock) and parent.data:
			para = Paragraph(parent.get_data(), ss['body'])
			self.story.append(para)
			parent.data = []

		if isinstance(curctx, NPDMLPageContext):
			tpl = ['default']
			if 'template' in curctx:
				tpl = curctx['template']
				if ',' in tpl:
					tpl = tpl.split(',')
				else:
					tpl = [tpl]
			self.story.append(NextPageTemplate(*tpl))
			if self._first_page_tpl is None:
				self._first_page_tpl = tpl[0]
			else:
				self.story.append(PageBreak())

	def end(self, tag):
		curctx = super(PDFParseTarget, self).end(tag)
		parent = self.parent
		ss = self.req.pdf_styles

		if isinstance(curctx, NPDMLParagraphContext):
			para = Paragraph(curctx.get_data(), ss['body'])
			self.story.append(para)
		elif isinstance(curctx, NPDMLTableCellContext):
			para_style = 'body'
			if isinstance(parent, NPDMLTableHeaderContext):
				para_style = 'table_header'
				if 'width' in curctx:
					parent.widths.append(_conv_length(curctx['width']))
				else:
					parent.widths.append(None)
			para = Paragraph(curctx.get_data(), ss[para_style])
			parent.cells.append(para)
		elif isinstance(curctx, NPDMLTableRowContext):
			parent.rows.append(curctx.cells)
			if isinstance(curctx, NPDMLTableHeaderContext) and curctx.widths:
				parent.widths = curctx.widths
		elif isinstance(curctx, NPDMLTableContext):
			# FIXME: unhardcode spacing
			kwargs = {
				'colWidths'   : curctx.widths,
				'spaceBefore' : 8
			}
			if 'repeatRows' in curctx:
				try:
					kwargs['repeatRows'] = int(curctx['repeatRows'])
				except (TypeError, ValueError):
					pass
			if 'align' in curctx:
				value = curctx['align'].upper()
				if value in ('LEFT', 'RIGHT', 'CENTER'):
					kwargs['hAlign'] = value
			table = Table(curctx.rows, **kwargs)
			# FIXME: create table style instead of using default one
			table.setStyle(DefaultTableStyle())
			self.story.append(table)
		elif isinstance(curctx, NPDMLAnchorContext):
			markup = '<a %s>%s</a>' % (_attr_str(curctx), curctx.get_data())
			parent.data.append(markup)
		elif isinstance(curctx, NPDMLBoldContext):
			markup = '<b>%s</b>' % (curctx.get_data(),)
			parent.data.append(markup)
		elif isinstance(curctx, NPDMLItalicContext):
			markup = '<i>%s</i>' % (curctx.get_data(),)
			parent.data.append(markup)
		elif isinstance(curctx, NPDMLUnderlineContext):
			markup = '<u>%s</u>' % (curctx.get_data(),)
			parent.data.append(markup)
		elif isinstance(curctx, NPDMLStrikethroughContext):
			markup = '<strike>%s</strike>' % (curctx.get_data(),)
			parent.data.append(markup)
		elif isinstance(curctx, NPDMLSuperscriptContext):
			markup = '<super>%s</super>' % (curctx.get_data(),)
			parent.data.append(markup)
		elif isinstance(curctx, NPDMLSubscriptContext):
			markup = '<sub>%s</sub>' % (curctx.get_data(),)
			parent.data.append(markup)
		elif isinstance(curctx, NPDMLFontContext):
			kwargs = {}
			for attr in ('name', 'size', 'color'):
				if attr in curctx:
					kwargs[attr] = curctx[attr]
			if len(kwargs):
				markup = '<font %s>%s</font>' % (_attr_str(kwargs), curctx.get_data())
				parent.data.append(markup)
			else:
				parent.data.append(curctx.get_data())
		elif isinstance(curctx, NPDMLTitleContext):
			# FIXME: draw actual title
			self._title = curctx.get_data()

	def data(self, data):
		self.parent.data.append(html_escape(data))

	def close(self):
		self.doc.build(self.story)
		self.buf.seek(0)
		return self.buf

