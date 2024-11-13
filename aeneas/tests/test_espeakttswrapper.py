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

import itertools

from aeneas.tests.base_ttswrapper import BaseTTSWrapperCase, SynthesizeCase
from aeneas.ttswrappers.espeakttswrapper import ESPEAKTTSWrapper


class TestESPEAKTTSWrapper(BaseTTSWrapperCase):
    TTS = "espeak"
    TTS_PATH = "/usr/bin/espeak"
    TTS_CLASS = ESPEAKTTSWrapper
    TTS_LANGUAGE = ESPEAKTTSWrapper.ENG
    TTS_LANGUAGE_VARIATION = ESPEAKTTSWrapper.ENG_GBR

    def iter_synthesize_cases(self):
        for v in itertools.product([True, False], repeat=3):
            yield SynthesizeCase(*v)

    def test_multiple_replace_language(self):
        tfl = self.tfl(
            [(ESPEAKTTSWrapper.UKR, ["Временами Сашке хотелось перестать делать то"])]
        )
        self.synthesize(tfl)

    def test_multiple_replace_language_mixed(self):
        tfl = self.tfl(
            [
                (ESPEAKTTSWrapper.UKR, ["Word"]),
                (
                    ESPEAKTTSWrapper.UKR,
                    ["Временами Сашке хотелось перестать делать то"],
                ),
                (ESPEAKTTSWrapper.UKR, ["Word"]),
            ]
        )
        self.synthesize(tfl)

    def test_multiple_replace_language_mixed_fragments(self):
        tfl = self.tfl(
            [
                (ESPEAKTTSWrapper.ENG, ["Word"]),
                (
                    ESPEAKTTSWrapper.UKR,
                    ["Временами Сашке хотелось перестать делать то"],
                ),
                (ESPEAKTTSWrapper.ENG, ["Word"]),
            ]
        )
        self.synthesize(tfl)
