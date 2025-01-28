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

from aeneas.exacttiming import TimeValue
from aeneas.ffprobewrapper import FFPROBEUnsupportedFormatError, FFPROBEWrapper
import aeneas.globalfunctions as gf


class TestFFPROBEWrapper(unittest.TestCase):
    FILES = (
        "res/audioformats/p001.aac",
        "res/audioformats/p001.aiff",
        "res/audioformats/p001.flac",
        "res/audioformats/p001.mp3",
        "res/audioformats/p001.mp4",
        "res/audioformats/p001.ogg",
        "res/audioformats/p001.wav",
        "res/audioformats/p001.webm",
    )

    NOT_EXISTING_PATH = "this_file_does_not_exist.mp3"
    EMPTY_FILE_PATH = "res/audioformats/p001.empty"

    def read_properties(self, input_file_path):
        return FFPROBEWrapper().read_properties(
            gf.absolute_path(input_file_path, __file__)
        )

    def test_mp3_properties(self):
        properties = self.read_properties("res/audioformats/p001.mp3")
        self.assertAlmostEqual(properties.duration, TimeValue("9.038"), places=2)
        self.assertEqual(properties.codec_name, "mp3")
        self.assertEqual(properties.sample_rate, 44_100)
        self.assertEqual(properties.channels, 2)
        self.assertEqual(properties.bit_rate, 64_000)

    def test_path_none(self):
        with self.assertRaises(TypeError):
            self.read_properties(None)

    def test_path_not_existing(self):
        with self.assertRaises(OSError):
            self.read_properties(self.NOT_EXISTING_PATH)

    def test_file_empty(self):
        with self.assertRaises(FFPROBEUnsupportedFormatError):
            self.read_properties(self.EMPTY_FILE_PATH)

    def test_formats(self):
        for path in self.FILES:
            with self.subTest(path=path):
                properties = self.read_properties(path)
                self.assertIsNotNone(properties.duration)
