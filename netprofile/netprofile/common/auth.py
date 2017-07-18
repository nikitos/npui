#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# NetProfile: Authentication routines
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
import string
import time

from zope.interface import implementer
from pyramid.interfaces import IAuthenticationPolicy
from pyramid.httpexceptions import HTTPFound
from pyramid.security import (
    Authenticated,
    Everyone,
    forget,
    remember
)

from netprofile.common.crypto import get_salt_string


def auth_add(request, login, route_name):
    sess = request.session
    # TODO: add hook here
    if sess:
        if 'auth.acls' in sess:
            del sess['auth.acls']
        if 'auth.settings' in sess:
            del sess['auth.settings']
    headers = remember(request, login)
    loc = request.route_url(route_name)
    return HTTPFound(location=loc, headers=headers)


def auth_remove(request, route_name):
    sess = request.session
    # TODO: add hook here
    if sess:
        if 'auth.acls' in sess:
            del sess['auth.acls']
        if 'auth.settings' in sess:
            del sess['auth.settings']
        sess.invalidate()
        sess.new_csrf_token()
    headers = forget(request)
    loc = request.route_url(route_name)
    return HTTPFound(location=loc, headers=headers)


class PluginPolicySelected(object):
    def __init__(self, request, policy):
        self.request = request
        self.policy = policy


@implementer(IAuthenticationPolicy)
class PluginAuthenticationPolicy(object):
    def __init__(self, default, routes=None):
        self._default = default
        if routes is None:
            routes = {}
        self._routes = routes

    def add_plugin(self, route, policy):
        self._routes[route] = policy

    def match(self, request):
        if hasattr(request, 'auth_policy'):
            return request.auth_policy
        cur = None
        cur_len = 0
        for route, plug in self._routes.items():
            r_len = len(route)
            if r_len <= cur_len:
                continue
            path = request.path
            if route == path[:r_len]:
                if len(path) > r_len:
                    if path[r_len:r_len + 1] != '/':
                        continue
                cur = plug
                cur_len = r_len
        if cur:
            request.auth_policy = cur
        else:
            request.auth_policy = self._default
        request.registry.notify(PluginPolicySelected(request,
                                                     request.auth_policy))
        return request.auth_policy

    def authenticated_userid(self, request):
        return self.match(request).authenticated_userid(request)

    def unauthenticated_userid(self, request):
        return self.match(request).unauthenticated_userid(request)

    def effective_principals(self, request):
        return self.match(request).effective_principals(request)

    def remember(self, request, principal, **kw):
        return self.match(request).remember(request, principal, **kw)

    def forget(self, request):
        return self.match(request).forget(request)


_TOKEN_FILTER_MAP = (
    [n for n in range(32)] +
    [127, ord('\\'), ord('"')]
)
_TOKEN_FILTER_MAP = dict.fromkeys(_TOKEN_FILTER_MAP, None)


def _filter_token(tok):
    return str(tok).translate(_TOKEN_FILTER_MAP)


def _format_kvpairs(**kwargs):
    return ', '.join('{0!s}="{1}"'.format(k, _filter_token(v))
                     for (k, v) in kwargs.items())


def _generate_nonce(ts, secret, salt=None, chars=string.hexdigits.upper()):
    # TODO: Add optional IP-address/subnet to nonce
    if not salt:
        salt = get_salt_string(16, chars)
    ctx = hashlib.md5(('%s:%s:%s' % (ts, salt, secret)).encode())
    return ('%s:%s:%s' % (ts, salt, ctx.hexdigest()))


def _is_valid_nonce(nonce, secret):
    comp = nonce.split(':')
    if len(comp) != 3:
        return False
    calc_nonce = _generate_nonce(comp[0], secret, comp[1])
    if nonce == calc_nonce:
        return True
    return False


def _is_valid_nonce_timestamp(nonce, max_ahead_sec=5, max_behind_sec=120):
    # Allow nonces to be max_ahead_sec into the future, to account for server
    # farms with unsynchronized clocks.
    cur_ts = round(time.time())
    nonce_ts = nonce.split(':', 1)[0]
    try:
        nonce_ts = int(nonce_ts)
    except (TypeError, ValueError):
        return False
    diff_ts = cur_ts - nonce_ts
    if -max_ahead_sec <= diff_ts <= max_behind_sec:
        return True
    return False


def _generate_digest_challenge(ts, secret, realm, opaque, stale=False):
    nonce = _generate_nonce(ts, secret)
    return 'Digest %s' % (_format_kvpairs(
        realm=realm,
        qop='auth',
        nonce=nonce,
        opaque=opaque,
        algorithm='MD5',
        stale='true' if stale else 'false'
    ),)


def _add_www_authenticate(request, secret, realm, stale=False):
    resp = request.response
    if not resp.www_authenticate:
        resp.www_authenticate = _generate_digest_challenge(
            round(time.time()),
            secret, realm, 'NPDIGEST', stale
        )


def _parse_authorization(request, secret, realm):
    authz = request.authorization
    if not authz or len(authz) != 2 or authz[0] != 'Digest':
        _add_www_authenticate(request, secret, realm)
        return None
    params = authz[1]
    if 'algorithm' not in params:
        params['algorithm'] = 'MD5'
    for required in ('username', 'realm', 'nonce', 'uri',
                     'response', 'cnonce', 'nc', 'opaque'):
        if required not in params or (
                required == 'opaque' and params['opaque'] != 'NPDIGEST'):
            _add_www_authenticate(request, secret, realm)
            return None
    return params


@implementer(IAuthenticationPolicy)
class DigestAuthenticationPolicy(object):
    def __init__(self, secret, callback, **kwargs):
        self.secret = secret
        self.callback = callback
        self.realm = kwargs.get('realm', 'Realm')
        self.check_ts = kwargs.get('check_timestamp', True)
        self.ts_max_ahead = kwargs.get('timestamp_max_ahead', 5)
        self.ts_max_behind = kwargs.get('timestamp_max_behind', 120)

    def authenticated_userid(self, request):
        params = _parse_authorization(request, self.secret, self.realm)
        if params is None:
            return None
        nonce = params['nonce']
        if not _is_valid_nonce(nonce, self.secret):
            _add_www_authenticate(request, self.secret, self.realm)
            return None
        if self.check_ts and not _is_valid_nonce_timestamp(
                nonce, self.ts_max_ahead, self.ts_max_behind):
            _add_www_authenticate(request, self.secret, self.realm, True)
            return None
        userid = params['username']
        if self.callback(params, request) is not None:
            return 'u:%s' % userid
        _add_www_authenticate(request, self.secret, self.realm)

    def unauthenticated_userid(self, request):
        params = _parse_authorization(request, self.secret, self.realm)
        if params is None:
            return None
        nonce = params['nonce']
        if not _is_valid_nonce(nonce, self.secret):
            _add_www_authenticate(request, self.secret, self.realm)
            return None
        if self.check_ts and not _is_valid_nonce_timestamp(
                nonce, self.ts_max_ahead, self.ts_max_behind):
            _add_www_authenticate(request, self.secret, self.realm, True)
            return None
        return 'u:%s' % params['username']

    def effective_principals(self, request):
        creds = [Everyone]
        params = _parse_authorization(request, self.secret, self.realm)
        if params is None:
            return creds
        nonce = params['nonce']
        if not _is_valid_nonce(nonce, self.secret):
            _add_www_authenticate(request, self.secret, self.realm)
            return creds
        if self.check_ts and not _is_valid_nonce_timestamp(
                nonce, self.ts_max_ahead, self.ts_max_behind):
            _add_www_authenticate(request, self.secret, self.realm, True)
            return creds
        groups = self.callback(params, request)
        if groups is None:
            _add_www_authenticate(request, self.secret, self.realm)
            return creds
        creds.append(Authenticated)
        creds.append('u:%s' % params['username'])
        creds.extend(groups)
        return creds

    def remember(self, request, principal, *kw):
        return []

    def forget(self, request):
        return [('WWW-Authenticate', _generate_digest_challenge(
            round(time.time()),
            self.secret,
            self.realm,
            'NPDIGEST'
        ))]
