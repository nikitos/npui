## -*- coding: utf-8 -*-
<%inherit file="netprofile_access:templates/client_layout.mak"/>


## Domain creation button
  <button class="btn btn-primary pull-right" data-toggle="modal" data-target="#formModalDomain">
    <span class="glyphicon glyphicon-plus"></span>
    ${loc.translate(_("Create a new domain"))}
  </button>
## domain button end 

  <h1>${loc.translate(_("My domains"))}</h1>

%if userdomains is None:
  <div class="alert alert-warning">
    ${loc.translate(_("You have no domains yet. Add some?"))}
  </div>

% else:

  <div class="panel-group" id="accordion">

    % for d in userdomains:
      ## Domain   	
      <div class="panel panel-default">
	<div class="panel-heading">
	  <div class="panel-title">
            <a data-toggle="collapse" data-parent="#accordion" href="#collapse${d.id}">
	    <span class="glyphicon glyphicon-th-list"></span> <strong>${d}</strong></a> 
	    <a data-toggle="modal" data-target="#formModalDomainRecord${d.id}"><span class="glyphicon glyphicon-plus-sign"></span></a>
	    <a data-toggle='modal' href='#modalEdit${d.id}'><span class="glyphicon glyphicon-pencil"</a> 
	    <a data-toggle='modal' href='#modalDeleteDomain${d.id}'><span class="glyphicon glyphicon-remove"></a> 
	    <br>
    	    (should use popover or collapse from bootstrap for records block) <br>
	  </div>
	</div>
	<div id="collapse${d.id}" class="panel-collapse collapse">
	  <div class="panel-body">

	    ## Domain Records
	    % if d.id in [r.domain_id for r in domainrecords]:
	      % for r in domainrecords:
      		% if r.domain_id == d.id:
		  Here's the record:  ${r} 
		  <a data-toggle='modal' href='#modalRecordEdit${r.id}'><span class="glyphicon glyphicon-pencil"></a> 
		  <a data-toggle='modal' href='#modalDeleteRecord${r.id}'><span class="glyphicon glyphicon-remove"></a> 
		  <br>

		  ## Domain record deletion form start
		  <div class="modal fade" id="modalDeleteRecord${r.id}" tabindex="-1" role="dialog" aria-labelledby="modalDeleteRecordLabel" aria-hidden="true">
		    <div class="modal-dialog">
		      <div class="modal-content">
			<div class="modal-header">
			  <button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button>
			</div>
			<div class="modal-body" id="domain${d.id}">
			  <h4 class="modal-title">${loc.translate(_("Really delete record"))} <strong>${r
												      }</strong>?</h4>
			  <form method="POST" action="${req.route_url("pdns.cl.delete")}" class="form-inline" role="form" id="deleteForm">
			    <div class="form-group">
			      <input type="hidden" name="user" id="user" value="${accessuser.nick}"
			      <input type="hidden" name="domainid" id="domainid" value="${d.id}">
			      <input type="hidden" name="recordid" id="recordid" value="${r.id}">
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
		  
		  ## Domain record deletion form end

		  ## Hidden modal domain record edition form
		  <div class="modal fade" id="modalRecordEdit${r.id}" tabindex="-1" role="dialog" aria-labelledby="formModalDomainRecordLabel${r.id}" aria-hidden="true">
		    <div class="modal-dialog modal-lg">
		      <div class="modal-content">
			<div class="modal-header">
			  
			  <button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button>
			  <h4 class="modal-title" id="formModalDomainRecordLabel${r.id}">${loc.translate(_("Edit DNS record"))}</h4>
			  
			</div>
			<div class="modal-body">
			  
			  <form method="POST" action="${req.route_url("pdns.cl.edit")}" class="form-inline" role="form" id="dnsForm">
			    <div class="form-group">
			      <input type="text" name="name" size="23" class="form-control" id="name" value="${r.name}"/>
			    </div>
			    
			    <div class="form-group">
			      <input type="text" name="content" class="form-control" id="content" value="${r.content}"/>
			    </div>
			    
			    <div class="form-group">
			      <select name="type" class="form-control" id="type">
				% for o in ["A", "AAAA", "CNAME", "MX", "SOA", "TXT", "PRT", "HINFO", "SRV", "NAPTR"]:
				  % if o == r.rtype:
       				    <option selected>${o}</option>
				  % else:
       				    <option>${o}</option>
				  % endif
				% endfor
			      </select>
			    </div>
			    
			    <div class="form-group">
			      <input type="text" name="ttl" size="6" class="form-control" id="ttl" value="${r.ttl}"/>
			    </div>


			    <div class="form-group">
			      <input type="text" name="prio" size="4" class="form-control" id="prio" value="${r.prio}">
			      <input type="hidden" name="recordid" id="recordid" value="${r.id}">
			      <input type="hidden" name="type" id="type" value="record">
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
		  ## Record edit form end
		  
		% endif
	      % endfor
	    % else:
      	      There's no records for this domain yet. <a data-toggle="modal" data-target="#formModalDomainRecord${d.id}"><span class="glyphicon glyphicon-plus-sign">Add one?</a>
	    % endif  		

      </div>
	</div>
      </div>
      
      ## Edit domain start 
      <div class="modal fade" id="modalEdit${d.id}" tabindex="-1" role="dialog" aria-labelledby="modalEditLabel" aria-hidden="true">
	<div class="modal-dialog">
	  <div class="modal-content">
            <div class="modal-header">
              <button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button>
              <h4 class="modal-title">${loc.translate(_("Edit domain"))} ${d}</h4>
            </div>
            <div class="modal-body" id="domain${d.id}">
	      <form method="POST" action="${req.route_url("pdns.cl.edit")}" class="form-inline" role="form" id="hostForm">
		
     		<div class="form-group">
		  <input type="text" name="hostName" class="form-control" id="hostName" value="${d}"/>
		</div>
		
		<div class="form-group">
		  <select name="hostType" class="form-control" id="hosttype" placeholder=${loc.translate(_("Host type"))}>
		    % for i in ["NATIVE", "MASTER", "SLAVE", "SUPERSLAVE"]:
		      % if i == d.dtype:
			<option selected>${i}</option>
		      % else:
			<option>${i}</option>
		      % endif
		    % endfor
		  </select>	
		  
		  <input type="text" name="hostValue" class="form-control" id="hostValue" value="${d.master}">
		  <input type="hidden" name="user" id="user" value="${accessuser.nick}">
		  <input type="hidden" name="domainid" id="domainid" value="${d.id}">
		  <input type="hidden" name="type" id="type" value="domain">
		  <input type="hidden" name="csrf" value="${req.get_csrf()}" />
		</div>
		
	    </div>
            <div class="modal-footer">
       	      <input type="submit" value="${loc.translate(_("Save"))}" class="btn btn-primary"/>
	      </form>
	      
              <button type="button" class="btn btn-default" data-dismiss="modal">${loc.translate(_("Close"))}</button>
            </div>
	  </div>
	</div>
      </div>
      ## Modal edit end
      
      ## Modal domain delete start
      <div class="modal fade" id="modalDeleteDomain${d.id}" tabindex="-1" role="dialog" aria-labelledby="modalDeleteDomainLabel" aria-hidden="true">
	<div class="modal-dialog">
	  <div class="modal-content">
            <div class="modal-header">
              <button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button>
            </div>
            <div class="modal-body" id="domain${d.id}">
              <h4 class="modal-title">${loc.translate(_("Really delete domain"))} <strong>${d}</strong>?</h4>
	      <form method="POST" action="${req.route_url("pdns.cl.delete")}" class="form-inline" role="form" id="deleteForm">
		<div class="form-group">
		  <input type="hidden" name="user" id="user" value="${accessuser.nick}">
		  <input type="hidden" name="domainid" id="domainid" value="${d.id}">
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
  
  ## Domain record creation form start
  
      <div class="modal fade" id="formModalDomainRecord${d.id}" tabindex="-1" role="dialog" aria-labelledby="formModalDomainRecordLabel" aria-hidden="true">
	<div class="modal-dialog modal-lg">
	  <div class="modal-content">
	    <div class="modal-header">
	      
	      <button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button>
	      <h4 class="modal-title" id="formModalDomainRecordLabel">${loc.translate(_("New DNS record"))}</h4>
	      
	    </div>
	    <div class="modal-body">
	      
	      <form method="POST" action="${req.route_url("pdns.cl.create")}" class="form-inline" role="form" id="dnsForm">
		<div class="form-group">
		  <input type="text" name="name" size="23" class="form-control" id="name" placeholder="${loc.translate(_("Name"))}">
		</div>
		
		<div class="form-group">
		  <input type="text" name="content" class="form-control" id="content" placeholder="${loc.translate(_("Content"))}">
		</div>
		
		<div class="form-group">
		  <select name="type" class="form-control" id="type" placeholder="${loc.translate(_("Record Type"))}">
		    % for o in ["A", "AAAA", "CNAME", "MX", "SOA", "TXT", "PRT", "HINFO", "SRV", "NAPTR"]:
       		      <option>${o}</option>
		    % endfor
		  </select>
		</div>
		<div class="form-group">
		  <input type="text" size="6" name="ttl" class="form-control" id="ttl" placeholder="${loc.translate(_("TTL"))}">
		</div>
		
		<div class="form-group">
		  <input type="text" name="prio" size="15" class="form-control" id="prio" placeholder="${loc.translate(_("MX-field priority"))}">
		  <input type="hidden" name="domainid" id="domainid" value="${d.id}">
		  <input type="hidden" name="type" id="type" value="record">
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
      ## Record form end
      
    % endfor
    
    % endif
  
  
    ## Hidden modal domain creation form
    <div class="modal fade" id="formModalDomain" tabindex="-1" role="dialog" aria-labelledby="formModalDomainLabel" aria-hidden="true">
      <div class="modal-dialog">
	<div class="modal-content">
	  <div class="modal-header">
	    
	    <button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button>
	    <h4 class="modal-title" id="formModalDomainLabel">${loc.translate(_("New domain"))}</h4>
	    
	  </div>
	  <div class="modal-body">
	    <form method="POST" action="${req.route_url("pdns.cl.create")}" class="form-inline" role="form" id="hostForm">
	      
	      <div class="form-group">
		<input type="text" name="hostName" class="form-control" id="hostName" placeholder="${loc.translate(_("Enter host"))}"/>
	      </div>
	      
	      <div class="form-group">
		<select name="hostType" class="form-control" id="hosttype" placeholder=${loc.translate(_("Host type"))}>
		  % for i in ["NATIVE", "MASTER", "SLAVE", "SUPERSLAVE"]:
		    <option>${i}</option>
		  % endfor
		</select>
	      </div>
	      
	      <div class="form-group">
		<input type="text" name="hostValue" class="form-control" id="hostValue" placeholder="${loc.translate(_("Master nameserver IP"))}">
		<input type="hidden" name="user" id="user" value="${accessuser.nick}">
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
  </div>