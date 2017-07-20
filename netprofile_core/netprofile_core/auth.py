#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# NetProfile: Custom authentication plugin for Pyramid
# Copyright © 2013-2017 Alex Unigovsky
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

import hashlib
import hmac
import datetime as dt
from six import PY3
from pyramid.settings import asbool
from pyramid.security import (
    Allow,
    Deny,
    Everyone,
    Authenticated,
    unauthenticated_userid
)
from pyramid.events import ContextFound
from pyramid.authentication import (
    BasicAuthAuthenticationPolicy,
    SessionAuthenticationPolicy
)
from pyramid.authorization import ACLAuthorizationPolicy
from sqlalchemy.orm.exc import NoResultFound

from netprofile.common.auth import (
    DigestAuthenticationPolicy,
    PluginAuthenticationPolicy,
    PluginPolicySelected,
    auth_remove
)
from netprofile.common.modules import IModuleManager
from netprofile.db.connection import DBSession
from netprofile.db.clauses import (
    SetVariable,
    SetVariables
)
from .models import (
    NPSession,
    Privilege,
    User,
    UserSetting,
    UserState
)

if PY3:
    from urllib.parse import unquote
else:
    from urllib import unquote


def get_user(request):
    sess = DBSession()
    userid = unauthenticated_userid(request)

    if userid is not None:
        if userid[:2] == 'u:':
            userid = userid[2:]
        try:
            return sess.query(User).filter(User.state == UserState.active,
                                           User.enabled.is_(True),
                                           User.login == userid).one()
        except NoResultFound:
            return None


def get_acls(request):
    # FIXME: implement ACL cache invalidation
    if 'auth.acls' in request.session:
        return request.session['auth.acls']
    ret = [(Allow, Authenticated, 'USAGE')]
    user = request.user
    if user is None:
        sess = DBSession()
        for priv in sess.query(Privilege):
            if priv.guest_value:
                right = Allow
            else:
                right = Deny
            ret.append((right, Everyone, priv.code))
        request.session['auth.acls'] = ret
        return ret
    for perm, val in user.flat_privileges.items():
        if val:
            right = Allow
        else:
            right = Deny
        ret.append((right, user.login, perm))
    request.session['auth.acls'] = ret
    return ret


def get_settings(request):
    # FIXME: implement settings cache invalidation
    if 'auth.settings' in request.session:
        return request.session['auth.settings']
    mmgr = request.registry.getUtility(IModuleManager)
    all_settings = mmgr.get_settings('user')
    user = request.user

    if user is None:
        ret = {}
        for moddef, sections in all_settings.items():
            for sname, section in sections.items():
                for setting_name, setting in section.items():
                    if setting.default is None:
                        continue
                    ret['%s.%s.%s' % (moddef,
                                      sname,
                                      setting_name)] = setting.default
    else:
        sess = DBSession()
        ret = dict(
            (s.name, s.value)
            for s
            in sess.query(UserSetting).filter(UserSetting.user == user))
        for moddef, sections in all_settings.items():
            for sname, section in sections.items():
                for setting_name, setting in section.items():
                    fullname = '%s.%s.%s' % (moddef, sname, setting.name)
                    if fullname in ret:
                        ret[fullname] = setting.parse_param(ret[fullname])
                    elif setting.default is not None:
                        ret[fullname] = setting.default
    request.session['auth.settings'] = ret
    return ret


def find_princs(userid, request):
    sess = DBSession()

    user = request.user
    if user and user.login == userid:
        return []
    try:
        user = sess.query(User).filter(User.state == UserState.active,
                                       User.enabled.is_(True),
                                       User.login == userid).one()
    except NoResultFound:
        return None
    return []


def find_princs_basic(username, pwd, request):
    sess = DBSession()

    try:
        user = sess.query(User).filter(User.state == UserState.active,
                                       User.enabled.is_(True),
                                       User.login == username).one()
    except NoResultFound:
        return None
    if not user.check_password(pwd):
        return None
    return []


def find_princs_digest(param, request):
    sess = DBSession()

    try:
        user = sess.query(User).filter(User.state == UserState.active,
                                       User.enabled.is_(True),
                                       User.login == param['username']).one()
    except NoResultFound:
        return None
    if not user.password_ha1:
        return None
    req_path = unquote(request.path.lower())
    uri_path = unquote(param['uri'].lower())
    if req_path != uri_path:
        return None
    ha2 = hashlib.md5(('%s:%s' % (request.method,
                                  param['uri'])).encode()).hexdigest()
    data = '%s:%s:%s:%s:%s' % (param['nonce'], param['nc'],
                               param['cnonce'], 'auth', ha2)
    resp = hashlib.md5(('%s:%s' % (user.password_ha1,
                                   data)).encode()).hexdigest()
    if hmac.compare_digest(resp, param['response']):
        groups = ['g:%s' % (user.group.name,)]
        for sgr in user.secondary_groups:
            if sgr == user.group:
                continue
            groups.append('g:%s' % (sgr.name,))
        return groups
    return None


def _auth_to_db(event):
    request = event.request

    if not request.matched_route:
        return
    rname = request.matched_route.name
    if rname[0] == '_':
        return
    if request.method == 'OPTIONS':
        return

    sess = DBSession()
    user = request.user

    if user:
        try:
            sess.execute(SetVariables(accessuid=user.id,
                                      accessgid=user.group_id,
                                      accesslogin=user.login))
        except NotImplementedError:
            sess.execute(SetVariable('accessuid', user.id))
            sess.execute(SetVariable('accessgid', user.group_id))
            sess.execute(SetVariable('accesslogin', user.login))
    else:
        try:
            sess.execute(SetVariables(accessuid=0,
                                      accessgid=0,
                                      accesslogin='[GUEST]'))
        except NotImplementedError:
            sess.execute(SetVariable('accessuid', 0))
            sess.execute(SetVariable('accessgid', 0))
            sess.execute(SetVariable('accesslogin', '[GUEST]'))


def _goto_login(request):
    if request.matched_route:
        if request.matched_route.name == 'extrouter':
            raise auth_remove(request, 'core.logout.direct')
    raise auth_remove(request, 'core.login')


def _check_session(event):
    request = event.request
    if not isinstance(event.policy, SessionAuthenticationPolicy):
        return
    user = request.user
    route_name = None
    if request.matched_route:
        route_name = request.matched_route.name
        # TODO: unhardcode excluded routes
        if route_name in {'core.login',
                          'debugtoolbar',
                          'core.logout.direct',
                          'core.wellknown'}:
            return
    if not user:
        _goto_login(request)
    settings = request.registry.settings

    skey = settings.get('redis.sessions.cookie_name')
    if not skey:
        skey = settings.get('session.key')
    assert skey is not None, 'Session cookie name does not exist'

    sess = DBSession()
    sname = request.cookies.get(skey)
    if sname:
        now = dt.datetime.now()
        oldsess = True

        try:
            npsess = sess.query(NPSession).filter(
                    NPSession.session_name == sname).one()
        except NoResultFound:
            npsess = user.generate_session(request, sname, now)
            if npsess is None:
                _goto_login(request)
            oldsess = False
            sess.add(npsess)

        if oldsess and not npsess.check_request(request, now):
            _goto_login(request)

        pw_age = request.session.get('sess.pwage', 'ok')
        if pw_age == 'force':
            # TODO: unhardcode excluded routes
            if route_name not in {'extrouter',
                                  'extapi',
                                  'core.home',
                                  'core.js.webshell'}:
                _goto_login(request)

        npsess.update_time(now)
        request.np_session = npsess
    else:
        _goto_login(request)


def includeme(config):
    """
    For inclusion by Pyramid.
    """
    config.add_request_method(get_user, str('user'), reify=True)
    config.add_request_method(get_acls, str('acls'), reify=True)
    config.add_request_method(get_settings, str('settings'), reify=True)

    settings = config.registry.settings

    authn_policy = PluginAuthenticationPolicy(
        SessionAuthenticationPolicy(callback=find_princs),
        {
            '/dav': DigestAuthenticationPolicy(
                settings.get('netprofile.auth.secret'),
                find_princs_digest,
                realm=settings.get('netprofile.auth.digest.realm',
                                   'NetProfile UI'),
                check_timestamp=asbool(settings.get(
                    'netprofile.auth.digest.check_timestamp', 'true')),
                timestamp_max_ahead=int(settings.get(
                    'netprofile.auth.digest.timestamp_max_ahead', 5)),
                timestamp_max_behind=int(settings.get(
                    'netprofile.auth.digest.timestamp_max_behind', 120))),
            '/api': BasicAuthAuthenticationPolicy(
                find_princs_basic,
                settings.get('netprofile.auth.rpc_realm', 'NetProfile RPC'),
                settings.get('netprofile.debug'))
        })
    authz_policy = ACLAuthorizationPolicy()

    config.set_authorization_policy(authz_policy)
    config.set_authentication_policy(authn_policy)

    config.add_subscriber(_auth_to_db, ContextFound)
    config.add_subscriber(_check_session, PluginPolicySelected)
