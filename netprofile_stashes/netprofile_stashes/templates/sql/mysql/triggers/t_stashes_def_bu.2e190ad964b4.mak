## -*- coding: utf-8 -*-
##
## NetProfile: SQL trigger on stashes_def (before update)
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
	DECLARE curts, user_qpend, user_newend DATETIME DEFAULT NULL;
	DECLARE done, aeid, user_rateid, user_aliasid, prev_rateid INT UNSIGNED DEFAULT 0;
	DECLARE user_nextrateid, user_sec, rate_qsec INT UNSIGNED DEFAULT 0;
	DECLARE user_uin, user_ueg, rate_qti, rate_qte DECIMAL(16,0) UNSIGNED;
	DECLARE user_state TINYINT UNSIGNED DEFAULT 0;
	DECLARE user_bcheck, user_pcheck, rate_abf, curr_conv_from, curr_conv_to ENUM('Y', 'N') CHARACTER SET ascii DEFAULT 'N';
	DECLARE isok, curr_credit, curr_accounts ENUM('Y', 'N') CHARACTER SET ascii DEFAULT 'Y';
	DECLARE old_balance, new_balance, pay, rate_qsum, rate_oqsum_in, rate_oqsum_eg, rate_oqsum_sec DECIMAL(20,8) DEFAULT 0.0;
	DECLARE curr_xrate, new_xrate DECIMAL(20,8) DEFAULT 1.0;
	DECLARE rate_auxsum DECIMAL(20,8) DEFAULT NULL;
	DECLARE rate_type ENUM('prepaid', 'prepaid_cont', 'postpaid', 'free');
	DECLARE rate_qpa SMALLINT UNSIGNED DEFAULT 1;
	DECLARE rate_qpu ENUM('a_hour', 'a_day', 'a_week', 'a_month', 'a_year', 'c_hour', 'c_day', 'c_month', 'c_year', 'f_hour', 'f_day', 'f_week', 'f_month', 'f_year') CHARACTER SET ascii DEFAULT 'c_month';
	DECLARE st_in VARCHAR(5) DEFAULT 'qin';
	DECLARE st_eg VARCHAR(5) DEFAULT 'qeg';
	DECLARE newpol_in, newpol_eg VARCHAR(255) CHARACTER SET ascii DEFAULT NULL;
	DECLARE cur CURSOR FOR
		SELECT `entityid`, `rateid`, `nextrateid`, `aliasid`, `ut_ingress`, `ut_egress`, `u_sec`, `qpend`, `state`, `bcheck`, `pcheck`
		FROM `entities_access`
		WHERE `stashid` = NEW.stashid
		ORDER BY `rateid` ASC;
	DECLARE CONTINUE HANDLER FOR SQLSTATE '02000'
		SET done := 1;

	SET curts := NOW();

	IF OLD.currid IS NOT NULL THEN
		SELECT `xchange_rate`, `convert_from`, `allow_credit`, `allow_accounts`
		INTO curr_xrate, curr_conv_from, curr_credit, curr_accounts
		FROM `currencies_def`
		WHERE `currid` = OLD.currid;
	END IF;

	IF NEW.amount > OLD.alltime_max THEN
		SET NEW.alltime_max := NEW.amount;
	ELSE
		SET NEW.alltime_max := OLD.alltime_max;
	END IF;
	IF NEW.amount < OLD.alltime_min THEN
		SET NEW.alltime_min := NEW.amount;
	ELSE
		SET NEW.alltime_min := OLD.alltime_min;
	END IF;

	SET old_balance := OLD.amount;
	SET new_balance := NEW.amount;
	IF curr_credit = 'Y' THEN
		SET old_balance := old_balance + OLD.credit;
		SET new_balance := new_balance + NEW.credit;
	END IF;

	IF (curr_accounts = 'Y') AND (new_balance > old_balance) AND ((@stash_ignore IS NULL) OR (@stash_ignore <> 1)) THEN
		OPEN cur;
		sdbic: REPEAT
			SET pay := 0.0;
			SET st_in := 'qin';
			SET st_eg := 'qeg';
			SET isok := 'Y';
			FETCH cur INTO aeid, user_rateid, user_nextrateid, user_aliasid, user_uin, user_ueg, user_sec, user_qpend, user_state, user_bcheck, user_pcheck;
			IF (((user_qpend IS NULL) OR (user_qpend < curts)) AND (user_state <> 2) AND (user_aliasid IS NULL)) THEN
				IF (prev_rateid = 0) OR (prev_rateid <> user_rateid) THEN
					SELECT `type`, `abf`, `qp_amount`, `qp_unit`, `qsum`, `auxsum`, `qt_ingress`, `qt_egress`, `qsec`, `oqsum_ingress`, `oqsum_egress`, `oqsum_sec`, `pol_ingress`, `pol_egress`
					INTO rate_type, rate_abf, rate_qpa, rate_qpu, rate_qsum, rate_auxsum, rate_qti, rate_qte, rate_qsec, rate_oqsum_in, rate_oqsum_eg, rate_oqsum_sec, newpol_in, newpol_eg
					FROM `rates_def`
					WHERE `rateid` = user_rateid;
					SET prev_rateid := user_rateid;

					IF rate_abf = 'Y' THEN
						CALL acct_rate_mods(curts, user_rateid, aeid, rate_oqsum_in, rate_oqsum_eg, rate_oqsum_sec, newpol_in, newpol_eg);
					END IF;
					IF OLD.currid IS NOT NULL THEN
						SET rate_qsum := rate_qsum / curr_xrate;
						SET rate_oqsum_in := rate_oqsum_in / curr_xrate;
						SET rate_oqsum_eg := rate_oqsum_eg / curr_xrate;
						SET rate_oqsum_sec := rate_oqsum_sec / curr_xrate;
						IF rate_auxsum IS NOT NULL THEN
							SET rate_auxsum := rate_auxsum / curr_xrate;
						END IF;
					END IF;
				END IF;
				IF (user_bcheck = 'Y') THEN
				BEGIN
					DECLARE ab_id INT UNSIGNED DEFAULT 0;
					DECLARE ab_state ENUM('planned', 'active', 'expired') DEFAULT 'expired';
					DECLARE CONTINUE HANDLER FOR NOT FOUND BEGIN END;

					SELECT `abid`, `bstate` INTO ab_id, ab_state
					FROM `accessblock_def`
					WHERE `entityid` = aeid
					AND `bstate` IN('planned', 'active')
					AND curts BETWEEN `startts` AND `endts`
					LIMIT 1;

					IF ab_id > 0 THEN
						IF ab_state = 'planned' THEN
							UPDATE `accessblock_def`
							SET
								`bstate` = 'active',
								`oldstate` = user_state
							WHERE `abid` = ab_id;
						END IF;
						UPDATE `entities_access`
						SET
							`state` = 2,
							`bcheck` = 'N'
						WHERE `entityid` = aeid;
						ITERATE sdbic;
					END IF;
				END;
				END IF;
				IF (user_nextrateid IS NOT NULL) AND (user_rateid <> user_nextrateid) AND (rate_type <> 'postpaid') THEN
					SET user_rateid := user_nextrateid;
					IF (prev_rateid = 0) OR (prev_rateid <> user_rateid) THEN
						SELECT `type`, `abf`, `qp_amount`, `qp_unit`, `qsum`, `auxsum`, `qt_ingress`, `qt_egress`, `qsec`, `oqsum_ingress`, `oqsum_egress`, `oqsum_sec`, `pol_ingress`, `pol_egress`
						INTO rate_type, rate_abf, rate_qpa, rate_qpu, rate_qsum, rate_auxsum, rate_qti, rate_qte, rate_qsec, rate_oqsum_in, rate_oqsum_eg, rate_oqsum_sec, newpol_in, newpol_eg
						FROM `rates_def`
						WHERE `rateid` = user_rateid;
						SET prev_rateid := user_rateid;

						IF rate_abf = 'Y' THEN
							CALL acct_rate_mods(curts, user_rateid, aeid, rate_oqsum_in, rate_oqsum_eg, rate_oqsum_sec, newpol_in, newpol_eg);
						END IF;
						IF OLD.currid IS NOT NULL THEN
							SET rate_qsum := rate_qsum / curr_xrate;
							SET rate_oqsum_in := rate_oqsum_in / curr_xrate;
							SET rate_oqsum_eg := rate_oqsum_eg / curr_xrate;
							SET rate_oqsum_sec := rate_oqsum_sec / curr_xrate;
							IF rate_auxsum IS NOT NULL THEN
								SET rate_auxsum := rate_auxsum / curr_xrate;
							END IF;
						END IF;
					END IF;
				END IF;
				IF (rate_type <> 'postpaid') OR (user_qpend IS NOT NULL) THEN
					SET pay := pay + rate_qsum;
				END IF;
				IF (rate_type = 'postpaid') AND (user_qpend IS NOT NULL) THEN
				BEGIN
					DECLARE payin, payout, paysec, tst_amount, tst_credit DECIMAL(20,8) DEFAULT 0.0;

					IF user_uin > rate_qti THEN
						SET payin := (user_uin - rate_qti) * rate_oqsum_in;
						SET st_in := 'min';
					END IF;
					IF user_ueg > rate_qte THEN
						SET payout := (user_ueg - rate_qte) * rate_oqsum_eg;
						SET st_eg := 'meg';
					END IF;
					IF user_sec > rate_qsec THEN
						SET paysec := (user_sec - rate_qsec) * rate_oqsum_sec;
					END IF;
					IF (user_pcheck = 'Y') THEN
						SET tst_amount := NEW.amount;
						IF curr_credit = 'Y' THEN
							SET tst_credit := NEW.credit;
						ELSE
							SET tst_credit := 0.0;
						END IF;
						SET isok := 'Y';
						SET pay := pay - rate_qsum;
						SET @stashio_ignore := 1;
						CALL acct_pcheck(aeid, curts, rate_type, isok, NEW.stashid, user_qpend, tst_amount, tst_credit, OLD.currid, curr_xrate, rate_qsum + payin + payout + paysec);
						SET @stashio_ignore := NULL;
						SET pay := pay + rate_qsum;
						IF (NEW.amount <> tst_amount) THEN
							SET pay := pay + (NEW.amount - tst_amount);
						END IF;
					END IF;
					SET pay := pay + payin + payout + paysec;
				END;
				END IF;
				IF (rate_type IN('prepaid', 'prepaid_cont')) AND (user_pcheck = 'Y') THEN
				BEGIN
					DECLARE tst_amount, tst_credit DECIMAL(20,8) DEFAULT 0.0;

					SET user_newend := FROM_UNIXTIME(UNIX_TIMESTAMP(curts) + acct_rate_qpnew(rate_qpa, rate_qpu, curts));
					SET tst_amount := NEW.amount;
					IF curr_credit = 'Y' THEN
						SET tst_credit := NEW.credit;
					ELSE
						SET tst_credit := 0.0;
					END IF;
					SET isok := 'N';
					SET pay := pay - rate_qsum;
					SET @stashio_ignore := 1;
					CALL acct_pcheck(aeid, curts, rate_type, isok, NEW.stashid, user_newend, tst_amount, tst_credit, OLD.currid, curr_xrate, rate_qsum);
					SET @stashio_ignore := NULL;
					SET pay := pay + rate_qsum;
					IF (NEW.amount <> tst_amount) THEN
						SET pay := pay + (NEW.amount - tst_amount);
					END IF;
				END;
				END IF;
				IF new_balance >= pay THEN
					IF (rate_type = 'prepaid_cont') AND (user_state = 1) AND (new_balance < rate_auxsum) THEN
						SET user_state := 1;
					ELSEIF (rate_type IN('prepaid', 'prepaid_cont')) AND (user_pcheck = 'Y') AND (isok = 'N') THEN
						SET user_state := 1;
					ELSE
						SET NEW.amount := NEW.amount - pay;
						SET new_balance := new_balance - pay;
						IF (rate_type = 'postpaid') AND (user_qpend IS NOT NULL) THEN
							SET @stashio_ignore := 1;
							INSERT INTO `stashes_io_def` (`siotypeid`, `stashid`, `currid`, `entityid`, `ts`, `diff`)
							VALUES (
								(SELECT `siotypeid` FROM `stashes_io_types` WHERE `ftype` = 'rate_qsum_post'),
								NEW.stashid, OLD.currid, aeid, curts, -rate_qsum
							);
							SET @stashio_ignore := NULL;
							INSERT INTO `stashes_ops` (`stashid`, `type`, `ts`, `entityid`, `diff`, `acct_ingress`, `acct_egress`)
							VALUES (NEW.stashid, CONCAT_WS('_', 'sub', st_in, st_eg), curts, aeid, -pay, user_uin, user_ueg);
						END IF;
						IF (user_newend IS NOT NULL) THEN
							SET user_qpend := user_newend;
						ELSE
							SET user_qpend := FROM_UNIXTIME(UNIX_TIMESTAMP(curts) + acct_rate_qpnew(rate_qpa, rate_qpu, curts));
						END IF;
						SET user_state := 0;
						SET user_uin := 0;
						SET user_ueg := 0;
						SET user_sec := 0;
						IF rate_type <> 'postpaid' THEN
							SET @stashio_ignore := 1;
							INSERT INTO `stashes_io_def` (`siotypeid`, `stashid`, `currid`, `entityid`, `ts`, `diff`)
							VALUES (
								(SELECT `siotypeid` FROM `stashes_io_types` WHERE `ftype` = 'rate_qsum_pre'),
								NEW.stashid, OLD.currid, aeid, curts, -rate_qsum
							);
							SET @stashio_ignore := NULL;
							INSERT INTO `stashes_ops` (`stashid`, `type`, `ts`, `entityid`, `diff`, `acct_ingress`, `acct_egress`)
							VALUES (NEW.stashid, CONCAT_WS('_', 'sub', st_in, st_eg), curts, aeid, -pay, 0, 0);
						END IF;
					END IF;
				ELSE
					SET user_state := 1;
				END IF;
				IF (user_nextrateid IS NOT NULL) AND (user_rateid <> user_nextrateid) AND (rate_type = 'postpaid') THEN
					SET user_rateid := user_nextrateid;
					IF (prev_rateid = 0) OR (prev_rateid <> user_rateid) THEN
						SELECT `type`, `abf`, `qp_amount`, `qp_unit`, `qsum`, `auxsum`, `qt_ingress`, `qt_egress`, `qsec`, `oqsum_ingress`, `oqsum_egress`, `oqsum_sec`, `pol_ingress`, `pol_egress`
						INTO rate_type, rate_abf, rate_qpa, rate_qpu, rate_qsum, rate_auxsum, rate_qti, rate_qte, rate_qsec, rate_oqsum_in, rate_oqsum_eg, rate_oqsum_sec, newpol_in, newpol_eg
						FROM `rates_def`
						WHERE `rateid` = user_rateid;
						SET prev_rateid := user_rateid;

						IF rate_abf = 'Y' THEN
							CALL acct_rate_mods(curts, user_rateid, aeid, rate_oqsum_in, rate_oqsum_eg, rate_oqsum_sec, newpol_in, newpol_eg);
						END IF;
						IF OLD.currid IS NOT NULL THEN
							SET rate_qsum := rate_qsum / curr_xrate;
							SET rate_oqsum_in := rate_oqsum_in / curr_xrate;
							SET rate_oqsum_eg := rate_oqsum_eg / curr_xrate;
							SET rate_oqsum_sec := rate_oqsum_sec / curr_xrate;
							IF rate_auxsum IS NOT NULL THEN
								SET rate_auxsum := rate_auxsum / curr_xrate;
							END IF;
						END IF;
					END IF;
				END IF;
				SET @ae_ignore := 1;
				UPDATE `entities_access` SET
					`rateid` = user_rateid,
					`nextrateid` = NULL,
					`ut_ingress` = user_uin,
					`ut_egress` = user_ueg,
					`u_sec` = user_sec,
					`qpend` = user_qpend,
					`state` = user_state
				WHERE `entityid` = aeid;
				SET @ae_ignore := NULL;
			ELSEIF (user_qpend >= curts) AND (user_state = 1) AND (new_balance > 0) THEN
				UPDATE `entities_access`
				SET `state` = 0
				WHERE `entityid` = aeid;
			END IF;
		UNTIL done END REPEAT;
		CLOSE cur;
	END IF;

	IF (OLD.currid <=> NEW.currid) OR (curr_conv_from = 'N') THEN
		SET NEW.currid := OLD.currid;
	ELSE
		IF NEW.currid IS NOT NULL THEN
			SELECT `xchange_rate`, `convert_to`
			INTO new_xrate, curr_conv_to
			FROM `currencies_def`
			WHERE `currid` = NEW.currid;
		END IF;

		SET NEW.amount := NEW.amount * curr_xrate / new_xrate;
		SET NEW.credit := NEW.credit * curr_xrate / new_xrate;
		SET NEW.alltime_max := NEW.alltime_max * curr_xrate / new_xrate;
		SET NEW.alltime_min := NEW.alltime_min * curr_xrate / new_xrate;
	END IF;
</%block>
