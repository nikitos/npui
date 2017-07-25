## -*- coding: utf-8 -*-
##
## NetProfile: HTML block template for rate ops
## Copyright © 2014-2017 Alex Unigovsky
##
## This file is part of NetProfile.
## NetProfile is free software: you can redistribute it and/or
## modify it under the terms of the GNU Affero General Public
## License as published by the Free Software Foundation, either
## version 3 of the License, or (at your option) any later
## version.
##
## NetProfile is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
## GNU Affero General Public License for more details.
##
## You should have received a copy of the GNU Affero General
## Public License along with NetProfile. If not, see
## <http://www.gnu.org/licenses/>.
##
			<div class="row">
				<label for="fld-rate-${stash.id}" class="col-sm-4">${_('Current Rate', domain='netprofile_access')}</label>
				<div id="fld-rate-${stash.id}" class="col-sm-8">
					${a.rate}
% if not a.next_rate:
					<button type="button" class="btn btn-link js-only" data-toggle="collapse" data-target="#form-chrate-${a.id}">${_('Change', domain='netprofile_access')}</button>
% endif
				</div>
			</div>
% if a.next_rate:
			<div class="row">
				<label for="fld-nextrate-${stash.id}" class="col-sm-4">${_('Next Rate', domain='netprofile_access')}</label>
				<div id="fld-nextrate-${stash.id}" class="col-sm-8">
					${a.next_rate}
					<button type="button" class="btn btn-link js-only" data-toggle="collapse" data-target="#form-chrate-${a.id}">${_('Change', domain='netprofile_access')}</button>
				</div>
			</div>
% endif
			<div id="form-chrate-${a.id}" class="collapse">
			<form class="row" role="form" method="post" action="${req.route_url('stashes.cl.accounts', traverse=(stash.id, 'chrate'))}">
				<label for="fld-chrate-${a.id}" class="col-sm-4">${_('New Next Rate', domain='netprofile_access')}</label>
				<div class="col-sm-8 form-inline">
					<input type="hidden" name="csrf" value="${req.get_csrf()}" />
					<input type="hidden" name="entityid" value="${a.id}" />
					<select class="form-control chosen-select padded-wrap" id="fld-chrate-${a.id}" name="rateid" title="${_('Next Rate', domain='netprofile_access')}" style="min-width: 120px;">
% for rate in rates:
						<option label="${rate}" value="${rate.id}"\
% if (a.next_rate_id and (rate.id == a.next_rate_id)) or ((not a.next_rate_id) and (rate.id == a.rate_id)):
 selected="selected"\
% endif
>${rate}</option>
% endfor
					</select>
					<span class="btn-group">
						<button class="btn btn-default" type="submit" name="submit" title="${_('Select different next rate', domain='netprofile_access')}">${_('Set', domain='netprofile_access')}</button>
% if a.next_rate_id:
						<button class="btn btn-default" type="submit" name="clear" title="${_('Cancel scheduled rate change', domain='netprofile_access')}">${_('Clear', domain='netprofile_access')}</button>
% endif
					</span>
				</div>
			</form>
			</div>

