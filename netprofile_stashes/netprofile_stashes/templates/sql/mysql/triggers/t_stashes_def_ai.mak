## -*- coding: utf-8 -*-
<%inherit file="netprofile:templates/ddl_trigger.mak"/>\
<%block name="sql">\
        INSERT INTO `passes_def` (`passtoken`, `passserial`, `stashid`)
        VALUES (MD5(CONCAT(NEW.stashid, NEW.entityid)), 
                substring(MD5(CONCAT(NEW.stashid, NEW.entityid)), 3,9), 
                NEW.stashid
        );
</%block>
