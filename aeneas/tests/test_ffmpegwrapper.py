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

import os
import unittest
import tempfile
import contextlib

from aeneas.ffmpegwrapper import FFMPEGWrapper
from aeneas.runtimeconfiguration import RuntimeConfiguration
import aeneas.globalfunctions as gf


class TestFFMPEGWrapper(unittest.TestCase):
    FILES = [
        {
            "path": "res/audioformats/p001.aac",
        },
        {
            "path": "res/audioformats/p001.aiff",
        },
        {
            "path": "res/audioformats/p001.flac",
        },
        {
            "path": "res/audioformats/p001.mp3",
        },
        {
            "path": "res/audioformats/p001.mp4",
        },
        {
            "path": "res/audioformats/p001.ogg",
        },
        {
            "path": "res/audioformats/p001.wav",
        },
        {
            "path": "res/audioformats/p001.webm",
        },
    ]

    CANNOT_BE_WRITTEN_PATH = "x/y/z/cannot_be_written.wav"
    NOT_EXISTING_PATH = "this_file_does_not_exist.mp3"
    EMPTY_FILE_PATH = "res/audioformats/p001.empty"

    def convert(self, input_file_path, *, ofp=None, runtime_configuration=None):
        with contextlib.ExitStack() as exit_stack:
            if ofp is None:
                tmp_dir = tempfile.TemporaryDirectory()
                exit_stack.enter_context(tmp_dir)
                output_path = tmp_dir.name
                output_file_path = os.path.join(output_path, "audio.wav")
            else:

                @contextlib.contextmanager
                def delete_file(path):
                    try:
                        yield
                    finally:
                        gf.delete_file(None, path)

                exit_stack.enter_context(delete_file(ofp))
                output_file_path = ofp

            converter = FFMPEGWrapper(rconf=runtime_configuration)
            result = converter.convert(
                gf.absolute_path(input_file_path, __file__), output_file_path
            )
            self.assertEqual(result, output_file_path)

    def test_convert(self):
        for f in self.FILES:
            with self.subTest(path=f["path"]):
                self.convert(f["path"])

    def test_convert_with_runtime_config(self):
        rc = RuntimeConfiguration("ffmpeg_sample_rate=44100")
        for f in self.FILES:
            with self.subTest(path=f["path"]):
                self.convert(f["path"], runtime_configuration=rc)

    def test_not_existing(self):
        with self.assertRaises(OSError):
            self.convert(self.NOT_EXISTING_PATH)

    def test_empty(self):
        with self.assertRaises(OSError):
            self.convert(self.EMPTY_FILE_PATH)

    def test_cannot_be_written(self):
        with self.assertRaises(OSError):
            self.convert(self.FILES[0]["path"], ofp=self.CANNOT_BE_WRITTEN_PATH)
