## -*- coding: utf-8 -*-
<%inherit file="netprofile_access:templates/client_layout.mak"/>\
<%namespace module="netprofile.common.hooks" import="gen_block" />\
<%namespace module="netprofile.tpl.filters" import="date_fmt, curr_fmt" />\
<%block name="title">${_('Register')}</%block>

<h1>${_('Registration Form')}</h1>
<p>${_('Please fill in this form so we can properly set up your account.')}</p>
% if 'csrf' in errors:
<div class="alert alert-warning alert-dismissable">
	<button type="button" class="close" data-dismiss="alert" aria-hidden="true">&times;</button>
	${errors['csrf']}
</div>
% endif
<div class="form-horizontal">
<form method="post" novalidate="novalidate" action="${req.route_url('paypal.cl.docc')}" id="register-form" role="form">
	<div class="row form-group${' has-warning' if 'type' in errors else ''}">
		<label class="col-sm-4 control-label" for="diff">${_('Payment amount')}</label>
		<div class="controls col-sm-8">
			<input
				type="text"
				class="form-control"
				required="required"
				id="diff"
				name="diff"
				value="${diff}"
				size="10"
				maxlength="254"
				pattern="[\w\d._-]+"
				tabindex="1"
				disabled="disabled"
			/>
		</div>
	</div>
<fieldset>
	<legend>${_('Credit card information')}</legend>
	<div class="row form-group${' has-warning' if 'type' in errors else ''}">
		<label class="col-sm-4 control-label" for="type">${_('Card type')}</label>
		<div class="controls col-sm-8">
			<select class="form-control padded-wrap" id="type" name="type" title="${_('Card type')}" style="min-width: 120px;" data-placeholder="${_('Select card type')}" required="required">
				<option value="" selected="selected"></option>
				<option label="VISA" value="visa">VISA</option>
				<option label="MasterCard" value="mastercard">MasterCard</option>
				<option label="American Express" value="amex">American Express</option>
				<option label="Discover" value="discover">Discover</option>
			</select>
			<span class="req">*</span>
			<div class="help-block"><ul role="alert">
% if 'type' in errors:
				<li>${errors['type']}</li>
% endif
			</div>
		</div>
	</div>
	<div class="row form-group${' has-warning' if 'number' in errors else ''}">
		<label class="col-sm-4 control-label" for="number1">${_('Card number')}</label>
		<div class="controls col-sm-8">
			<div class="row">
			<div class="col-xs-3">
			<input
				type="number"
				class="form-control"
				required="required"
				id="number1"
				name="number1"
				value=""
				size="4"
				maxlength="4"
				tabindex="2"
				data-validation-required-message="${_('This field is required')}"
				data-validation-maxlength-message="${_('This field is too long')}"
			/>
			</div>
			<div class="col-xs-3">
			<input
				type="number"
				class="form-control"
				required="required"
				id="number2"
				name="number2"
				value=""
				size="4"
				maxlength="4"
				tabindex="2"
				data-validation-required-message="${_('This field is required')}"
				data-validation-maxlength-message="${_('This field is too long')}"
			/>
			</div>
			<div class="col-xs-3">
			<input
				type="number"
				class="form-control"
				required="required"
				id="number3"
				name="number3"
				value=""
				size="4"
				maxlength="4"
				tabindex="2"
				data-validation-required-message="${_('This field is required')}"
				data-validation-maxlength-message="${_('This field is too long')}"
			/>
			</div>
			<div class="col-xs-3">
			<input
				type="number"
				class="form-control"
				required="required"
				id="number4"
				name="number4"
				value=""
				size="4"
				maxlength="4"
				tabindex="2"
				data-validation-required-message="${_('This field is required')}"
				data-validation-maxlength-message="${_('This field is too long')}"
			/>
			</div>
			</div>
			<span class="req">*</span>
			<div class="help-block"><ul role="alert">
% if 'number' in errors:
				<li>${errors['number']}</li>
% endif
			</ul></div>
		</div>
	</div>
	<div class="row form-group${' has-warning' if 'date' in errors else ''}">
		<label class="col-sm-4 control-label" for="date">${_('Card expire')}</label>
		<div class="controls col-sm-8">
			<div class="row">
			<div class="col-sm-4">
			<select class="form-control padded-wrap" id="month" name="month" title="${_('Expire month')}">
				<option value="01">${_('January')}</option>
				<option value="02">${_('February')}</option>
				<option value="03">${_('March')}</option>
				<option value="04">${_('April')}</option>
				<option value="05">${_('May')}</option>
				<option value="06">${_('June')}</option>
				<option value="07">${_('July')}</option>
				<option value="08">${_('August')}</option>
				<option value="09">${_('Septebmer')}</option>
				<option value="10">${_('October')}</option>
				<option value="11">${_('November')}</option>
				<option value="12">${_('December')}</option>
			</select>
			</div>
			<div class="col-sm-8">
			<select class="form-control padded-wrap" id="year" name="year" title="${_('Expire year')}">
				<option value="2014">2014</option>
				<option value="2015">2015</option>
				<option value="2016">2016</option>
				<option value="2017">2017</option>
				<option value="2018">2018</option>
				<option value="2019">2019</option>
				<option value="2020">2020</option>
			</select>
			</div>
			</div>
			<span class="req">*</span>
			<div class="help-block"><ul role="alert">
% if 'date' in errors:
				<li>${errors['date']}</li>
% endif
			</ul></div>
		</div>
	</div>
	<div class="row form-group${' has-warning' if 'cvv2' in errors else ''}">
		<label class="col-sm-4 control-label" for="cvv2">${_('Secret code')}</label>
		<div class="controls col-sm-8">
			<input
				type="text"
				class="form-control"
				required="required"
				id="cvv2"
				name="cvv2"
				title="${_('Enter your desired password')}"
				placeholder="${_('Enter your desired password')}"
				value=""
				size="10"
				minlength="3"
				maxlength="4"
				tabindex="3"
				data-validation-required-message="${_('This field is required')}"
				data-validation-minlength-message="${_('This field is too short')}"
				data-validation-maxlength-message="${_('This field is too long')}"
			/>
			<span class="req">*</span>
			<div class="help-block"><ul role="alert">
% if 'cvv2' in errors:
				<li>${errors['pass']}</li>
% endif
			</ul></div>
		</div>
	</div>
</fieldset>
<fieldset>
	<legend>${_('Personal Information')}</legend>
	<div class="row form-group${' has-warning' if 'name_family' in errors else ''}">
		<label class="col-sm-4 control-label" for="name_family">${_('Family Name')}</label>
		<div class="controls col-sm-8">
			<input
				type="text"
				class="form-control"
				required="required"
				id="name_family"
				name="name_family"
				title="${_('Enter your family name')}"
				placeholder="${_('Enter your family name')}"
				value=""
				size="30"
				maxlength="254"
				tabindex="5"
				data-validation-required-message="${_('This field is required')}"
				data-validation-maxlength-message="${_('This field is too long')}"
			/>
			<span class="req">*</span>
			<div class="help-block"><ul role="alert">
% if 'name_family' in errors:
				<li>${errors['name_family']}</li>
% endif
			</ul></div>
		</div>
	</div>
	<div class="row form-group${' has-warning' if 'name_given' in errors else ''}">
		<label class="col-sm-4 control-label" for="name_given">${_('Given Name')}</label>
		<div class="controls col-sm-8">
			<input
				type="text"
				class="form-control"
				required="required"
				id="name_given"
				name="name_given"
				title="${_('Enter your given name')}"
				placeholder="${_('Enter your given name')}"
				value=""
				size="30"
				maxlength="254"
				tabindex="6"
				data-validation-required-message="${_('This field is required')}"
				data-validation-maxlength-message="${_('This field is too long')}"
			/>
			<span class="req">*</span>
			<div class="help-block"><ul role="alert">
% if 'name_given' in errors:
				<li>${errors['name_given']}</li>
% endif
			</ul></div>
		</div>
	</div>
</fieldset>
% if must_recaptcha:
<fieldset>
	<legend>${_('User Validation')}</legend>
	<div class="row recaptcha-row form-group"><div class="col-sm-offset-4 col-sm-8">
% if 'recaptcha' in errors:
		<div class="alert alert-warning alert-dismissable">
			<button type="button" class="close" data-dismiss="alert" aria-hidden="true">&times;</button>
			${errors['recaptcha']}
		</div>
% endif
		<script type="text/javascript" src="http://www.google.com/recaptcha/api/challenge?k=${rc_public}"></script>
		<noscript>
			<iframe src="http://www.google.com/recaptcha/api/noscript?k=${rc_public}" height="300" width="500" frameborder="0"></iframe><br />
			<textarea name="recaptcha_challenge_field" rows="3" cols="40"></textarea>
			<input type="hidden" name="recaptcha_response_field" value="manual_challenge" />
		</noscript>
	</div></div>
</fieldset>
% endif
<div class="form-actions row">
	<p class="col-sm-4 legend"><span class="req">*</span> ${_('Fields marked with this symbol are required.')}</p>
	<div class="controls col-sm-8">
		<input type="hidden" id="csrf" name="csrf" value="${req.get_csrf()}" />
		<input type="hidden" id="xopid" name="xopid" value="${xopid}" />
		<button type="submit" class="btn btn-primary btn-large pull-right" id="pay" name="pay" title="${_('Register new account')}" tabindex="10">${_('Pay')}</button>
</form>
<form method="post" novalidate="novalidate" action="${req.route_url('paypal.cl.docc')}" id="register-form" class="form-horizontal" role="form">
		<input type="hidden" id="csrf" name="csrf" value="${req.get_csrf()}" />
		<input type="hidden" id="xopid" name="xopid" value="${xopid}" />
		<button type="submit" class="btn btn-large" id="cancel" name="cancel" title="${_('Cancel payment')}" tabindex="11">${_('Cancel')}</button>
</form>
	</div>
</div>
</div>

