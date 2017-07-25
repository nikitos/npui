## -*- coding: utf-8 -*-
##
## NetProfile: SQL trigger on entities_access (before update)
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
<%inherit file="netprofile:templates/ddl_trigger.mak"/>\
<%block name="sql">\
	DECLARE xdiff DECIMAL(20,8) DEFAULT 0.00000000;
	DECLARE xowned ENUM('Y', 'N') DEFAULT 'N';
	DECLARE curts DATETIME DEFAULT NULL;

	SET NEW.aliasid := OLD.aliasid;
	IF (@ae_ignore IS NULL) OR (@ae_ignore <> 1) THEN
		IF (OLD.rateid <> NEW.rateid) AND (NEW.aliasid IS NULL) THEN
			SET curts := NOW();
			CALL acct_rollback(
				OLD.entityid,
				curts,
				NEW.stashid,
				OLD.rateid,
				NEW.rateid,
				NEW.ut_ingress,
				NEW.ut_egress,
				NEW.qpend,
				NEW.state,
				xdiff
			);
			IF xdiff > 0 THEN
				SET @stash_ignore := 1;
				UPDATE `stashes_def`
				SET `amount` = `amount` + xdiff
				WHERE `stashid` = NEW.stashid;
				SET @stash_ignore := NULL;

				INSERT INTO `stashes_io_def` (`siotypeid`, `stashid`, `entityid`, `ts`, `diff`)
				VALUES (
					(SELECT `siotypeid` FROM `stashes_io_types` WHERE `ftype` = 'rate_rollback'),
					NEW.stashid, OLD.entityid, curts, xdiff
				);
			END IF;
		ELSE
			SET NEW.rateid := OLD.rateid;
		END IF;
	END IF;

	IF (OLD.ipaddrid <> NEW.ipaddrid)
	OR ((OLD.ipaddrid IS NULL) AND (NEW.ipaddrid IS NOT NULL))
	OR ((OLD.ipaddrid IS NOT NULL) AND (NEW.ipaddrid IS NULL))
	THEN
		IF NEW.ipaddrid IS NOT NULL THEN
			SELECT `owned` INTO xowned
			FROM `ipaddr_def`
			WHERE `ipaddrid` = NEW.ipaddrid;

			IF xowned = 'Y' THEN
				SET NEW.ipaddrid := OLD.ipaddrid;
			ELSE
				UPDATE `ipaddr_def`
				SET `owned` = 'Y'
				WHERE `ipaddrid` = NEW.ipaddrid;
			END IF;
		END IF;
		IF (OLD.ipaddrid IS NOT NULL) AND (xowned = 'N') THEN
			UPDATE `ipaddr_def`
			SET `owned` = 'N'
			WHERE `ipaddrid` = OLD.ipaddrid;
		END IF;
	END IF;

	IF (OLD.ip6addrid <> NEW.ip6addrid)
	OR ((OLD.ip6addrid IS NULL) AND (NEW.ip6addrid IS NOT NULL))
	OR ((OLD.ip6addrid IS NOT NULL) AND (NEW.ip6addrid IS NULL))
	THEN
		IF NEW.ip6addrid IS NOT NULL THEN
			SELECT `owned` INTO xowned
			FROM `ip6addr_def`
			WHERE `ip6addrid` = NEW.ip6addrid;

			IF xowned = 'Y' THEN
				SET NEW.ip6addrid := OLD.ip6addrid;
			ELSE
				UPDATE `ip6addr_def`
				SET `owned` = 'Y'
				WHERE `ip6addrid` = NEW.ip6addrid;
			END IF;
		END IF;
		IF (OLD.ip6addrid IS NOT NULL) AND (xowned = 'N') THEN
			UPDATE `ip6addr_def`
			SET `owned` = 'N'
			WHERE `ip6addrid` = OLD.ip6addrid;
		END IF;
	END IF;
</%block>
