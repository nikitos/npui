## -*- coding: utf-8 -*-
<%inherit file="netprofile_access:templates/client_base.mak"/>
<%block name="title">${_('Log In')}</%block>
<%block name="head">\
	<link rel="stylesheet" href="${req.static_url('netprofile_access:static/css/login.css')}" type="text/css" />

<script type="text/javascript">
$(document).ready(function(){
   $("#registersocial").popover({
     placement : 'bottom',
     html : 'true'
    });
});
</script>

</%block>

<div class="container">
<form class="form-signin" role="form" method="post" action="${req.route_url('access.cl.login')}">
	<h2 class="form-signin-heading">${_('Log In')}</h2>
% for msg in req.session.pop_flash():
	<div class="alert alert-${msg['class'] if 'class' in msg else 'success'} alert-dismissable" role="alert">
		<button type="button" class="close" data-dismiss="alert" aria-hidden="true">&times;</button>
		${msg['text']}
	</div>
% endfor
	<input type="hidden" id="csrf" name="csrf" value="${req.get_csrf()}" />
	<input type="text" class="form-control" placeholder="${_('E-mail') if maillogin else _('User Name')}" required="required" autofocus="autofocus" id="user" name="user" title="${_('Enter your e-mail address') if maillogin else _('Enter your user name here')}" value="" maxlength="254" tabindex="1" autocomplete="off" />
	<input type="password" class="form-control" placeholder="${_('Password')}" required="required" id="pass" name="pass" title="${_('Enter your password here')}" value="" maxlength="254" tabindex="2" autocomplete="off" />
	<button type="submit" class="btn btn-lg btn-primary btn-block" id="submit" name="submit" title="${_('Log in to your account')}" tabindex="3">${_('Log In')}</button>
</form>
<form class="form-signin" role="form" method="get" action="${req.route_url('access.cl.login')}">
	<div class="input-group">
		<label class="input-group-addon" for="__locale">${_('Language')}</label>
		<select class="form-control chosen-select" id="__locale" name="__locale" tabindex="4">
% for lang in req.locales:
			<option label="${'%s [%s]' % (req.locales[lang].english_name, req.locales[lang].display_name)}" value="${lang}"\
% if lang == cur_loc:
 selected="selected"\
% endif
>${'%s [%s]' % (req.locales[lang].english_name, req.locales[lang].display_name)}</option>
% endfor
		</select>
		<span class="input-group-btn">
			<button type="submit" class="btn btn-default" id="lang_submit" title="${_('Change your current language')}">${_('Change')}</button>
		</span>
	</div>
	<div>
% if can_reg:
		<a href="${req.route_url('access.cl.register')}" id="register" class="btn btn-default" title="${_('Register new account')}" tabindex="5">${_('Register')}</a>
% endif
% if can_recover:
		<a href="${req.route_url('access.cl.restorepass')}" id="restorepass" class="btn btn-info pull-right" title="${_('Recover lost password via e-mail')}" tabindex="6">${_('Lost Password?')}</a>
% endif
% if can_usesocial:
                <a href="#" id='registersocial' class="btn btn-default" data-toggle="popover" title="${_('Login with...')}" data-content='
		   % for lp in login_providers.keys():
		   % if lp == 'twitter':
		     <span><a data-toggle="modal" href="#modalTwitterEmail"><img src="${req.static_url('netprofile_access:static/img/loginproviders/%s.png' % lp)}" title="${lp.capitalize()}"></a></span>
		   % else:  
		     <span><a href="${req.route_url('access.cl.oauthwrapper')}?prov=${lp.lower()}"><img src="${req.static_url('netprofile_access:static/img/loginproviders/%s.png' % lp)}" title="${lp.capitalize()}"></a><span>
		   % endif
		   % endfor 
		  '>${_('Login with...')}</a>
% endif
	</div>
</form>

% if can_usesocial:
<div class="modal fade" id="modalTwitterEmail" tabindex="-1" role="dialog" aria-labelledby="modalLabelTwitter" aria-hidden="true">
  <div class="modal-dialog">
    <div class="modal-content">
      <div class="modal-header">
        <button type="button" class="close" data-dismiss="modal"><span aria-hidden="true">&times;</span><span class="sr-only">${_('Close')}</span></button>
        <h4 class="modal-title" id="modalLabelTwitter">${_('Please provide a valid email')}</h4>
      </div>
      <div class="modal-body">
        <form method="GET" action="${req.route_url('access.cl.oauthwrapper')}" class="form-inline" role="form" id="emailForm">
          <div class="form-group">
	    <label for="twitterEmail">${_('Email address')}</label>
	    <input type="email" class="form-control" name="twitterEmail" id="twitterEmail" placeholder="${_('Enter email')}">
            <input type="hidden" name="prov" id="prov" value="twitter">
            <input type="hidden" name="csrf" value="${req.get_csrf()}" />
          </div>
      </div>
      <div class="modal-footer">
	<input type="submit" value="${_("Login")}" class="btn btn-primary"/>
	</form>
        <button type="button" class="btn btn-default" data-dismiss="modal">${_('Close')}</button>
      </div>
    </div>
  </div>
</div>

% endif

</div>

