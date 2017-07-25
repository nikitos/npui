## -*- coding: utf-8 -*-
##
## NetProfile: SQL function: acct_alloc_ipv6
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
<%inherit file="netprofile:templates/ddl_function.mak"/>\
<%block name="sql">\
	DECLARE pid, entid, rid, xnasid INT UNSIGNED DEFAULT 0;
	DECLARE ipid, sid BIGINT UNSIGNED DEFAULT 0;
	DECLARE ip6_prefix BINARY(16) DEFAULT NULL;
	DECLARE ip6_plen TINYINT UNSIGNED DEFAULT NULL;
	DECLARE EXIT HANDLER FOR NOT FOUND BEGIN
		SELECT
			0 AS `ipstr`,
			0 AS `nasid`,
			NULL AS `prefix`,
			NULL AS `plen`;
		ROLLBACK;
	END;

	START TRANSACTION;

	SELECT `entityid`
	INTO entid
	FROM `entities_def`
	WHERE `nick` = ename AND `etypeid` = 6;

	SELECT `ip6addrid`, `rateid`
	INTO ipid, rid
	FROM `entities_access`
	WHERE `entityid` = entid;

	SELECT `nasid`
	INTO xnasid
	FROM `nas_def`
	WHERE `idstr` LIKE nid;

	IF ipid IS NULL THEN
		SELECT `poolid`
		INTO pid
		FROM `rates_def`
		WHERE `rateid` = rid;

		IF pid IS NULL THEN
			SELECT `poolid`
			INTO pid
			FROM `nas_pools`
			WHERE `nasid` = xnasid
			ORDER BY RAND()
			LIMIT 1;
		ELSE
			SELECT `poolid`
			INTO pid
			FROM `nas_pools`
			WHERE `nasid` = xnasid
			AND `poolid` = pid
			LIMIT 1;
		END IF;

		BEGIN
			DECLARE CONTINUE HANDLER FOR NOT FOUND BEGIN END;

			SET ipid := 0;

			SELECT `ip6addrid`
			INTO ipid
			FROM `ip6addr_def`
			WHERE `inuse` = 'N' AND `poolid` = pid
			LIMIT 1
			FOR UPDATE;

			IF (ipid IS NULL) OR (ipid = 0) THEN
				SELECT `ip6prefix`, `ip6plen`
				INTO ip6_prefix, ip6_plen
				FROM `ippool_def`
				WHERE `poolid` = pid;
			END IF;
		END;
	ELSE
		BEGIN
			DECLARE CONTINUE HANDLER FOR NOT FOUND BEGIN END;

			SELECT `sessid`
			INTO sid
			FROM `sessions_def`
			WHERE `ip6addrid` = ipid;

			IF sid > 0 THEN
				DELETE FROM `sessions_def`
				WHERE `sessid` = sid;
			END IF;
		END;

		SELECT `ip6addrid`
		INTO ipid
		FROM `ip6addr_def`
		WHERE `ip6addrid` = ipid
		FOR UPDATE;
	END IF;

	IF ipid > 0 THEN
		UPDATE `ip6addr_def` SET
			`inuse` = 'Y'
		WHERE `ip6addrid` = ipid;
	END IF;

	SELECT
		ipid AS `ipstr`,
		xnasid AS `nasid`,
		ip6_prefix AS `prefix`,
		ip6_plen AS `plen`;
	COMMIT;
</%block>

