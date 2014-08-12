## -*- coding: utf-8 -*-
<%inherit file="netprofile_access:templates/client_layout.mak"/>

## domain creation button
<button class="btn btn-primary pull-right" data-toggle="modal" data-target="#formModalDomain">
  <span class="glyphicon glyphicon-plus"></span>
  ${loc.translate(_("Attach a new domain"))}
</button>
## domain button end 

## Mailbox creation button
<button class="btn btn-primary pull-right" data-toggle="modal" data-target="#formModalMailbox">
  <span class="glyphicon glyphicon-plus"></span>
  ${loc.translate(_("Create a new mailbox"))}
</button>
## mailbox button end 

<h1>${loc.translate(_("My mailboxes"))}</h1>

  ## if there's no domain to attach a mailbox to, we propose to create one
    % if maildomains is None:
      <div class="alert alert-warning">
	${loc.translate(_("You have no domains to attach a mailbox."))}

## >>>>>>>>>>> Make a link here 
	<button class="btn btn-primary btn-sm pull-right" data-toggle="modal" data-target="#formModalDomain">
	  <span class="glyphicon glyphicon-plus"></span>

	  ${loc.translate(_("Create a new domain"))}
	</button>
      </div>
      
## >>>>>>>>>> Make a link here
## if user already have some domains, but no mailboxes, here's the way to create a new mailbox
  % elif maildomains is not None and mailboxes is None:
     <div class="alert alert-warning">
       ${loc.translate(_("You have no mailbox."))}
       <button class="btn btn-primary btn-sm pull-right" data-toggle="modal" data-target="#formModalMailbox">
	 <span class="glyphicon glyphicon-plus"></span>
	 ${loc.translate(_("Create a new one?"))}
       </button>
     </div>

## if user already has some domains and mailboxes attached, we list it here
## we show a list of domains and for every domain a list of all attached mailboxes
  % else:
  <div class="panel-group" id="accordion">
    % for d in maildomains:
      <div class="panel panel-default">
	<div class="panel-heading">
	  <div class="panel-title">
            <a data-toggle="collapse" data-parent="#accordion" href="#collapse${d.id}">
	      <span class="glyphicon glyphicon-th-list"></span> <strong>${d}</strong></a> 
	    <a data-toggle="modal" data-target="#formModalMailbox${d.id}"><span class="glyphicon glyphicon-plus-sign"></span></a>
	    <a data-toggle='modal' href='#modalDomainEdit${d.id}'><span class="glyphicon glyphicon-pencil"</a> 
	      <a data-toggle='modal' href='#modalDomainDelete${d.id}'><span class="glyphicon glyphicon-remove"></a> 
	  </div>
	</div>
	
	<div id="collapse${d.id}" class="panel-collapse collapse">
	  <div class="panel-body">
	    
	    % if d.domain in [m.domain for m in mailboxes]:
	      % for mb in mailboxes:
      		% if mb.domain == d.domain:
		  ${mb}@${d}
		  <a data-toggle='modal' href='#modalMboxEdit${mb.id}'><span class="glyphicon glyphicon-pencil"></a> 
		    <a data-toggle='modal' href='#modalMboxDelete${mb.id}'><span class="glyphicon glyphicon-remove"></a> 
		      <br>

		      ## mbox deletion form start
		      <div class="modal fade" id="modalMboxDelete${mb.id}" tabindex="-1" role="dialog" aria-labelledby="modalMboxDeleteLabel" aria-hidden="true">
			
			<div class="modal-dialog">
			  <div class="modal-content">
	
			    <div class="modal-header">
			      <button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button>
			    </div>
			    
			    <div class="modal-body" id="domain${d.id}">
			      <h4 class="modal-title">${loc.translate(_("Really delete mailbox"))} <strong>${mb}@${d}</strong>?</h4>
			      
			      <form method="POST" action="${req.route_url("postfix.cl.delete")}" class="form-inline" role="form" id="deleteForm">
				<div class="form-group">
				  <input type="hidden" name="user" id="user" value="${accessuser.nick}"
				  <input type="hidden" name="domainid" id="domainid" value="${d.id}">
				  <input type="hidden" name="mboxid" id="mboxid" value="${mb.id}">
				  <input type="hidden" name="type" id="type" value="mbox">
				  <input type="hidden" name="csrf" value="${req.get_csrf()}" />
				</div>
			    </div>
			    <div class="modal-footer">
       			      <input type="submit" value="${loc.translate(_("Delete"))}" class="btn btn-primary"/>
			      </form>
			      <button type="button" class="btn btn-default" data-dismiss="modal">${loc.translate(_("Cancel"))}</button>
			    </div>
			  </div>
			</div>
		      </div>
		      
		      ## Mailbox deletion form end
		      
		      ## Hidden modal mailbox edition form
		      <div class="modal fade" id="modalMboxEdit${mb.id}" tabindex="-1" role="dialog" aria-labelledby="formModalMboxLabel${mb.id}" aria-hidden="true">
			<div class="modal-dialog">
			  <div class="modal-content">
			    <div class="modal-header">
     
			      <button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button>
			      <h4 class="modal-title" id="formModalMboxLabel${mb.id}">${loc.translate(_("Edit mailbox "))}${mb}@${d}</h4>
			    </div>
			    <div class="modal-body">
			      
			      <form method="POST" action="${req.route_url("postfix.cl.edit")}" class="form-inline" role="form" id="editForm">
				<div class="form-group">
				  <input type="text" name="mbName" class="form-control" id="mbName" value="${mb}"/>
				</div>
				@
				<div class="form-group">
				  <select name="mbDomain" class="form-control" id="mbDomain">
				    % for mbd in maildomains:
				      % if mbd.domain == mb.domain:	
       					<option selected>${mbd}</option>
				      % else:
					<option>${mbd}</option>
				      % endif
				    % endfor
				  </select>
				</div>
		
				<div class="form-group">
				  <input type="password" name="mbPassword" class="form-control" id="mbPassword" value="${mb.password}">
				  <input type="hidden" name="mbUsername" id="mbUsername" value="${mb.username}">
				  <input type="hidden" name="id" id="id" value="${mb.id}">
				  <input type="hidden" name="csrf" value="${req.get_csrf()}" />
				</div>
			    </div>
			    <div class="modal-footer">
			      <input type="submit" value="${loc.translate(_("Save"))}" class="btn btn-primary"/>
			      </form>
			      
			      <button type="button" class="btn btn-default" data-dismiss="modal">Close</button>
			      
			    </div>
			  </div>
			</div>
		      </div>
		      ## Mailbox edit form end
		      
		% endif
	      % endfor
	    % else:
	      ## >>>>>>>>>>>>> Make a link to create a mailbox for a domain
      	      There's no mailboxes for this domain yet. <button type="button" class="btn btn-primary btn-sm" data-toggle="modal" data-target="#formModalMailbox${d.id}"><span class="glyphicon glyphicon-plus-sign">${loc.translate(_("Add one?"))} </button>
	    % endif  		
	    
	  </div>
	</div>
      </div>
      
      ## Edit domain start 
      <div class="modal fade" id="modalDomainEdit${d.id}" tabindex="-1" role="dialog" aria-labelledby="modalDomainEditLabel${d.id}" aria-hidden="true">
	<div class="modal-dialog">
	  <div class="modal-content">
	    <div class="modal-header">
              <button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button>
              <h4 class="modal-title" id="modalDomainEditLabel${d.id}">${loc.translate(_("Edit domain"))} ${d}</h4>
            </div>
            <div class="modal-body">
	      <form method="POST" action="${req.route_url("postfix.cl.edit")}" class="form-inline" role="form" id="createDomainForm">
		<div class="form-group">
		  <input type="text" name="mbDomainDescription" class="form-control" id="mbDomainDescription" placeholder="${loc.translate(_("Domain description"))}" value="${d.description}"/>
		</div>

		<div class="form-group">
		  <input type="hidden" name="mbUsername" id="mbUsername" value="${accessuser.nick}">
		  <input type="hidden" name="did" id="did" value="${d.id}">
		  <input type="hidden" name="csrf" value="${req.get_csrf()}" />
		</div>
	    </div>

            <div class="modal-footer">
       	      <input type="submit" value="${loc.translate(_("Save"))}" class="btn btn-primary"/>
			      </form>
			      ## Domain edit form end 	      
              <button type="button" class="btn btn-default" data-dismiss="modal">${loc.translate(_("Close"))}</button>
            </div>
	  </div>
	</div>
      </div>
      ## Modal edit end
      
      ## Modal domain delete start
      <div class="modal fade" id="modalDomainDelete${d.id}" tabindex="-1" role="dialog" aria-labelledby="modalDeleteDomainLabel" aria-hidden="true">
	<div class="modal-dialog">
	  <div class="modal-content">
            <div class="modal-header">
              <button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button>
            </div>
            <div class="modal-body" id="domain${d.id}">
              <h4 class="modal-title">${loc.translate(_("Really delete domain"))} <strong>${d}</strong>?</h4>
	      <form method="POST" action="${req.route_url("postfix.cl.delete")}" class="form-inline" role="form" id="domainDeleteform">
		<div class="form-group">
		  <input type="hidden" name="user" id="user" value="${accessuser.nick}">
		  <input type="hidden" name="domainid" id="domainid" value="${d.id}">
		  <input type="hidden" name="type" id="type" value="domain">
		  <input type="hidden" name="csrf" value="${req.get_csrf()}" />
		</div>
	    </div>
            <div class="modal-footer">
       	      <input type="submit" value="${loc.translate(_("Delete"))}" class="btn btn-primary"/>
	      </form>
              <button type="button" class="btn btn-default" data-dismiss="modal">${loc.translate(_("Cancel"))}</button>
            </div>
	  </div>
	</div>
      </div>
      
      ## Modal domain delete end
      
      ## Mailbox creation form start
      ##  
      <div class="modal fade" id="formModalMailbox${d.id}" tabindex="-1" role="dialog" aria-labelledby="formModalMailboxLabel" aria-hidden="true">
	<div class="modal-dialog modal-lg">
	  <div class="modal-content">
	    <div class="modal-header">
	      
	      <button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button>
	      <h4 class="modal-title" id="formModalMailboxLabel">${loc.translate(_("New mailbox for "))}${d.domain}</h4>
	      
	    </div>
	    <div class="modal-body">
	      
	      <form method="POST" action="${req.route_url("postfix.cl.create")}" class="form-inline" role="form" id="createMailboxForm">
		## >>>>>> Mailbox fields here
		<div class="form-group">
		  <input type="text" name="mbName" class="form-control" id="mbName" placeholder="${loc.translate(_("mailbox"))}">
		</div>
		@
		<div class="form-group">
		  <select name="mbDomain" class="form-control" id="mbDomain" placeholder="${loc.translate(_("domain"))}">
		    % for mbd in maildomains:
		      % if mbd.id == d.id:	
       			<option selected>${mbd}</option>
		      % else:
			<option>${mbd}</option>
		      % endif
		    % endfor
		  </select>
		</div>
		<div class="form-group">
		  <input type="password" name="mbPassword" class="form-control" id="mbPassword" placeholder="${loc.translate(_("password"))}">
		  <input type="hidden" name="mbUsername" id="mbUsername" value="${accessuser.nick}">
		  <input type="hidden" name="type" id="type" value="mbox">
		  <input type="hidden" name="csrf" value="${req.get_csrf()}" />
		</div>
		
	    </div>
	    <div class="modal-footer">
	      <input type="submit" value="${loc.translate(_("Create"))}" class="btn btn-primary"/>
	      </form>
	      
	      <button type="button" class="btn btn-default" data-dismiss="modal">Close</button>
	      
	    </div>
	  </div>
	</div>
      </div>
      ## mailbox form end
      
    % endfor
    
% endif

## Hidden modal mailbox creation form
<div class="modal fade" id="formModalMailbox" tabindex="-1" role="dialog" aria-labelledby="formModalMailboxLabel" aria-hidden="true">
  <div class="modal-dialog">
    <div class="modal-content">
      <div class="modal-header">
	
	<button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button>
	<h4 class="modal-title" id="formModalMailboxLabel">${loc.translate(_("New mailbox"))}</h4>
	
      </div>
      <div class="modal-body">
	<form method="POST" action="${req.route_url("postfix.cl.create")}" class="form-inline" role="form" id="createMailboxForm">
	  <div class="form-group">
	    <input type="text" name="mbName" class="form-control" id="mbName" placeholder="${loc.translate(_("mailbox"))}"/>
	  </div>
	  @
	  <div class="form-group">
	    <select name="mbDomain" class="form-control" id="mbDomain" placeholder=${loc.translate(_("domain"))}>
	      % for d in maildomains:
		<option>${d}</option>
	      % endfor
	    </select>
	  </div>
	  <div class="form-group">
	    <input type="password" name="mbPassword" class="form-control" id="mbPassword" placeholder="${loc.translate(_("password"))}">
	    <input type="hidden" name="mbUsername" id="mbUsername" value="${accessuser.nick}">
	    <input type="hidden" name="type" id="type" value="mbox">
	    <input type="hidden" name="csrf" value="${req.get_csrf()}" />
	  </div>
      </div>
      <div class="modal-footer">
	<input type="submit" value="${loc.translate(_("Create"))}" class="btn btn-primary"/>
	</form>
	<button type="button" class="btn btn-default" data-dismiss="modal">Close</button>
      </div>
    </div>
  </div>
</div>
## mailbox creation form end

## domain creation form
<div class="modal fade" id="formModalDomain" tabindex="-1" role="dialog" aria-labelledby="formModalDomainLabel" aria-hidden="true">
  <div class="modal-dialog">
    <div class="modal-content">
      <div class="modal-header">
	<button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button>
	<h4 class="modal-title" id="formModalDomainLabel">${loc.translate(_("New domain attachment"))}</h4>
      </div>
      <div class="modal-body">
	<form method="POST" action="${req.route_url("postfix.cl.create")}" class="form-inline" role="form" id="createDomainForm">
	  <div class="form-group">
	    ## a list of user related pdnsdomains
	    <select name="mbDomain" class="form-control" id="mbDomain" placeholder=${loc.translate(_("Domain"))}>
	      % for ud in userdomains:
		<option>${ud}</option>
	      % endfor
	    </select>
	  </div>
	  <div class="form-group">
	    <input type="text" name="mbDomainDescription" class="form-control" id="mbDomainDescription" placeholder="${loc.translate(_("Domain description"))}"/>
	  </div>

	  <div class="form-group">
	    <input type="hidden" name="mbUsername" id="mbUsername" value="${accessuser.nick}">
	    <input type="hidden" name="type" id="type" value="domain">
	    <input type="hidden" name="csrf" value="${req.get_csrf()}" />
	  </div>
      </div>
      <div class="modal-footer">
	<input type="submit" value="${loc.translate(_("Create"))}" class="btn btn-primary"/>
	</form>
	<button type="button" class="btn btn-default" data-dismiss="modal">Close</button>
      </div>
    </div>
  </div>
</div>
## domain form end 
</div>
  
