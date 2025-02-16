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

import itertools
import tempfile

from aeneas.exacttiming import TimeValue
from aeneas.language import Language
from aeneas.runtimeconfiguration import RuntimeConfiguration
from aeneas.synthesizer import Synthesizer
from aeneas.textfile import TextFile, TextFileFormat
import aeneas.globalfunctions as gf

from .common import BaseCase


class TestSynthesizer(BaseCase):
    PATH_NOT_WRITEABLE = gf.absolute_path("x/y/z/not_writeable.wav", __file__)

    def perform(
        self,
        path: str,
        expected_anchors: int,
        *,
        expected_total_time: TimeValue | None = None,
        quit_after: TimeValue | None = None,
        backwards: bool = False,
    ):
        def inner(c_ext: bool, cew_subprocess: bool, tts_cache: bool):
            tfl = TextFile(gf.absolute_path(path, __file__), TextFileFormat.PLAIN)
            tfl.set_language(Language.ENG)

            synth_rconf = RuntimeConfiguration()
            synth_rconf[RuntimeConfiguration.C_EXTENSIONS] = c_ext
            synth_rconf[RuntimeConfiguration.CEW_SUBPROCESS_ENABLED] = cew_subprocess
            synth_rconf[RuntimeConfiguration.TTS_CACHE] = tts_cache
            synth = Synthesizer.from_rconf(synth_rconf)

            with tempfile.NamedTemporaryFile(suffix=".wav") as tmp_file:
                anchors, total_time, _ = synth.synthesize(
                    tfl, tmp_file.name, quit_after=quit_after, backwards=backwards
                )
            self.assertEqual(len(anchors), expected_anchors)
            if expected_total_time is not None:
                self.assertAlmostEqual(total_time, expected_total_time, places=0)

        for c_ext, cew_subprocess, tts_cache in itertools.product(
            [True, False], repeat=3
        ):
            inner(c_ext, cew_subprocess, tts_cache)

    def test_clear_cache(self):
        synth = Synthesizer.from_rconf(RuntimeConfiguration())
        synth.clear_cache()

    def test_synthesize_none(self):
        synth = Synthesizer.from_rconf(RuntimeConfiguration())
        with self.assertRaises(TypeError):
            synth.synthesize(None, self.PATH_NOT_WRITEABLE)

    def test_synthesize_invalid_text_file(self):
        synth = Synthesizer.from_rconf(RuntimeConfiguration())
        with self.assertRaises(TypeError):
            synth.synthesize("foo", self.PATH_NOT_WRITEABLE)

    def test_synthesize(self):
        self.perform("res/inputtext/sonnet_plain.txt", 15)

    def test_synthesize_unicode(self):
        self.perform("res/inputtext/sonnet_plain_utf8.txt", 15)

    def test_synthesize_quit_after(self):
        self.perform(
            "res/inputtext/sonnet_plain.txt",
            6,
            expected_total_time=TimeValue("12.000"),
            quit_after=TimeValue("10.000"),
        )

    def test_synthesize_backwards(self):
        self.perform("res/inputtext/sonnet_plain.txt", 15, backwards=True)

    def test_synthesize_quit_after_backwards(self):
        self.perform(
            "res/inputtext/sonnet_plain.txt",
            4,
            expected_total_time=TimeValue("10.000"),
            quit_after=TimeValue("10.000"),
            backwards=True,
        )

    def test_synthesize_plain_with_empty_lines(self):
        self.perform("res/inputtext/plain_with_empty_lines.txt", 19)
