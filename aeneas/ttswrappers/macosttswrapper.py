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

"""
This module contains the following classes:

* :class:`~aeneas.ttswrappers.macosttswrapper.MacOSTTSWrapper`,
  a wrapper for the ``macOS`` "say" TTS engine.

Please refer to
https://developer.apple.com/library/content/documentation/UserExperience/Conceptual/SpeechSynthesisProgrammingGuide/SpeechOverview/SpeechOverview.html
for further details.
"""

from aeneas.language import Language
from aeneas.ttswrappers.basettswrapper import BaseTTSWrapper


class MacOSTTSWrapper(BaseTTSWrapper):
    """
    A wrapper for the ``macOS`` TTS engine.

    This wrapper supports calling the TTS engine
    via ``subprocess``.

    Future support for calling via Python C extension
    is planned.

    In abstract terms, it performs one or more calls like ::

        $ say -v voice_name -o /tmp/output_file.wav --data-format LEF32@22050 < text

    To use this TTS engine, specify ::

        "tts=macos"

    in the ``RuntimeConfiguration`` object.

    See :class:`~aeneas.ttswrappers.basettswrapper.BaseTTSWrapper`
    for the available functions.
    Below are listed the languages supported by this wrapper.

    :param rconf: a runtime configuration
    :type  rconf: :class:`~aeneas.runtimeconfiguration.RuntimeConfiguration`
    :param logger: the logger object
    :type  logger: :class:`~aeneas.logger.Logger`
    """

    ARA = Language.ARA
    """ Arabic """

    CES = Language.CES
    """ Czech """

    DAN = Language.DAN
    """ Danish """

    DEU = Language.DEU
    """ German """

    ELL = Language.ELL
    """ Greek (Modern) """

    ENG = Language.ENG
    """ English """

    FIN = Language.FIN
    """ Finnish """

    FRA = Language.FRA
    """ French """

    HEB = Language.HEB
    """ Hebrew """

    HIN = Language.HIN
    """ Hindi """

    HUN = Language.HUN
    """ Hungarian """

    IND = Language.IND
    """ Indonesian """

    ITA = Language.ITA
    """ Italian """

    JPN = Language.JPN
    """ Japanese """

    KOR = Language.KOR
    """ Korean """

    NLD = Language.NLD
    """ Dutch """

    NOR = Language.NOR
    """ Norwegian """

    POL = Language.POL
    """ Polish """

    POR = Language.POR
    """ Portuguese """

    RON = Language.RON
    """ Romanian """

    RUS = Language.RUS
    """ Russian """

    SLK = Language.SLK
    """ Slovak """

    SPA = Language.SPA
    """ Spanish """

    SWE = Language.SWE
    """ Swedish """

    THA = Language.THA
    """ Thai """

    TUR = Language.TUR
    """ Turkish """

    ZHO = Language.ZHO
    """ Chinese """

    ENG_GBR = "eng-GBR"
    """ English (GB) """

    CODE_TO_HUMAN = {
        ARA: "Arabic",
        CES: "Czech",
        DAN: "Danish",
        DEU: "German",
        ELL: "Greek (Modern)",
        ENG: "English",
        FIN: "Finnish",
        FRA: "French",
        HEB: "Hebrew",
        HIN: "Hindi",
        HUN: "Hungarian",
        IND: "Indonesian",
        ITA: "Italian",
        JPN: "Japanese",
        KOR: "Korean",
        NLD: "Dutch",
        NOR: "Norwegian",
        POL: "Polish",
        POR: "Portuguese",
        RON: "Romanian",
        RUS: "Russian",
        SLK: "Slovak",
        SPA: "Spanish",
        SWE: "Swedish",
        THA: "Thai",
        TUR: "Turkish",
        ZHO: "Chinese",
        ENG_GBR: "English (GB)",
    }

    CODE_TO_HUMAN_LIST = sorted([f"{k}\t{v}" for k, v in CODE_TO_HUMAN.items()])

    LANGUAGE_TO_VOICE_CODE = {
        ARA: "Maged",
        CES: "Zuzana",
        DAN: "Sara",
        DEU: "Anna",
        ELL: "Melina",
        ENG: "Alex",
        FIN: "Satu",
        FRA: "Thomas",
        HEB: "Carmit",
        HIN: "Lekha",
        HUN: "Mariska",
        IND: "Damayanti",
        ITA: "Alice",
        JPN: "Kyoko",
        KOR: "Yuna",
        NLD: "Xander",
        NOR: "Nora",
        POL: "Zosia",
        POR: "Luciana",
        RON: "Ioana",
        RUS: "Yuri",
        SLK: "Laura",
        SPA: "Juan",
        SWE: "Alva",
        THA: "Kanya",
        TUR: "Yelda",
        ZHO: "Ting-Ting",
        ENG_GBR: "Daniel",
    }
    DEFAULT_LANGUAGE = ENG

    OUTPUT_AUDIO_FORMAT = ("pcm_s16le", 1, 22050)

    HAS_SUBPROCESS_CALL = True

    TAG = "MacOSTTSWrapper"

    def __init__(self, rconf=None, logger=None):
        super().__init__(rconf=rconf, logger=logger)

        self.set_subprocess_arguments(
            [
                "say",  # path to say
                "-v",  # append "-v"
                self.CLI_PARAMETER_VOICE_CODE_STRING,  # it will be replaced by the actual voice code
                "-o",  # append "-o"
                self.CLI_PARAMETER_WAVE_PATH,  # it will be replaced by the actual output file
                self.CLI_PARAMETER_TEXT_STDIN,  # text is read from stdin,
                "--data-format",  # set output data format
                "LEF32@22050",  # data format string
            ]
        )
