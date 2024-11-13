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
import os
import tempfile
import contextlib
import typing

from aeneas.exacttiming import TimeValue
from aeneas.textfile import TextFile, TextFragment
from aeneas.ttswrappers.basettswrapper import BaseTTSWrapper
from aeneas.runtimeconfiguration import RuntimeConfiguration


class SynthesizeCase(typing.NamedTuple):
    c_ext: bool
    cew_subprocess: bool
    cache: bool


class TestBaseTTSWrapper(unittest.TestCase):
    def test_not_implemented(self):
        with self.assertRaises(NotImplementedError):
            BaseTTSWrapper()


class BaseTTSWrapperCase(unittest.TestCase):
    TTS = ""
    TTS_PATH = ""

    TTS_CLASS: typing.ClassVar = BaseTTSWrapper
    TTS_LANGUAGE: typing.ClassVar[str] = "eng"
    TTS_LANGUAGE_VARIATION: typing.ClassVar[str | None] = None

    def synthesize(
        self,
        text_file,
        ofp: str | None = None,
        quit_after: TimeValue | None = None,
        backwards: bool = False,
        zero_length: bool = False,
        expected_exc=None,
    ):
        if not self.TTS:
            self.skipTest("`self.TTS` is not set")
        elif not self.TTS_PATH:
            self.skipTest("`self.TTS_PATH` is not set")
        elif not os.path.isfile(self.TTS_PATH):
            self.skipTest(f"`self.TTS_PATH` ({self.TTS_PATH}) does not exist")

        def inner(case: SynthesizeCase):
            with contextlib.ExitStack() as exit_stack:
                if ofp is None:
                    tmp_file = tempfile.NamedTemporaryFile(suffix=".wav")
                    exit_stack.enter_context(tmp_file)
                    output_file_path = tmp_file.name
                else:
                    output_file_path = ofp

                try:
                    rconf = RuntimeConfiguration()
                    rconf[RuntimeConfiguration.TTS] = self.TTS
                    rconf[RuntimeConfiguration.TTS_PATH] = self.TTS_PATH
                    rconf[RuntimeConfiguration.C_EXTENSIONS] = case.c_ext
                    rconf[RuntimeConfiguration.CEW_SUBPROCESS_ENABLED] = (
                        case.cew_subprocess
                    )
                    rconf[RuntimeConfiguration.TTS_CACHE] = case.cache
                    tts_engine = self.TTS_CLASS(rconf=rconf)
                    anchors, total_time, num_chars = tts_engine.synthesize_multiple(
                        text_file, output_file_path, quit_after, backwards
                    )
                    if case.cache:
                        tts_engine.clear_cache()

                    if zero_length:
                        self.assertEqual(total_time, 0.0)
                    else:
                        self.assertGreater(total_time, 0.0)

                except (OSError, TypeError, UnicodeDecodeError, ValueError) as exc:
                    if case.cache and tts_engine is not None:
                        tts_engine.clear_cache()
                    with self.assertRaises(expected_exc):
                        raise exc

        for case in self.iter_synthesize_cases():
            with self.subTest(case=case):
                inner(case)

    def iter_synthesize_cases(self) -> typing.Iterator[SynthesizeCase]:
        yield SynthesizeCase(c_ext=True, cew_subprocess=False, cache=True)
        yield SynthesizeCase(c_ext=True, cew_subprocess=False, cache=False)

    def tfl(self, frags):
        tfl = TextFile()
        for language, lines in frags:
            tfl.add_fragment(
                TextFragment(language=language, lines=lines, filtered_lines=lines)
            )
        return tfl

    def test_use_cache(self):
        if self.TTS == "":
            self.skipTest("`self.TTS` is not set")
        rconf = RuntimeConfiguration()
        rconf[RuntimeConfiguration.TTS_CACHE] = True
        tts_engine = self.TTS_CLASS(rconf=rconf)
        self.assertTrue(tts_engine.use_cache)
        self.assertIsNotNone(tts_engine.cache)

    def test_clear_cache(self):
        if self.TTS == "":
            self.skipTest("`self.TTS` is not set")
        tts_engine = self.TTS_CLASS()
        tts_engine.clear_cache()

    def test_tfl_none(self):
        self.synthesize(None, zero_length=True, expected_exc=TypeError)

    def test_invalid_output_path(self):
        tfl = self.tfl([(self.TTS_LANGUAGE, ["word"])])
        self.synthesize(tfl, ofp="x/y/z/not_existing.wav", expected_exc=OSError)

    def test_no_fragments(self):
        tfl = TextFile()
        tfl.set_language(self.TTS_LANGUAGE)
        self.synthesize(tfl, expected_exc=ValueError)

    def test_unicode_ascii(self):
        tfl = self.tfl([(self.TTS_LANGUAGE, ["word"])])
        self.synthesize(tfl)

    def test_unicode_unicode(self):
        tfl = self.tfl([(self.TTS_LANGUAGE, ["Ausführliche"])])
        self.synthesize(tfl)

    def test_empty(self):
        tfl = self.tfl([(self.TTS_LANGUAGE, [""])])
        self.synthesize(tfl, expected_exc=ValueError)

    def test_empty_multiline(self):
        tfl = self.tfl([(self.TTS_LANGUAGE, ["", "", ""])])
        self.synthesize(tfl, expected_exc=ValueError)

    def test_empty_fragments(self):
        tfl = self.tfl(
            [
                (self.TTS_LANGUAGE, [""]),
                (self.TTS_LANGUAGE, [""]),
                (self.TTS_LANGUAGE, [""]),
            ]
        )
        self.synthesize(tfl, expected_exc=ValueError)

    def test_empty_mixed(self):
        tfl = self.tfl([(self.TTS_LANGUAGE, ["Word", "", "Word"])])
        self.synthesize(tfl)

    def test_empty_mixed_fragments(self):
        tfl = self.tfl(
            [
                (self.TTS_LANGUAGE, ["Word"]),
                (self.TTS_LANGUAGE, [""]),
                (self.TTS_LANGUAGE, ["Word"]),
            ]
        )
        self.synthesize(tfl)

    def test_invalid_language(self):
        tfl = self.tfl([("zzzz", ["Word"])])
        self.synthesize(tfl, expected_exc=ValueError)

    def test_variation_language(self):
        if self.TTS_LANGUAGE_VARIATION is None:
            self.skipTest("`self.TTS_LANGUAGE_VARIATION` is not set")

        tfl = self.tfl([(self.TTS_LANGUAGE_VARIATION, ["Word"])])
        self.synthesize(tfl)
