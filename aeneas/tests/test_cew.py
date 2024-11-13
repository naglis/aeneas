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
import importlib.util
import tempfile


@unittest.skipIf(
    importlib.util.find_spec("aeneas.cew.cew") is None,
    "CEW C extension is not available",
)
class TestCEW(unittest.TestCase):
    def test_cew_synthesize_multiple(self):
        c_quit_after = 0.0
        c_backwards = 0
        c_text = [
            ("en", "Dummy 1"),  # NOTE cew requires the actual eSpeak voice code
            ("en", "Dummy 2"),  # NOTE cew requires the actual eSpeak voice code
            ("en", "Dummy 3"),  # NOTE cew requires the actual eSpeak voice code
        ]
        import aeneas.cew.cew

        with tempfile.NamedTemporaryFile(suffix=".wav") as tmp_file:
            sr, sf, intervals = aeneas.cew.cew.synthesize_multiple(
                tmp_file.name, c_quit_after, c_backwards, c_text
            )

        self.assertEqual(sr, 22050)
        self.assertEqual(sf, 3)
        self.assertEqual(len(intervals), 3)

    def test_cew_synthesize_multiple_lang(self):
        c_quit_after = 0.0
        c_backwards = 0
        c_text = [
            ("en", "Dummy 1"),  # NOTE cew requires the actual eSpeak voice code
            (
                "it",
                "Segnaposto 2",
            ),  # NOTE cew requires the actual eSpeak voice code
            ("en", "Dummy 3"),  # NOTE cew requires the actual eSpeak voice code
        ]
        import aeneas.cew.cew

        with tempfile.NamedTemporaryFile(suffix=".wav") as tmp_file:
            sr, sf, intervals = aeneas.cew.cew.synthesize_multiple(
                tmp_file.name, c_quit_after, c_backwards, c_text
            )

        self.assertEqual(sr, 22050)
        self.assertEqual(sf, 3)
        self.assertEqual(len(intervals), 3)
