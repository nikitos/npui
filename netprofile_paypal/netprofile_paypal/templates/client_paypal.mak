## -*- coding: utf-8 -*-
		<li class="list-group-item">
			<form class="row" role="form" method="post" action="https://www.paypal.com/cgi-bin/webscr" target="_top">
##			<form class="row" role="form" method="post" action="${req.route_url('paypal.cl.docc')}" target="_top">
				<label for="" class="col-sm-4">${_('Paypal Payment')}</label>
				<div class="col-sm-8 form-inline">
					<input type="hidden" name="cmd" value="_xclick">
					<input type="hidden" name="business" value="info@itws.ru">
					<input type="hidden" name="item_name" value="${_('Stash refill')}">
					<input type="hidden" name="no_shipping" value="1">
					<input type="hidden" name="no_note" value="1">
					<input type="hidden" name="tax" value="0">
					<input type="hidden" name="currency_code" value="RUB">
					<input type="hidden" name="bn" value="PP-BuyNowBF">
					<input type="hidden" name="charset" value="UTF-8">
					<input type="hidden" name="return" value="">
					<input type="hidden" name="cancel" value="">
					<input type="hidden" name="csrf" value="${req.get_csrf()}" />
					<input type="hidden" name="stashid" value="${stash.id}" />
					<input type="text" placeholder="${_('Enter sum')}" class="form-control" required="required" name="amount" title="${_('Enter the sum you want to pay at a later date.')}" value="" tabindex="-1" autocomplete="off" />
##					<input type="text" placeholder="${_('Enter sum')}" class="form-control" required="required" name="diff" title="${_('Enter the sum you want to pay at a later date.')}" value="" tabindex="-1" autocomplete="off" />
					<button class="btn btn-default" type="submit" name="submit" title="${_('Press to make payment')}">${_('Pay')}</button>
				</div>
			</form>
		</li>

