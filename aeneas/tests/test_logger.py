#!/usr/bin/env python

# aeneas is a Python/C library and a set of tools
# to automagically synchronize audio and text (aka forced alignment)
#
# Copyright (C) 2012-2013, Alberto Pettarin (www.albertopettarin.it)
# Copyright (C) 2013-2015, ReadBeyond Srl   (www.readbeyond.it)
# Copyright (C) 2015-2017, Alberto Pettarin (www.albertopettarin.it)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import unittest

from aeneas.logger import Loggable
from aeneas.logger import Logger
from aeneas.runtimeconfiguration import RuntimeConfiguration


class TestLogger(unittest.TestCase):
    def test_log(self):
        logger = Logger(tee=False, indentation=4)
        logger.log("Message 1", Logger.DEBUG)
        logger.log("Message 2", Logger.INFO)
        logger.log("Message 3", Logger.WARNING)
        logger.log("Message 4", Logger.CRITICAL)
        self.assertEqual(len(logger), 4)

    def test_clear(self):
        logger = Logger(tee=False, indentation=4)
        logger.log("Message 1", Logger.DEBUG)
        logger.log("Message 2", Logger.INFO)
        logger.log("Message 3", Logger.WARNING)
        logger.log("Message 4", Logger.CRITICAL)
        self.assertEqual(len(logger), 4)
        logger.clear()
        self.assertEqual(len(logger), 0)

    def test_change_indentation(self):
        logger = Logger(tee=False, indentation=4)
        self.assertEqual(logger.indentation, 4)
        logger.log("Message 1", Logger.DEBUG)
        logger.log("Message 2", Logger.INFO)
        logger.indentation = 2
        self.assertEqual(logger.indentation, 2)
        logger.log("Message 3", Logger.WARNING)
        logger.log("Message 4", Logger.CRITICAL)
        logger.indentation = 0
        self.assertEqual(logger.indentation, 0)

    def test_tag(self):
        logger = Logger(tee=False, indentation=4)
        logger.log("Message 1", Logger.DEBUG, tag="TEST")
        logger.log("Message 2", Logger.DEBUG)
        logger.log("Message 3", Logger.DEBUG, tag="TEST")
        logger.log("Message 4", Logger.DEBUG)
        strings = logger.pretty_print(as_list=True)
        self.assertEqual(strings[0].find("TEST") > -1, True)
        self.assertEqual(strings[1].find("TEST") > -1, False)
        self.assertEqual(strings[2].find("TEST") > -1, True)
        self.assertEqual(strings[3].find("TEST") > -1, False)

    def run_test_multi(self, msg):
        logger = Logger(tee=False)
        logger.log(msg)
        self.assertEqual(len(logger), 1)

    def test_bytes(self):
        with self.assertRaises(TypeError):
            self.run_test_multi(b"These are bytes")

    def test_multi_01(self):
        self.run_test_multi("Message ascii")

    def test_multi_02(self):
        self.run_test_multi("Message with unicode chars: à and '…'")

    def test_multi_03(self):
        self.run_test_multi(["Message ascii"])

    def test_multi_04(self):
        self.run_test_multi(["Message with unicode chars: à and '…'"])

    def test_multi_05(self):
        self.run_test_multi(["Message %s", "1"])

    def test_multi_06(self):
        self.run_test_multi(["Message %d", 1])

    def test_multi_07(self):
        self.run_test_multi(["Message %.3f", 1.234])

    def test_multi_08(self):
        self.run_test_multi(["Message %.3f %.3f", 1.234, 2.345])

    def test_multi_09(self):
        self.run_test_multi(["Message with unicode chars: à and '…' and %s", "ascii"])

    def test_multi_10(self):
        self.run_test_multi("unicode but only with ascii chars")

    def test_multi_11(self):
        self.run_test_multi("unicode with non-ascii chars: à and '…'")

    def test_multi_12(self):
        self.run_test_multi(["Message with unicode chars: %s and '…' and ascii", "àbc"])

    def test_multi_13(self):
        self.run_test_multi(["Message with unicode chars: %s and '…' and ascii", "àbc"])

    def test_multi_14(self):
        self.run_test_multi(["Message %.3f %s %.3f", 1.234, "--->", 2.345])

    def test_multi_15(self):
        self.run_test_multi(["Message %.3f %s %.3f", 1.234, "-à->", 2.345])

    def test_loggable(self):
        loggable = Loggable()
        self.assertIsNotNone(loggable.rconf)
        self.assertIsNotNone(loggable.logger)

    def test_loggable_logger(self):
        logger = Logger()
        loggable = Loggable(logger=logger)
        self.assertIsNotNone(loggable.rconf)
        self.assertEqual(logger, loggable.logger)

    def test_loggable_rconf(self):
        rconf = RuntimeConfiguration()
        loggable = Loggable(rconf=rconf)
        self.assertEqual(rconf, loggable.rconf)
        self.assertIsNotNone(loggable.logger)

    def test_loggable_rconf_logger(self):
        logger = Logger()
        rconf = RuntimeConfiguration()
        loggable = Loggable(rconf=rconf, logger=logger)
        self.assertEqual(rconf, loggable.rconf)
        self.assertEqual(logger, loggable.logger)

    def test_loggable_log(self):
        loggable = Loggable()
        loggable.log("Message")
        self.assertEqual(len(loggable.logger), 1)

    def test_loggable_log_crit(self):
        loggable = Loggable()
        loggable.log_crit("Message")
        self.assertEqual(len(loggable.logger), 1)

    def test_loggable_log_warn(self):
        loggable = Loggable()
        loggable.log_warn("Message")
        self.assertEqual(len(loggable.logger), 1)

    def test_loggable_log_info(self):
        loggable = Loggable()
        loggable.log_info("Message")
        self.assertEqual(len(loggable.logger), 1)

    def test_loggable_log_exc_warn(self):
        loggable = Loggable()
        loggable.log_exc("Message", None, False, None)
        self.assertEqual(len(loggable.logger), 1)

    def test_loggable_log_exc_crit_no_raise(self):
        loggable = Loggable()
        loggable.log_exc("Message", None, True, None)
        self.assertEqual(len(loggable.logger), 1)

    def test_loggable_log_exc_crit_raise(self):
        loggable = Loggable()
        with self.assertRaises(TypeError):
            loggable.log_exc("Message", None, True, TypeError)
            self.assertEqual(len(loggable.logger), 1)

    def test_loggable_log_exc_obj(self):
        loggable = Loggable()
        exc = TypeError("Message")
        with self.assertRaises(TypeError):
            loggable.log_exc("Message", exc, True, TypeError)
            self.assertEqual(len(loggable.logger), 1)


if __name__ == "__main__":
    unittest.main()
