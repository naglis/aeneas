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

* :class:`~aeneas.ttswrappers.festivalttswrapper.FESTIVALTTSWrapper`,
  a wrapper for the ``Festival`` TTS engine.

Please refer to
http://www.cstr.ed.ac.uk/projects/festival/
for further details.
"""

from aeneas.exacttiming import TimeValue
from aeneas.language import Language
from aeneas.ttswrappers.basettswrapper import BaseTTSWrapper
import aeneas.globalfunctions as gf


class FESTIVALTTSWrapper(BaseTTSWrapper):
    """
    A wrapper for the ``Festival`` TTS engine.

    This wrapper supports calling the TTS engine
    via ``subprocess`` or via Python C++ extension.

    .. warning::
        The C++ extension call is experimental and
        probably works only on Linux at the moment.

    In abstract terms, it performs one or more calls like ::

        $ echo text | text2wave -eval "(language_italian)" -o output_file.wav

    To use this TTS engine, specify ::

        "tts=festival"

    in the ``RuntimeConfiguration`` object.
    To execute from a non-default location: ::

        "tts=festival|tts_path=/path/to/wave2text"

    See :class:`~aeneas.ttswrappers.basettswrapper.BaseTTSWrapper`
    for the available functions.
    Below are listed the languages supported by this wrapper.

    :param rconf: a runtime configuration
    :type  rconf: :class:`~aeneas.runtimeconfiguration.RuntimeConfiguration`
    :param logger: the logger object
    :type  logger: :class:`~aeneas.logger.Logger`
    """

    CES = Language.CES
    """ Czech """

    CYM = Language.CYM
    """ Welsh """

    ENG = Language.ENG
    """ English """

    FIN = Language.FIN
    """ Finnish """

    ITA = Language.ITA
    """ Italian """

    RUS = Language.RUS
    """ Russian """

    SPA = Language.SPA
    """ Spanish """

    ENG_GBR = "eng-GBR"
    """ English (GB) """

    ENG_SCT = "eng-SCT"
    """ English (Scotland) """

    ENG_USA = "eng-USA"
    """ English (USA) """

    LANGUAGE_TO_VOICE_CODE = {
        CES: CES,
        CYM: CYM,
        ENG: ENG,
        SPA: SPA,
        FIN: FIN,
        ITA: ITA,
        RUS: RUS,
        ENG_GBR: ENG_GBR,
        ENG_SCT: ENG_SCT,
        ENG_USA: ENG_USA,
    }
    DEFAULT_LANGUAGE = ENG_USA

    CODE_TO_HUMAN = {
        CES: "Czech",
        CYM: "Welsh",
        ENG: "English",
        FIN: "Finnish",
        ITA: "Italian",
        RUS: "Russian",
        SPA: "Spanish",
        ENG_GBR: "English (GB)",
        ENG_SCT: "English (Scotland)",
        ENG_USA: "English (USA)",
    }

    CODE_TO_HUMAN_LIST = sorted([f"{k}\t{v}" for k, v in CODE_TO_HUMAN.items()])

    VOICE_CODE_TO_SUBPROCESS = {
        CES: "(language_czech)",
        CYM: "(language_welsh)",
        ENG: "(language_english)",
        ENG_GBR: "(language_british_english)",
        ENG_SCT: "(language_scots_gaelic)",
        ENG_USA: "(language_american_english)",
        SPA: "(language_castillian_spanish)",
        FIN: "(language_finnish)",
        ITA: "(language_italian)",
        RUS: "(language_russian)",
    }

    DEFAULT_TTS_PATH = "text2wave"

    OUTPUT_AUDIO_FORMAT = ("pcm_s16le", 1, 16000)

    HAS_SUBPROCESS_CALL = True

    HAS_C_EXTENSION_CALL = True

    C_EXTENSION_NAME = "cfw"

    TAG = "FESTIVALTTSWrapper"

    def __init__(self, rconf=None, logger=None):
        super().__init__(rconf=rconf, logger=logger)
        self.set_subprocess_arguments(
            [
                self.tts_path,
                self.CLI_PARAMETER_VOICE_CODE_FUNCTION,
                "-o",
                self.CLI_PARAMETER_WAVE_PATH,
                self.CLI_PARAMETER_TEXT_STDIN,
            ]
        )

    def _voice_code_to_subprocess(self, voice_code):
        return ["-eval", self.VOICE_CODE_TO_SUBPROCESS[voice_code]]

    def _synthesize_multiple_c_extension(
        self, text_file, output_file_path, quit_after=None, backwards=False
    ):
        """
        Synthesize multiple text fragments, using the cfw extension.

        Return a tuple (anchors, total_time, num_chars).

        :rtype: (bool, (list, :class:`~aeneas.exacttiming.TimeValue`, int))
        """
        self.log("Synthesizing using C extension...")

        # convert parameters from Python values to C values
        try:
            c_quit_after = float(quit_after)
        except TypeError:
            c_quit_after = 0.0
        c_backwards = 0
        if backwards:
            c_backwards = 1
        self.log(["output_file_path: %s", output_file_path])
        self.log(["c_quit_after:     %.3f", c_quit_after])
        self.log(["c_backwards:      %d", c_backwards])
        self.log("Preparing u_text...")
        u_text = []
        fragments = text_file.fragments
        for fragment in fragments:
            f_lang = fragment.language
            f_text = fragment.filtered_text
            if f_lang is None:
                f_lang = self.DEFAULT_LANGUAGE
            f_voice_code = self.VOICE_CODE_TO_SUBPROCESS[
                self._language_to_voice_code(f_lang)
            ]
            if f_text is None:
                f_text = ""
            u_text.append((f_voice_code, f_text))
        self.log("Preparing u_text... done")

        # call C extension
        sr = None
        sf = None
        intervals = None

        self.log("Preparing c_text...")
        c_text = [(gf.safe_unicode(t[0]), gf.safe_unicode(t[1])) for t in u_text]
        self.log("Preparing c_text... done")

        self.log("Calling aeneas.cfw directly")
        try:
            self.log("Importing aeneas.cfw...")
            import aeneas.cfw.cfw

            self.log("Importing aeneas.cfw... done")
            self.log("Calling aeneas.cfw...")
            sr, sf, intervals = aeneas.cfw.cfw.synthesize_multiple(
                output_file_path, c_quit_after, c_backwards, c_text
            )
            self.log("Calling aeneas.cfw... done")
        except Exception as exc:
            self.log_exc(
                "An unexpected error occurred while running cfw", exc, False, None
            )
            return (False, None)

        self.log(["sr: %d", sr])
        self.log(["sf: %d", sf])

        # create output
        anchors = []
        current_time = TimeValue("0.000")
        num_chars = 0
        if backwards:
            fragments = fragments[::-1]
        for i in range(sf):
            # get the correct fragment
            fragment = fragments[i]
            # store for later output
            anchors.append(
                [
                    TimeValue(intervals[i][0]),
                    fragment.identifier,
                    fragment.filtered_text,
                ]
            )
            # increase the character counter
            num_chars += fragment.characters
            # update current_time
            current_time = TimeValue(intervals[i][1])

        # return output
        # NOTE anchors do not make sense if backwards == True
        self.log(["Returning %d time anchors", len(anchors)])
        self.log(["Current time %.3f", current_time])
        self.log(["Synthesized %d characters", num_chars])
        self.log("Synthesizing using C extension... done")
        return (True, (anchors, current_time, num_chars))
