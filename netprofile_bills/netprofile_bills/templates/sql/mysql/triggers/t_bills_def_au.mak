## -*- coding: utf-8 -*-
<%inherit file="netprofile:templates/ddl_trigger.mak"/>\
<%block name="sql">\
	INSERT INTO `logs_data` (`login`, `type`, `action`, `data`)
	VALUES (@accesslogin, 15, 2, CONCAT_WS(" ",
		"Modified bill",
		CONCAT("[ID ", NEW.billid, "]")
	));
</%block>
