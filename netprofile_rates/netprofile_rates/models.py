#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# NetProfile: Rates module - Models
# Copyright © 2013-2016 Alex Unigovsky
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

from __future__ import (unicode_literals, print_function,
                        absolute_import, division)

__all__ = [
    'BillingPeriod',
    'Destination',
    'DestinationSet',
    'EntityTypeRateClass',
    'Filter',
    'FilterSet',
    'GlobalRateModifier',
    'Rate',
    'RateClass',
    'RateModifierType',

    'AcctRateDestProcedure',
    'AcctRateFilterProcedure',
    'AcctRatePercentRemainingFunction',
    'AcctRatePercentSpentFunction',
    'AcctRateQPCountFunction',
    'AcctRateQPLengthFunction',
    'AcctRateQPNewFunction',
    'AcctRateQPSpentFunction'
]

from sqlalchemy import (
    Column,
    DateTime,
    FetchedValue,
    ForeignKey,
    Index,
    Sequence,
    TIMESTAMP,
    Unicode,
    UnicodeText,
    text
)
from sqlalchemy.orm import (
    backref,
    relationship
)
from sqlalchemy.ext.associationproxy import association_proxy
from pyramid.i18n import TranslationStringFactory

from netprofile.common.locale import money_format
from netprofile.db.connection import Base
from netprofile.db.fields import (
    ASCIIString,
    DeclEnum,
    Int32,
    Money,
    NPBoolean,
    PercentFraction,
    Traffic,
    UInt8,
    UInt16,
    UInt32,
    npbool
)
from netprofile.db.ddl import (
    Comment,
    InArgument,
    InOutArgument,
    OutArgument,
    SQLFunction,
    SQLFunctionArgument,
    Trigger
)
from netprofile.ext.wizards import SimpleWizard

_ = TranslationStringFactory('netprofile_rates')


class RateType(DeclEnum):
    """
    Enumeration of available values for rate types.
    """
    prepaid = 'prepaid', _('Prepaid'), 10
    prepaid_cont = 'prepaid_cont', _('Continuous Prepaid'), 20
    postpaid = 'postpaid', _('Postpaid'), 30
    free = 'free', _('Free'), 40


class QuotaPeriodUnit(DeclEnum):
    """
    Enumeration of available values for quota period unit.
    """
    absolute_hour = 'a_hour', _('Hour (abs.)'), 10
    absolute_day = 'a_day', _('Day (abs.)'), 20
    absolute_week = 'a_week', _('Week (abs.)'), 30
    absolute_month = 'a_month', _('Month (abs.)'), 40
    absolute_year = 'a_year', _('Year (abs.)'), 50
    calendar_hour = 'c_hour', _('Hour (cal.)'), 60
    calendar_day = 'c_day', _('Day (cal.)'), 70
    calendar_month = 'c_month', _('Month (cal.)'), 80
    calendar_year = 'c_year', _('Year (cal.)'), 90
    fixed_hour = 'f_hour', _('Hour (fix.)'), 100
    fixed_day = 'f_day', _('Day (fix.)'), 110
    fixed_week = 'f_week', _('Week (fix.)'), 120
    fixed_month = 'f_month', _('Month (fix.)'), 130
    fixed_year = 'f_year', _('Year (fix.)'), 140


class DestinationType(DeclEnum):
    """
    Enumeration of available values for destination types.
    """
    normal = 'normal', _('Normal'), 10
    no_quota = 'noquota', _('No Quota'), 20
    only_quota = 'onlyquota', _('Only Quota'), 30
    reject = 'reject', _('Reject'), 40


class DestinationMatchType(DeclEnum):
    """
    Enumeration of available values for destination match types.
    """
    exact = 'exact', _('Exact Match'), 10
    prefix = 'prefix', _('Prefix Match'), 20
    suffix = 'suffix', _('Suffix Match'), 30
    regex = 'regex', _('Regular Expression'), 40


# Taken from http://www.iana.org/assignments/radius-types/radius-types.xhtml
# Section: "Values for RADIUS Attribute 61, NAS-Port-Type"
_radattr_nas_port_type = {
    0:  'Async',
    1:  'Sync',
    2:  'ISDN Sync',
    3:  'ISDN Async V.120',
    4:  'ISDN Async V.110',
    5:  'Virtual - VPN/tunnel',
    6:  'PIAFS',
    7:  'HDLC Clear Channel',
    8:  'X.25',
    9:  'X.75',
    10: 'G.3 Fax',
    11: 'SDSL - Symmetric DSL',
    12: 'ADSL-CAP - ADSL, CAP mod.',
    13: 'ADSL-DMT - ADSL, DMT mod.',
    14: 'IDSL - ISDN Digital Subscriber Line',
    15: 'Ethernet',
    16: 'xDSL - Unspecified DSL',
    17: 'Cable',
    18: 'Wireless - Other',
    19: 'Wireless - IEEE 802.11',
    20: 'Token-Ring',
    21: 'FDDI',
    22: 'Wireless - CDMA2000',
    23: 'Wireless - UMTS',
    24: 'Wireless - 1X-EV',
    25: 'IAPP',
    26: 'FTTP - Fiber To The Premises',
    27: 'Wireless - IEEE 802.16',
    28: 'Wireless - IEEE 802.20',
    29: 'Wireless - IEEE 802.22',
    30: 'PPPoA - PPP over ATM',
    31: 'PPPoEoA - PPPoE over ATM',
    32: 'PPPoEoE - PPPoE over Ethernet',
    33: 'PPPoEoVLAN - PPPoE over VLAN',
    34: 'PPPoEoQinQ - PPPoE over IEEE 802.1QinQ',
    35: 'xPON - Passive Optical Network',
    36: 'Wireless - XGP',
    37: 'WiMAX Pre-Release 8 IWK function',
    38: 'WIMAX-WIFI-IWK: WiMAX WiFi Interworking',
    39: 'WIMAX-SFF: Signal Forward for LTE/3GPP2',
    40: 'WIMAX-HA-LMA: WiMAX HA/LMA function',
    41: 'WIMAX-DHCP: WiMAX DCHP service',
    42: 'WIMAX-LBS: WiMAX location based service',
    43: 'WIMAX-WVS: WiMAX voice service'
}
# Section: "Values for RADIUS Attribute 6, Service-Type"
_radattr_service_type = {
    1:  'Login',
    2:  'Framed',
    3:  'Callback Login',
    4:  'Callback Framed',
    5:  'Outbound',
    6:  'Administrative',
    7:  'NAS Prompt',
    8:  'Authenticate Only',
    9:  'Callback NAS Prompt',
    10: 'Call Check',
    11: 'Callback Administrative',
    12: 'Voice',
    13: 'Fax',
    14: 'Modem Relay',
    15: 'IAPP-Register',
    16: 'IAPP-AP-Check',
    17: 'Authorize Only',
    18: 'Framed-Management',
    19: 'Additional-Authorization'
}
# Section: "Values for RADIUS Attribute 7, Framed-Protocol"
# Note: values 9, 1008 are not assigned by IANA
_radattr_framed_protocol = {
    1:    'PPP',
    2:    'SLIP',
    3:    'ARAP',
    4:    'Gandalf SingleLink/MultiLink',
    5:    'Xylogics IPX/SLIP',
    6:    'X.75 Synchronous',
    7:    'GPRS PDP Context',
    9:    'PPTP (non-standard)',
    1008: 'Dynamic ATM (non-standard)'
}
# Section: "Values for RADIUS Attribute 64, Tunnel-Type"
_radattr_tunnel_type = {
    1:  'PPTP',
    2:  'L2F',
    3:  'L2TP',
    4:  'ATMP',
    5:  'VTP',
    6:  'IPsec AH tunnel mode',
    7:  'IP-IP encapsulation',
    8:  'Minimal IP-IP encapsulation',
    9:  'IPsec ESP tunnel mode',
    10: 'GRE',
    11: 'Bay DVS',
    12: 'IP-in-IP tunneling',
    13: 'VLAN'
}
# Section "Values for RADIUS Attribute 65, Tunnel-Medium-Type"
_radattr_tunnel_medium_type = {
    1:  'IPv4',
    2:  'IPv6',
    3:  'NSAP',
    4:  'HDLC',
    5:  'BBN 1822',
    6:  'IEEE 802 - all types',
    7:  'E.163 - POTS',
    8:  'E.164 - SMDS, Frame Relay, ATM',
    9:  'F.69 - Telex',
    10: 'X.121 - X.25, Frame Relay',
    11: 'IPX',
    12: 'AppleTalk',
    13: 'Decnet IV',
    14: 'Banyan Vines',
    15: 'E.164 + NSAP subaddress'
}


class BillingPeriod(Base):
    """
    Billing Periods definition
    """
    __tablename__ = 'bperiods_def'
    __table_args__ = (
        Comment('Billing periods'),
        Index('bperiods_def_u_name', 'name', unique=True),
        Index('bperiods_def_i_month', 'start_month', 'end_month'),
        Index('bperiods_def_i_mday', 'start_mday', 'end_mday'),
        Index('bperiods_def_i_wday', 'start_wday', 'end_wday'),
        Index('bperiods_def_i_hour', 'start_hour', 'end_hour'),
        Index('bperiods_def_i_minute', 'start_minute', 'end_minute'),
        {
            'mysql_engine':  'InnoDB',
            'mysql_charset': 'utf8',
            'info':          {
                'cap_menu':      'BASE_RATES',
                'cap_read':      'RATES_LIST',
                'cap_create':    'RATES_EDIT',
                'cap_edit':      'RATES_EDIT',
                'cap_delete':    'RATES_EDIT',

                'menu_name':     _('Billing Periods'),
                'show_in_menu':  'modules',
                'default_sort':  ({'property': 'name', 'direction': 'ASC'},),
                'grid_view':     ('bperiodid', 'name'),
                'grid_hidden':   ('bperiodid',),
                'form_view':     ('name',
                                  'start_month', 'start_mday', 'start_wday',
                                  'start_hour', 'start_minute',
                                  'end_month', 'end_mday', 'end_wday',
                                  'end_hour', 'end_minute'),
                'easy_search':   ('name',),
                'detail_pane':   ('netprofile_core.views', 'dpane_simple'),
                'create_wizard': SimpleWizard(
                                    title=_('Add new billing period'))
            }
        })
    id = Column(
        'bperiodid',
        UInt32(),
        Sequence('bperiods_def_bperiodid_seq'),
        Comment('Billing period ID'),
        primary_key=True,
        nullable=False,
        info={
            'header_string': _('ID')
        })
    name = Column(
        Unicode(255),
        Comment('Billing period name'),
        nullable=False,
        info={
            'header_string': _('Name'),
            'column_flex': 1
        })
    start_month = Column(
        UInt8(),
        Comment('Start month'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string': _('Start Month')
        })
    start_day_of_month = Column(
        'start_mday',
        UInt8(),
        Comment('Start day of month'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string': _('Start Day of Month')
        })
    start_weekday = Column(
        'start_wday',
        UInt8(),
        Comment('Start day of week'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string': _('Start Day of Week')
        })
    start_hour = Column(
        UInt8(),
        Comment('Start hour'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string': _('Start Hour')
        })
    start_minute = Column(
        UInt8(),
        Comment('Start minute'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string': _('Start Minute')
        })
    end_month = Column(
        UInt8(),
        Comment('End month'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string': _('End Month')
        })
    end_day_of_month = Column(
        'end_mday',
        UInt8(),
        Comment('End day of month'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string': _('End Day of Month')
        })
    end_weekday = Column(
        'end_wday',
        UInt8(),
        Comment('End day of week'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string': _('End Day of Week')
        })
    end_hour = Column(
        UInt8(),
        Comment('End hour'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string': _('End Hour')
        })
    end_minute = Column(
        UInt8(),
        Comment('End minute'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string': _('End Minute')
        })

    def __str__(self):
        return str(self.name)


class DestinationSet(Base):
    """
    Accounting destination set definition
    """
    __tablename__ = 'dest_sets'
    __table_args__ = (
        Comment('Accounting destination sets'),
        Index('dest_sets_u_name', 'name', unique=True),
        {
            'mysql_engine':  'InnoDB',
            'mysql_charset': 'utf8',
            'info':          {
                'cap_menu':      'BASE_RATES',
                'cap_read':      'RATES_LIST',
                'cap_create':    'RATES_DS_CREATE',
                'cap_edit':      'RATES_DS_EDIT',
                'cap_delete':    'RATES_DS_DELETE',

                'menu_name':     _('Destination Sets'),
                'show_in_menu':  'modules',
                'default_sort':  ({'property': 'name', 'direction': 'ASC'},),
                'grid_view':     ('dsid', 'name'),
                'grid_hidden':   ('dsid',),
                'easy_search':   ('name',),
                'detail_pane':   ('netprofile_core.views', 'dpane_simple'),
                'create_wizard': SimpleWizard(title=_(
                                    'Add new accounting destination set'))
            }
        })
    id = Column(
        'dsid',
        UInt32(),
        Sequence('dest_sets_dsid_seq'),
        Comment('Destination set ID'),
        primary_key=True,
        nullable=False,
        info={
            'header_string': _('ID')
        })
    name = Column(
        Unicode(255),
        Comment('Destination set name'),
        nullable=False,
        info={
            'header_string': _('Name'),
            'column_flex': 1
        })

    destinations = relationship(
        'Destination',
        backref=backref('set', innerjoin=True),
        cascade='all, delete-orphan',
        passive_deletes=True)

    def __str__(self):
        return str(self.name)


class Destination(Base):
    """
    Accounting destination definition
    """
    __tablename__ = 'dest_def'
    __table_args__ = (
        Comment('Accounting destinations'),
        Index('dest_def_i_dsid', 'dsid'),
        Index('dest_def_i_active', 'active'),
        Index('dest_def_i_l_ord', 'l_ord'),
        {
            'mysql_engine':  'InnoDB',
            'mysql_charset': 'utf8',
            'info':          {
                'cap_menu':      'BASE_RATES',
                'cap_read':      'RATES_LIST',
                'cap_create':    'RATES_DS_EDIT',
                'cap_edit':      'RATES_DS_EDIT',
                'cap_delete':    'RATES_DS_EDIT',

                'menu_name':     _('Destinations'),
                'default_sort':  ({'property': 'l_ord', 'direction': 'ASC'},),
                'grid_view':     ('destid', 'set', 'name', 'type',
                                  'mt', 'match', 'l_ord', 'active'),
                'grid_hidden':   ('destid',),
                'form_view':     ('set', 'name', 'type',
                                  'active', 'l_ord',
                                  'mt', 'match',
                                  'oqsum_sec', 'oqmul_sec',
                                  'cb_acct'),
                'easy_search':   ('name', 'match'),
                'detail_pane':   ('netprofile_core.views', 'dpane_simple'),
                'create_wizard': SimpleWizard(title=_('Add new destination'))
            }
        })
    id = Column(
        'destid',
        UInt32(),
        Sequence('dest_def_destid_seq'),
        Comment('Destination ID'),
        primary_key=True,
        nullable=False,
        info={
            'header_string': _('ID')
        })
    type = Column(
        DestinationType.db_type(),
        Comment('Destination type'),
        nullable=False,
        default=DestinationType.normal,
        server_default=DestinationType.normal,
        info={
            'header_string': _('Type'),
            'column_flex': 1
        })
    match_type = Column(
        'mt',
        DestinationMatchType.db_type(),
        Comment('Destination match type'),
        nullable=False,
        default=DestinationMatchType.prefix,
        server_default=DestinationMatchType.prefix,
        info={
            'header_string': _('Match Type'),
            'column_flex': 1
        })
    set_id = Column(
        'dsid',
        UInt32(),
        Comment('Destination set ID'),
        ForeignKey('dest_sets.dsid', name='dest_def_fk_dsid',
                   ondelete='CASCADE', onupdate='CASCADE'),
        nullable=False,
        info={
            'header_string': _('Set'),
            'filter_type': 'nplist',
            'column_flex': 2
        })
    name = Column(
        Unicode(255),
        Comment('Destination name'),
        nullable=False,
        info={
            'header_string': _('Name'),
            'column_flex': 3
        })
    active = Column(
        NPBoolean(),
        Comment('Is destination active?'),
        nullable=False,
        default=True,
        server_default=npbool(True),
        info={
            'header_string': _('Active')
        })
    lookup_order = Column(
        'l_ord',
        UInt16(),
        Comment('Lookup order'),
        nullable=False,
        default=1000,
        server_default=text('1000'),
        info={
            'header_string': _('Lookup Order')
        })
    match_string = Column(
        'match',
        ASCIIString(255),
        Comment('Match expression'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string': _('Match String')
        })
    overquota_sum_seconds = Column(
        'oqsum_sec',
        Money(),
        Comment('Over quota per second override'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string': _('O/Q per Second Override')
        })
    overquota_multiplier_seconds = Column(
        'oqmul_sec',
        Money(),
        Comment('Over quota per second multiplier'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string': _('O/Q per Second Multiplier')
        })
    cb_acct = Column(
        ASCIIString(255),
        Comment('Callback on accounting'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string': _('Accounting Callback')
        })

    def __str__(self):
        return str(self.name)


class FilterSet(Base):
    """
    Accounting filter set definition
    """
    __tablename__ = 'filters_sets'
    __table_args__ = (
        Comment('Accounting filter sets'),
        Index('filters_sets_u_name', 'name', unique=True),
        {
            'mysql_engine':  'InnoDB',
            'mysql_charset': 'utf8',
            'info':          {
                'cap_menu':      'BASE_RATES',
                'cap_read':      'RATES_LIST',
                'cap_create':    'RATES_FS_CREATE',
                'cap_edit':      'RATES_FS_EDIT',
                'cap_delete':    'RATES_FS_DELETE',

                'menu_name':     _('Filter Sets'),
                'show_in_menu':  'modules',
                'default_sort':  ({'property': 'name', 'direction': 'ASC'},),
                'grid_view':     ('fsid', 'name'),
                'grid_hidden':   ('fsid',),
                'easy_search':   ('name',),
                'detail_pane':   ('netprofile_core.views', 'dpane_simple'),
                'create_wizard': SimpleWizard(
                                    title=_('Add new accounting filter set'))
            }
        })
    id = Column(
        'fsid',
        UInt32(),
        Sequence('filters_sets_fsid_seq'),
        Comment('Filter set ID'),
        primary_key=True,
        nullable=False,
        info={
            'header_string': _('ID')
        })
    name = Column(
        Unicode(255),
        Comment('Filter set name'),
        nullable=False,
        info={
            'header_string': _('Name'),
            'column_flex': 1
        })

    filters = relationship(
        'Filter',
        backref=backref('set', innerjoin=True),
        cascade='all, delete-orphan',
        passive_deletes=True)

    def __str__(self):
        return str(self.name)


class Filter(Base):
    """
    Accounting filter definition
    """
    __tablename__ = 'filters_def'
    __table_args__ = (
        Comment('Accounting filters'),
        Index('filters_def_i_fsid', 'fsid'),
        {
            'mysql_engine':  'InnoDB',
            'mysql_charset': 'utf8',
            'info':          {
                'cap_menu':      'BASE_RATES',
                'cap_read':      'RATES_LIST',
                'cap_create':    'RATES_FS_EDIT',
                'cap_edit':      'RATES_FS_EDIT',
                'cap_delete':    'RATES_FS_EDIT',

                'menu_name':     _('Filters'),
                'grid_view':     ('fid', 'set', 'porttype', 'servicetype',
                                  'frproto', 'tuntype', 'tunmedium'),
                'grid_hidden':   ('fid',),
                'detail_pane':   ('netprofile_core.views', 'dpane_simple'),
                'create_wizard': SimpleWizard(title=_('Add new filter'))
            }
        })
    id = Column(
        'fid',
        UInt32(),
        Sequence('filters_def_fid_seq'),
        Comment('Filter ID'),
        primary_key=True,
        nullable=False,
        info={
            'header_string': _('ID')
        })
    set_id = Column(
        'fsid',
        UInt32(),
        Comment('Filter set ID'),
        ForeignKey('filters_sets.fsid', name='filters_def_fk_fsid',
                   ondelete='CASCADE', onupdate='CASCADE'),
        nullable=False,
        info={
            'header_string': _('Set'),
            'filter_type': 'nplist',
            'column_flex': 3
        })
    nas_port_type = Column(
        'porttype',
        UInt32(),
        Comment('Required NAS-Port-Type'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string': 'NAS-Port-Type',
            'choices': _radattr_nas_port_type,
            'column_flex': 1
        })
    service_type = Column(
        'servicetype',
        UInt32(),
        Comment('Required Service-Type'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string': 'Service-Type',
            'choices': _radattr_service_type,
            'column_flex': 1
        })
    framed_protocol = Column(
        'frproto',
        UInt32(),
        Comment('Required Framed-Protocol'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string': 'Framed-Protocol',
            'choices': _radattr_framed_protocol,
            'column_flex': 1
        })
    tunnel_type = Column(
        'tuntype',
        UInt32(),
        Comment('Required Tunnel-Type'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string': 'Tunnel-Type',
            'choices': _radattr_tunnel_type,
            'column_flex': 1
        })
    tunnel_medium_type = Column(
        'tunmedium',
        UInt32(),
        Comment('Required Tunnel-Medium-Type'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string': 'Tunnel-Medium-Type',
            'choices': _radattr_tunnel_medium_type,
            'column_flex': 1
        })

    def __str__(self):
        loc = str
        req = getattr(self, '__req__', None)
        if req:
            loc = req.localizer.translate
        return loc(_('Filter #%d')) % (self.id,)


class Rate(Base):
    """
    Payment rate definition
    """
    __tablename__ = 'rates_def'
    __table_args__ = (
        Comment('Payment rates'),
        Index('rates_def_u_name', 'name', unique=True),
        Index('rates_def_i_polled', 'polled'),
        Index('rates_def_i_rcid', 'rcid'),
        Index('rates_def_i_poolid', 'poolid'),
        Index('rates_def_i_dsid', 'dsid'),
        Index('rates_def_i_fsid', 'fsid'),
        Trigger('after', 'insert', 't_rates_def_ai'),
        Trigger('after', 'update', 't_rates_def_au'),
        Trigger('after', 'delete', 't_rates_def_ad'),
        {
            'mysql_engine':  'InnoDB',
            'mysql_charset': 'utf8',
            'info':          {
                'cap_menu':      'BASE_RATES',
                'cap_read':      'RATES_LIST',
                'cap_create':    'RATES_CREATE',
                'cap_edit':      'RATES_EDIT',
                'cap_delete':    'RATES_DELETE',

                'menu_name':     _('Payment Rates'),
                'show_in_menu':  'modules',
                'menu_main':     True,
                'default_sort':  ({'property': 'name', 'direction': 'ASC'},),
                'grid_view':     ('rateid', 'name', 'class', 'type',
                                  'qp_amount', 'qp_unit', 'qsum'),
                'grid_hidden':   ('rateid',),
                'form_view':     ('name', 'class', 'type',
                                  'polled', 'abf', 'usersel',
                                  'pool', 'destination_set', 'filter_set',
                                  'qp_amount', 'qp_unit',
                                  'qsum', 'auxsum',
                                  'qt_ingress', 'qt_egress', 'qsec',
                                  'oq_ingress', 'oq_egress',
                                  'oqsum_ingress', 'oqsum_egress', 'oqsum_sec',
                                  'sim',
                                  'pol_ingress', 'pol_egress',
                                  'block_timeframe',
                                  'cb_qsum_before',
                                  'cb_qsum_success', 'cb_qsum_failure',
                                  'cb_after_connect', 'cb_after_disconnect',
                                  'descr'),
                'easy_search':   ('name',),
                'extra_data':    ('formatted_quota_sum',
                                  'formatted_auxiliary_sum'),
                'detail_pane':   ('netprofile_core.views', 'dpane_simple'),
                'create_wizard': SimpleWizard(title=_('Add new payment rate'))
            }
        })
    id = Column(
        'rateid',
        UInt32(),
        Sequence('rates_def_rateid_seq'),
        Comment('Rate ID'),
        primary_key=True,
        nullable=False,
        info={
            'header_string': _('ID')
        })
    type = Column(
        RateType.db_type(),
        Comment('Rate usage type'),
        nullable=False,
        default=RateType.prepaid,
        server_default=RateType.prepaid,
        info={
            'header_string': _('Type')
        })
    name = Column(
        Unicode(255),
        Comment('Rate name'),
        nullable=False,
        info={
            'header_string': _('Name'),
            'column_flex': 3
        })
    polled = Column(
        NPBoolean(),
        Comment('Is periodically polled?'),
        nullable=False,
        default=False,
        server_default=npbool(False),
        info={
            'header_string': _('Periodically Polled')
        })
    advanced_features = Column(
        'abf',
        NPBoolean(),
        Comment('Use advanced billing features'),
        nullable=False,
        default=False,
        server_default=npbool(False),
        info={
            'header_string': _('Advanced')
        })
    user_selectable = Column(
        'usersel',
        NPBoolean(),
        Comment('Is user-selectable?'),
        nullable=False,
        default=False,
        server_default=npbool(False),
        info={
            'header_string': _('User-selectable')
        })
    allow_overquota_ingress = Column(
        'oq_ingress',
        NPBoolean(),
        Comment('Allow going over quota on ingress traffic?'),
        nullable=False,
        default=True,
        server_default=npbool(True),
        info={
            'header_string': _('Allow Ingress O/Q')
        })
    allow_overquota_egress = Column(
        'oq_egress',
        NPBoolean(),
        Comment('Allow going over quota on egress traffic?'),
        nullable=False,
        default=True,
        server_default=npbool(True),
        info={
            'header_string': _('Allow Egress O/Q')
        })
    class_id = Column(
        'rcid',
        UInt32(),
        Comment('Rate class ID'),
        ForeignKey('rates_classes_def.rcid', name='rates_def_fk_rcid',
                   onupdate='CASCADE'),
        nullable=False,
        default=1,
        server_default=text('1'),
        info={
            'header_string': _('Class'),
            'filter_type': 'nplist',
            'column_flex': 2
        })
    pool_id = Column(
        'poolid',
        UInt32(),
        ForeignKey('ippool_def.poolid', name='rates_def_fk_poolid',
                   ondelete='SET NULL', onupdate='CASCADE'),
        Comment('IP address pool ID'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string': _('IP Address Pool'),
            'filter_type': 'nplist'
        })
    destination_set_id = Column(
        'dsid',
        UInt32(),
        ForeignKey('dest_sets.dsid', name='rates_def_fk_dsid',
                   ondelete='SET NULL', onupdate='CASCADE'),
        Comment('Accounting destination set ID'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string': _('Destination Set'),
            'filter_type': 'nplist'
        })
    filter_set_id = Column(
        'fsid',
        UInt32(),
        ForeignKey('filters_sets.fsid', name='rates_def_fk_fsid',
                   ondelete='SET NULL', onupdate='CASCADE'),
        Comment('Accounting filter set ID'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string': _('Filter Set'),
            'filter_type': 'nplist'
        })
    quota_period_amount = Column(
        'qp_amount',
        UInt16(),
        Comment('Quota period amount'),
        nullable=False,
        default=1,
        server_default=text('1'),
        info={
            'header_string': _('Quota Period Amount')
        })
    quota_period_unit = Column(
        'qp_unit',
        QuotaPeriodUnit.db_type(),
        Comment('Quota period unit'),
        nullable=False,
        default=QuotaPeriodUnit.calendar_month,
        server_default=QuotaPeriodUnit.calendar_month,
        info={
            'header_string': _('Quota Period Unit')
        })
    quota_sum = Column(
        'qsum',
        Money(),
        Comment('Quota sum'),
        nullable=False,
        default=0.0,
        server_default=text('0.0'),
        info={
            'header_string': _('Quota Sum'),
            'column_xtype': 'templatecolumn',
            'template': '{formatted_quota_sum}'
        })
    auxiliary_sum = Column(
        'auxsum',
        Money(),
        Comment('Auxiliary sum'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string': _('Auxiliary Sum'),
            'column_xtype': 'templatecolumn',
            'template': '{formatted_auxiliary_sum}'
        })
    quota_ingress_traffic = Column(
        'qt_ingress',
        Traffic(),
        Comment('Ingress traffic included in quota (in bytes)'),
        nullable=False,
        default=0,
        server_default=text('0'),
        info={
            'header_string': _('Ingress Traffic Quota')
        })
    quota_egress_traffic = Column(
        'qt_egress',
        Traffic(),
        Comment('Egress traffic included in quota (in bytes)'),
        nullable=False,
        default=0,
        server_default=text('0'),
        info={
            'header_string': _('Egress Traffic Quota')
        })
    quota_seconds = Column(
        'qsec',
        UInt32(),
        Comment('Session time included in quota (in seconds)'),
        nullable=False,
        default=0,
        server_default=text('0'),
        info={
            'header_string': _('Time Quota')
        })
    overquota_sum_ingress = Column(
        'oqsum_ingress',
        Money(),
        Comment('Over quota payment for ingress traffic (per byte)'),
        nullable=False,
        default=0.0,
        server_default=text('0.0'),
        info={
            'header_string': _('Payment for Over Quota Ingress')
        })
    overquota_sum_egress = Column(
        'oqsum_egress',
        Money(),
        Comment('Over quota payment for egress traffic (per byte)'),
        nullable=False,
        default=0.0,
        server_default=text('0.0'),
        info={
            'header_string': _('Payment for Over Quota Egress')
        })
    overquota_sum_seconds = Column(
        'oqsum_sec',
        Money(),
        Comment('Over quota payment for time (per second)'),
        nullable=False,
        default=0.0,
        server_default=text('0.0'),
        info={
            'header_string': _('Payment for Over Quota Seconds')
        })
    simultaneous = Column(
        'sim',
        UInt16(),
        Comment('Max. number of simultaneous sessions (per user)'),
        nullable=False,
        default=0,
        server_default=text('0'),
        info={
            'header_string': _('Max. Simultaneous')
        })
    ingress_policy = Column(
        'pol_ingress',
        ASCIIString(255),
        Comment('Ingress traffic policy'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string': _('Ingress Traffic Policy')
        })
    egress_policy = Column(
        'pol_egress',
        ASCIIString(255),
        Comment('Egress traffic policy'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string': _('Egress Traffic Policy')
        })
    block_timeframe = Column(
        UInt16(),
        Comment('Max continuous blocking time (in accounting periods)'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string': _('Max Continuous Blocking Time')
        })
    cb_qsum_before = Column(
        ASCIIString(255),
        Comment('Callback before quota payment'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string': _('Callback before quota payment')
        })
    cb_qsum_success = Column(
        ASCIIString(255),
        Comment('Callback on successful quota payment'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string': _('Callback on successful quota payment')
        })
    cb_qsum_failure = Column(
        ASCIIString(255),
        Comment('Callback on failed quota payment'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string': _('Callback on failed quota payment')
        })
    cb_after_connect = Column(
        ASCIIString(255),
        Comment('Callback after connecting'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string': _('Callback after connecting')
        })
    cb_after_disconnect = Column(
        ASCIIString(255),
        Comment('Callback after disconnecting'),
        nullable=True,
        server_default=text('NULL'),
        info={
            'header_string': _('Callback after disconnecting')
        })
    description = Column(
        'descr',
        UnicodeText(),
        Comment('Rate description'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string': _('Description')
        })

    pool = relationship(
        'IPPool',
        backref=backref('rates',
                        passive_deletes=True))
    destination_set = relationship(
        'DestinationSet',
        backref=backref('rates',
                        passive_deletes=True))
    filter_set = relationship(
        'FilterSet',
        backref=backref('rates',
                        passive_deletes=True))
    global_modmap = relationship(
        'GlobalRateModifier',
        backref=backref('rate', innerjoin=True),
        cascade='all, delete-orphan',
        passive_deletes=True)

    global_modifiers = association_proxy(
        'global_modmap',
        'type',
        creator=lambda v: GlobalRateModifier(type=v))

    def __str__(self):
        return str(self.name)

    def formatted_quota_sum(self, req):
        return money_format(req, self.quota_sum)

    def formatted_auxiliary_sum(self, req):
        return money_format(req, self.auxiliary_sum)


class RateClass(Base):
    """
    Rate Classes
    """
    __tablename__ = 'rates_classes_def'
    __table_args__ = (
        Comment('Rate classes'),
        Index('rates_classes_def_u_name', 'name', unique=True),
        {
            'mysql_engine':  'InnoDB',
            'mysql_charset': 'utf8',
            'info':          {
                'cap_menu':      'BASE_RATES',
                'cap_read':      'RATES_LIST',
                'cap_create':    'RATES_CLASSES_CREATE',
                'cap_edit':      'RATES_CLASSES_EDIT',
                'cap_delete':    'RATES_CLASSES_DELETE',

                'menu_name':     _('Classes'),
                'show_in_menu':  'modules',
                'default_sort':  ({'property': 'name', 'direction': 'ASC'},),
                'grid_view':     ('rcid', 'name'),
                'grid_hidden':   ('rcid',),
                'form_view':     ('name', 'descr'),
                'easy_search':   ('name',),
                'detail_pane':   ('netprofile_core.views', 'dpane_simple'),
                'create_wizard': SimpleWizard(title=_('Add new rate class'))
            }
        })
    id = Column(
        'rcid',
        UInt32(),
        Sequence('rates_classes_def_rcid_seq'),
        Comment('Rate class ID'),
        primary_key=True,
        nullable=False,
        info={
            'header_string': _('ID')
        })
    name = Column(
        Unicode(255),
        Comment('Rate class name'),
        nullable=False,
        info={
            'header_string': _('Name'),
            'column_flex': 1
        })
    description = Column(
        'descr',
        UnicodeText(),
        Comment('Rate class description'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string': _('Description')
        })

    rates = relationship(
        'Rate',
        backref=backref('class', innerjoin=True))
    etypemap = relationship(
        'EntityTypeRateClass',
        backref=backref('class', innerjoin=True),
        cascade='all, delete-orphan',
        passive_deletes=True)

    entity_types = association_proxy(
        'etypemap',
        'entity_type',
        creator=lambda v: EntityTypeRateClass(entity_type=v))

    def __str__(self):
        return str(self.name)


class EntityTypeRateClass(Base):
    """
    Rate class mapping to entity types
    """
    __tablename__ = 'rates_classes_etypes'
    __table_args__ = (
        Comment('Rate class mappings to entity types'),
        Index('rates_classes_etypes_u_mapping', 'rcid', 'etypeid',
              unique=True),
        Index('rates_classes_etypes_i_etypeid', 'etypeid'),
        {
            'mysql_engine':  'InnoDB',
            'mysql_charset': 'utf8',
            'info':          {
                'cap_menu':      'BASE_RATES',
                'cap_read':      'RATES_LIST',
                'cap_create':    'RATES_CLASSES_EDIT',
                'cap_edit':      'RATES_CLASSES_EDIT',
                'cap_delete':    'RATES_CLASSES_EDIT',

                'menu_name':     _('Entity Type Mappings'),
                'default_sort':  ({'property': 'etypeid',
                                   'direction': 'ASC'},),
                'grid_view':     ('rcmapid', 'class', 'entity_type'),
                'grid_hidden':   ('rcmapid',),
                'form_view':     ('class', 'entity_type'),
                'create_wizard': SimpleWizard(title=_('Add new mapping'))
            }
        })
    id = Column(
        'rcmapid',
        UInt32(),
        Sequence('rates_classes_etypes_rcmapid_seq'),
        Comment('Rate class to entity type mapping ID'),
        primary_key=True,
        nullable=False,
        info={
            'header_string': _('ID')
        })
    class_id = Column(
        'rcid',
        UInt32(),
        ForeignKey('rates_classes_def.rcid',
                   name='rates_classes_etypes_fk_rcid',
                   ondelete='CASCADE', onupdate='CASCADE'),
        Comment('Rate class ID'),
        nullable=False,
        info={
            'header_string': _('Class'),
            'column_flex': 1
        })
    entity_type_id = Column(
        'etypeid',
        UInt32(),
        ForeignKey('entities_types.etypeid',
                   name='rates_classes_etypes_fk_etypeid',
                   onupdate='CASCADE'),
        Comment('Entity type ID'),
        nullable=False,
        info={
            'header_string': _('Entity Type'),
            'column_flex': 1
        })

    entity_type = relationship(
        'EntityType',
        innerjoin=True,
        backref=backref('rate_classes',
                        passive_deletes='all'))


class RateModifierType(Base):
    """
    Rate modifier type definition
    """
    __tablename__ = 'rates_mods_types'
    __table_args__ = (
        Comment('Rate modifier types'),
        Index('rates_mods_types_u_name', 'name', unique=True),
        Index('rates_mods_types_i_bperiodid', 'bperiodid'),
        {
            'mysql_engine':  'InnoDB',
            'mysql_charset': 'utf8',
            'info':          {
                'cap_menu':      'BASE_RATES',
                'cap_read':      'RATES_LIST',
                'cap_create':    'RATES_CREATE',
                'cap_edit':      'RATES_EDIT',
                'cap_delete':    'RATES_DELETE',

                'menu_name':     _('Rate Modifiers'),
                'show_in_menu':  'modules',
                'default_sort':  ({'property': 'name', 'direction': 'ASC'},),
                'grid_view':     ('rmtid', 'name', 'enabled'),
                'grid_hidden':   ('rmtid',),
                'form_view':     ('name', 'enabled', 'descr',
                                  'billing_period',
                                  'oqsum_ingress_mul', 'oqsum_egress_mul',
                                  'oqsum_sec_mul',
                                  'ow_ingress', 'ow_egress',
                                  'pol_ingress', 'pol_egress'),
                'easy_search':   ('name',),
                'detail_pane':   ('netprofile_core.views', 'dpane_simple'),
                'create_wizard': SimpleWizard(title=_('Add new rate modifier'))
            }
        })
    id = Column(
        'rmtid',
        UInt32(),
        Sequence('rates_mods_types_rmtid_seq'),
        Comment('Rate modifier type ID'),
        primary_key=True,
        nullable=False,
        info={
            'header_string': _('ID')
        })
    name = Column(
        Unicode(255),
        Comment('Rate modifier type name'),
        nullable=False,
        info={
            'header_string': _('Name'),
            'column_flex': 1
        })
    enabled = Column(
        NPBoolean(),
        Comment('Is modifier type enabled?'),
        nullable=False,
        default=False,
        server_default=npbool(False),
        info={
            'header_string': _('Enabled')
        })
    billing_period_id = Column(
        'bperiodid',
        UInt32(),
        Comment('Billing period ID'),
        ForeignKey('bperiods_def.bperiodid',
                   name='rates_mods_types_fk_bperiodid',
                   onupdate='CASCADE'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string': _('Period'),
            'filter_type': 'nplist'
        })
    oq_sum_multiplier_ingress = Column(
        'oqsum_ingress_mul',
        Money(),
        Comment('Ingress overquota sum multiplier'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string': _('O/Q Sum Multiplier for Ingress')
        })
    oq_sum_multiplier_egress = Column(
        'oqsum_egress_mul',
        Money(),
        Comment('Egress overquota sum multiplier'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string': _('O/Q Sum Multiplier for Egress')
        })
    oq_sum_multiplier_seconds = Column(
        'oqsum_sec_mul',
        Money(),
        Comment('Per-second overquota sum multiplier'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string': _('O/Q Sum Multiplier for Seconds')
        })
    overwrite_ingress_policy = Column(
        'ow_ingress',
        NPBoolean(),
        Comment('Overwrite ingress policy?'),
        nullable=False,
        default=False,
        server_default=npbool(False),
        info={
            'header_string': _('Overwrite Ingress Policy')
        })
    overwrite_egress_policy = Column(
        'ow_egress',
        NPBoolean(),
        Comment('Overwrite egress policy?'),
        nullable=False,
        default=False,
        server_default=npbool(False),
        info={
            'header_string': _('Overwrite Egress Policy')
        })
    ingress_policy = Column(
        'pol_ingress',
        ASCIIString(255),
        Comment('Ingress traffic policy'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string': _('Ingress Traffic Policy')
        })
    egress_policy = Column(
        'pol_egress',
        ASCIIString(255),
        Comment('Egress traffic policy'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string': _('Egress Traffic Policy')
        })
    description = Column(
        'descr',
        UnicodeText(),
        Comment('Rate modifier description'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string': _('Description')
        })

    billing_period = relationship(
        'BillingPeriod',
        backref='rate_modifiers')
    global_modifiers = relationship(
        'GlobalRateModifier',
        backref=backref('type', innerjoin=True),
        cascade='all, delete-orphan',
        passive_deletes=True)

    def __str__(self):
        return str(self.name)


class GlobalRateModifier(Base):
    """
    Global rate modifier definition
    """
    __tablename__ = 'rates_mods_global'
    __table_args__ = (
        Comment('Global rate modifiers'),
        Index('rates_mods_global_u_mapping', 'rmtid', 'rateid', unique=True),
        Index('rates_mods_global_i_rateid', 'rateid'),
        Index('rates_mods_global_i_l_ord', 'l_ord'),
        Trigger('before', 'insert', 't_rates_mods_global_bi'),
        {
            'mysql_engine':  'InnoDB',
            'mysql_charset': 'utf8',
            'info':          {
                'cap_menu':      'BASE_RATES',
                'cap_read':      'RATES_LIST',
                'cap_create':    'RATES_EDIT',
                'cap_edit':      'RATES_EDIT',
                'cap_delete':    'RATES_EDIT',

                'menu_name':     _('Rate Modifiers'),
                'default_sort':  ({'property': 'l_ord', 'direction': 'ASC'},),
                'grid_view':     ('rmid', 'rate', 'type', 'enabled', 'l_ord'),
                'grid_hidden':   ('rmid',),
                'create_wizard': SimpleWizard(title=_('Add new rate modifier'))
            }
        })
    id = Column(
        'rmid',
        UInt32(),
        Sequence('rates_mods_global_rmid_seq'),
        Comment('Rate modifier ID'),
        primary_key=True,
        nullable=False,
        info={
            'header_string': _('ID')
        })
    type_id = Column(
        'rmtid',
        UInt32(),
        Comment('Rate modifier type ID'),
        ForeignKey('rates_mods_types.rmtid', name='rates_mods_global_fk_rmtid',
                   ondelete='CASCADE', onupdate='CASCADE'),
        nullable=False,
        info={
            'header_string': _('Type'),
            'filter_type': 'nplist',
            'column_flex': 1
        })
    rate_id = Column(
        'rateid',
        UInt32(),
        Comment('Rate ID'),
        ForeignKey('rates_def.rateid', name='rates_mods_global_fk_rateid',
                   ondelete='CASCADE', onupdate='CASCADE'),
        nullable=False,
        info={
            'header_string': _('Rate'),
            'filter_type': 'nplist',
            'column_flex': 1
        })
    creation_time = Column(
        'ctime',
        TIMESTAMP(),
        Comment('Creation timestamp'),
        nullable=True,
        default=None,
        server_default=FetchedValue(),
        info={
            'header_string': _('Created'),
            'read_only': True
        })
    enabled = Column(
        NPBoolean(),
        Comment('Is modifier enabled?'),
        nullable=False,
        default=False,
        server_default=npbool(False),
        info={
            'header_string': _('Enabled')
        })
    lookup_order = Column(
        'l_ord',
        UInt16(),
        Comment('Lookup order'),
        nullable=False,
        default=1000,
        server_default=text('1000'),
        info={
            'header_string': _('Lookup Order')
        })


AcctRateDestProcedure = SQLFunction(
    'acct_rate_dest',
    args=(InArgument('ts', DateTime()),
          InArgument('rateid', UInt32()),
          InArgument('dsid', UInt32()),
          InArgument('called', ASCIIString(255)),
          InOutArgument('destid', UInt32()),
          InOutArgument('dtype', DestinationType.db_type()),
          InOutArgument('oqsum_sec', Money())),
    comment='Search destination sets for a match',
    writes_sql=False,
    label='ardfunc',
    is_procedure=True)
AcctRateFilterProcedure = SQLFunction(
    'acct_rate_filter',
    args=(InArgument('fsid', UInt32()),
          InArgument('r_porttype', Int32()),
          InArgument('r_servicetype', Int32()),
          InArgument('r_frproto', Int32()),
          InArgument('r_tuntype', Int32()),
          InArgument('r_tunmedium', Int32()),
          OutArgument('filterid', UInt32())),
    comment='Search filter sets for a match',
    writes_sql=False,
    label='arffunc',
    is_procedure=True)
AcctRatePercentRemainingFunction = SQLFunction(
    'acct_rate_percent_remaining',
    args=(SQLFunctionArgument('qpa', UInt16()),
          SQLFunctionArgument('qpu', QuotaPeriodUnit.db_type()),
          SQLFunctionArgument('time', DateTime()),
          SQLFunctionArgument('endtime', DateTime())),
    returns=PercentFraction(),
    comment='Calculate remaining part of current quota period',
    reads_sql=False,
    writes_sql=False)
AcctRatePercentSpentFunction = SQLFunction(
    'acct_rate_percent_spent',
    args=(SQLFunctionArgument('qpa', UInt16()),
          SQLFunctionArgument('qpu', QuotaPeriodUnit.db_type()),
          SQLFunctionArgument('time', DateTime()),
          SQLFunctionArgument('endtime', DateTime())),
    returns=PercentFraction(),
    comment='Calculate spent part of current quota period',
    reads_sql=False,
    writes_sql=False)
AcctRateQPCountFunction = SQLFunction(
    'acct_rate_qpcount',
    args=(SQLFunctionArgument('qpa', UInt16()),
          SQLFunctionArgument('qpu', QuotaPeriodUnit.db_type()),
          SQLFunctionArgument('dfrom', DateTime()),
          SQLFunctionArgument('dto', DateTime())),
    returns=UInt32(),
    comment='Calculate number of periods between two dates',
    reads_sql=False,
    writes_sql=False)
AcctRateQPLengthFunction = SQLFunction(
    'acct_rate_qplength',
    args=(SQLFunctionArgument('qpa', UInt16()),
          SQLFunctionArgument('qpu', QuotaPeriodUnit.db_type()),
          SQLFunctionArgument('endtime', DateTime())),
    returns=UInt32(),
    comment='Calculate length of current quota period in seconds',
    reads_sql=False,
    writes_sql=False)
AcctRateQPNewFunction = SQLFunction(
    'acct_rate_qpnew',
    args=(SQLFunctionArgument('qpa', UInt16()),
          SQLFunctionArgument('qpu', QuotaPeriodUnit.db_type()),
          SQLFunctionArgument('time', DateTime())),
    returns=UInt32(),
    comment='Calculate new quota period to seconds',
    reads_sql=False,
    writes_sql=False)
AcctRateQPSpentFunction = SQLFunction(
    'acct_rate_qpspent',
    args=(SQLFunctionArgument('qpa', UInt16()),
          SQLFunctionArgument('qpu', QuotaPeriodUnit.db_type()),
          SQLFunctionArgument('time', DateTime()),
          SQLFunctionArgument('endtime', DateTime())),
    returns=UInt32(),
    comment='Calculate spent part of current quota period in seconds',
    reads_sql=False,
    writes_sql=False)
