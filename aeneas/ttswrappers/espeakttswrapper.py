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

* :class:`~aeneas.ttswrappers.espeakttswrapper.ESPEAKTTSWrapper`,
  a wrapper for the ``eSpeak`` TTS engine.

Please refer to
http://espeak.sourceforge.net/
for further details.
"""

import logging

from aeneas.exacttiming import TimeValue
from aeneas.language import Language
from aeneas.runtimeconfiguration import RuntimeConfiguration
from aeneas.ttswrappers.basettswrapper import BaseTTSWrapper
import aeneas.globalfunctions as gf

logger = logging.getLogger(__name__)


class ESPEAKTTSWrapper(BaseTTSWrapper):
    """
    A wrapper for the ``eSpeak`` TTS engine.

    This wrapper is the default TTS engine for ``aeneas``.

    This wrapper supports calling the TTS engine
    via ``subprocess`` or via Python C extension.

    In abstract terms, it performs one or more calls like ::

        $ espeak -v voice_code -w /tmp/output_file.wav < text

    To use this TTS engine, specify ::

        "tts=espeak"

    in the ``RuntimeConfiguration`` object.
    (You can omit this, since eSpeak is the default TTS engine.)
    To execute from a non-default location: ::

        "tts=espeak|tts_path=/path/to/espeak"

    To run the ``cew`` Python C extension
    in a separate process via
    :class:`~aeneas.cewsubprocess.CEWSubprocess`, use ::

        "cew_subprocess_enabled=True|cew_subprocess_path=/path/to/python"

    in the ``rconf`` object.

    See :class:`~aeneas.ttswrappers.basettswrapper.BaseTTSWrapper`
    for the available functions.
    Below are listed the languages supported by this wrapper.

    :param rconf: a runtime configuration
    :type  rconf: :class:`~aeneas.runtimeconfiguration.RuntimeConfiguration`
    """

    AFR = Language.AFR
    """ Afrikaans """

    ARG = Language.ARG
    """ Aragonese (not tested) """

    BOS = Language.BOS
    """ Bosnian (not tested) """

    BUL = Language.BUL
    """ Bulgarian """

    CAT = Language.CAT
    """ Catalan """

    CES = Language.CES
    """ Czech """

    CMN = Language.CMN
    """ Mandarin Chinese (not tested) """

    CYM = Language.CYM
    """ Welsh """

    DAN = Language.DAN
    """ Danish """

    DEU = Language.DEU
    """ German """

    ELL = Language.ELL
    """ Greek (Modern) """

    ENG = Language.ENG
    """ English """

    EPO = Language.EPO
    """ Esperanto (not tested) """

    EST = Language.EST
    """ Estonian """

    FAS = Language.FAS
    """ Persian """

    FIN = Language.FIN
    """ Finnish """

    FRA = Language.FRA
    """ French """

    GLE = Language.GLE
    """ Irish """

    GRC = Language.GRC
    """ Greek (Ancient) """

    HIN = Language.HIN
    """ Hindi (not tested) """

    HRV = Language.HRV
    """ Croatian """

    HUN = Language.HUN
    """ Hungarian """

    HYE = Language.HYE
    """ Armenian (not tested) """

    IND = Language.IND
    """ Indonesian (not tested) """

    ISL = Language.ISL
    """ Icelandic """

    ITA = Language.ITA
    """ Italian """

    JBO = Language.JBO
    """ Lojban (not tested) """

    KAN = Language.KAN
    """ Kannada (not tested) """

    KAT = Language.KAT
    """ Georgian (not tested) """

    KUR = Language.KUR
    """ Kurdish (not tested) """

    LAT = Language.LAT
    """ Latin """

    LAV = Language.LAV
    """ Latvian """

    LFN = Language.LFN
    """ Lingua Franca Nova (not tested) """

    LIT = Language.LIT
    """ Lithuanian """

    MAL = Language.MAL
    """ Malayalam (not tested) """

    MKD = Language.MKD
    """ Macedonian (not tested) """

    MSA = Language.MSA
    """ Malay (not tested) """

    NEP = Language.NEP
    """ Nepali (not tested) """

    NLD = Language.NLD
    """ Dutch """

    NOR = Language.NOR
    """ Norwegian """

    PAN = Language.PAN
    """ Panjabi (not tested) """

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

    SQI = Language.SQI
    """ Albanian (not tested) """

    SRP = Language.SRP
    """ Serbian """

    SWA = Language.SWA
    """ Swahili """

    SWE = Language.SWE
    """ Swedish """

    TAM = Language.TAM
    """ Tamil (not tested) """

    TUR = Language.TUR
    """ Turkish """

    UKR = Language.UKR
    """ Ukrainian """

    VIE = Language.VIE
    """ Vietnamese (not tested) """

    YUE = Language.YUE
    """ Yue Chinese (not tested) """

    ZHO = Language.ZHO
    """ Chinese (not tested) """

    ENG_GBR = "eng-GBR"
    """ English (GB) """

    ENG_SCT = "eng-SCT"
    """ English (Scotland) (not tested) """

    ENG_USA = "eng-USA"
    """ English (USA) """

    SPA_ESP = "spa-ESP"
    """ Spanish (Castillan) """

    FRA_BEL = "fra-BEL"
    """ French (Belgium) (not tested) """

    FRA_FRA = "fra-FRA"
    """ French (France) """

    POR_BRA = "por-bra"
    """ Portuguese (Brazil) (not tested) """

    POR_PRT = "por-prt"
    """ Portuguese (Portugal) """

    AF = "af"
    """ Afrikaans """

    AN = "an"
    """ Aragonese (not tested) """

    BG = "bg"
    """ Bulgarian """

    BS = "bs"
    """ Bosnian (not tested) """

    CA = "ca"
    """ Catalan """

    CS = "cs"
    """ Czech """

    CY = "cy"
    """ Welsh """

    DA = "da"
    """ Danish """

    DE = "de"
    """ German """

    EL = "el"
    """ Greek (Modern) """

    EN = "en"
    """ English """

    EN_GB = "en-gb"
    """ English (GB) """

    EN_SC = "en-sc"
    """ English (Scotland) (not tested) """

    EN_UK_NORTH = "en-uk-north"
    """ English (Northern) (not tested) """

    EN_UK_RP = "en-uk-rp"
    """ English (Received Pronunciation) (not tested) """

    EN_UK_WMIDS = "en-uk-wmids"
    """ English (Midlands) (not tested) """

    EN_US = "en-us"
    """ English (USA) """

    EN_WI = "en-wi"
    """ English (West Indies) (not tested) """

    EO = "eo"
    """ Esperanto (not tested) """

    ES = "es"
    """ Spanish (Castillan) """

    ES_LA = "es-la"
    """ Spanish (Latin America) (not tested) """

    ET = "et"
    """ Estonian """

    FA = "fa"
    """ Persian """

    FA_PIN = "fa-pin"
    """ Persian (Pinglish) """

    FI = "fi"
    """ Finnish """

    FR = "fr"
    """ French """

    FR_BE = "fr-be"
    """ French (Belgium) (not tested) """

    FR_FR = "fr-fr"
    """ French (France) """

    GA = "ga"
    """ Irish """

    # NOTE already defined
    # COMMENTED GRC = "grc"
    # COMMENTED """ Greek (Ancient) """

    HI = "hi"
    """ Hindi (not tested) """

    HR = "hr"
    """ Croatian """

    HU = "hu"
    """ Hungarian """

    HY = "hy"
    """ Armenian (not tested) """

    HY_WEST = "hy-west"
    """ Armenian (West) (not tested) """

    ID = "id"
    """ Indonesian (not tested) """

    IS = "is"
    """ Icelandic """

    IT = "it"
    """ Italian """

    # NOTE already defined
    # COMMENTED JBO = "jbo"
    # COMMENTED """ Lojban (not tested) """

    KA = "ka"
    """ Georgian (not tested) """

    KN = "kn"
    """ Kannada (not tested) """

    KU = "ku"
    """ Kurdish (not tested) """

    LA = "la"
    """ Latin """

    # NOTE already defined
    # COMMENTED LFN = "lfn"
    # COMMENTED """ Lingua Franca Nova (not tested) """

    LT = "lt"
    """ Lithuanian """

    LV = "lv"
    """ Latvian """

    MK = "mk"
    """ Macedonian (not tested) """

    ML = "ml"
    """ Malayalam (not tested) """

    MS = "ms"
    """ Malay (not tested) """

    NE = "ne"
    """ Nepali (not tested) """

    NL = "nl"
    """ Dutch """

    NO = "no"
    """ Norwegian """

    PA = "pa"
    """ Panjabi (not tested) """

    PL = "pl"
    """ Polish """

    PT = "pt"
    """ Portuguese """

    PT_BR = "pt-br"
    """ Portuguese (Brazil) (not tested) """

    PT_PT = "pt-pt"
    """ Portuguese (Portugal) """

    RO = "ro"
    """ Romanian """

    RU = "ru"
    """ Russian """

    SQ = "sq"
    """ Albanian (not tested) """

    SK = "sk"
    """ Slovak """

    SR = "sr"
    """ Serbian """

    SV = "sv"
    """ Swedish """

    SW = "sw"
    """ Swahili """

    TA = "ta"
    """ Tamil (not tested) """

    TR = "tr"
    """ Turkish """

    UK = "uk"
    """ Ukrainian """

    VI = "vi"
    """ Vietnamese (not tested) """

    VI_HUE = "vi-hue"
    """ Vietnamese (hue) (not tested) """

    VI_SGN = "vi-sgn"
    """ Vietnamese (sgn) (not tested) """

    ZH = "zh"
    """ Mandarin Chinese (not tested) """

    ZH_YUE = "zh-yue"
    """ Yue Chinese (not tested) """

    CODE_TO_HUMAN = {
        AFR: "Afrikaans",
        ARG: "Aragonese (not tested)",
        BOS: "Bosnian (not tested)",
        BUL: "Bulgarian",
        CAT: "Catalan",
        CES: "Czech",
        CMN: "Mandarin Chinese (not tested)",
        CYM: "Welsh",
        DAN: "Danish",
        DEU: "German",
        ELL: "Greek (Modern)",
        ENG: "English",
        EPO: "Esperanto (not tested)",
        EST: "Estonian",
        FAS: "Persian",
        FIN: "Finnish",
        FRA: "French",
        GLE: "Irish",
        GRC: "Greek (Ancient)",
        HIN: "Hindi (not tested)",
        HRV: "Croatian",
        HUN: "Hungarian",
        HYE: "Armenian (not tested)",
        IND: "Indonesian (not tested)",
        ISL: "Icelandic",
        ITA: "Italian",
        JBO: "Lojban (not tested)",
        KAN: "Kannada (not tested)",
        KAT: "Georgian (not tested)",
        KUR: "Kurdish (not tested)",
        LAT: "Latin",
        LAV: "Latvian",
        LFN: "Lingua Franca Nova (not tested)",
        LIT: "Lithuanian",
        MAL: "Malayalam (not tested)",
        MKD: "Macedonian (not tested)",
        MSA: "Malay (not tested)",
        NEP: "Nepali (not tested)",
        NLD: "Dutch",
        NOR: "Norwegian",
        PAN: "Panjabi (not tested)",
        POL: "Polish",
        POR: "Portuguese",
        RON: "Romanian",
        RUS: "Russian",
        SLK: "Slovak",
        SPA: "Spanish",
        SQI: "Albanian (not tested)",
        SRP: "Serbian",
        SWA: "Swahili",
        SWE: "Swedish",
        TAM: "Tamil (not tested)",
        TUR: "Turkish",
        UKR: "Ukrainian",
        VIE: "Vietnamese (not tested)",
        YUE: "Yue Chinese (not tested)",
        ZHO: "Chinese (not tested)",
        ENG_GBR: "English (GB)",
        ENG_SCT: "English (Scotland) (not tested)",
        ENG_USA: "English (USA)",
        SPA_ESP: "Spanish (Castillan)",
        FRA_BEL: "French (Belgium) (not tested)",
        FRA_FRA: "French (France)",
        POR_BRA: "Portuguese (Brazil) (not tested)",
        POR_PRT: "Portuguese (Portugal)",
        AF: "Afrikaans",
        AN: "Aragonese (not tested)",
        BG: "Bulgarian",
        BS: "Bosnian (not tested)",
        CA: "Catalan",
        CS: "Czech",
        CY: "Welsh",
        DA: "Danish",
        DE: "German",
        EL: "Greek (Modern)",
        EN: "English",
        EN_GB: "English (GB)",
        EN_SC: "English (Scotland) (not tested)",
        EN_UK_NORTH: "English (Northern) (not tested)",
        EN_UK_RP: "English (Received Pronunciation) (not tested)",
        EN_UK_WMIDS: "English (Midlands) (not tested)",
        EN_US: "English (USA)",
        EN_WI: "English (West Indies) (not tested)",
        EO: "Esperanto (not tested)",
        ES: "Spanish (Castillan)",
        ES_LA: "Spanish (Latin America) (not tested)",
        ET: "Estonian",
        FA: "Persian",
        FA_PIN: "Persian (Pinglish)",
        FI: "Finnish",
        FR: "French",
        FR_BE: "French (Belgium) (not tested)",
        FR_FR: "French (France)",
        GA: "Irish",
        HI: "Hindi (not tested)",
        HR: "Croatian",
        HU: "Hungarian",
        HY: "Armenian (not tested)",
        HY_WEST: "Armenian (West) (not tested)",
        ID: "Indonesian (not tested)",
        IS: "Icelandic",
        IT: "Italian",
        KA: "Georgian (not tested)",
        KN: "Kannada (not tested)",
        KU: "Kurdish (not tested)",
        LA: "Latin",
        LT: "Lithuanian",
        LV: "Latvian",
        MK: "Macedonian (not tested)",
        ML: "Malayalam (not tested)",
        MS: "Malay (not tested)",
        NE: "Nepali (not tested)",
        NL: "Dutch",
        NO: "Norwegian",
        PA: "Panjabi (not tested)",
        PL: "Polish",
        PT: "Portuguese",
        PT_BR: "Portuguese (Brazil) (not tested)",
        PT_PT: "Portuguese (Portugal)",
        RO: "Romanian",
        RU: "Russian",
        SQ: "Albanian (not tested)",
        SK: "Slovak",
        SR: "Serbian",
        SV: "Swedish",
        SW: "Swahili",
        TA: "Tamil (not tested)",
        TR: "Turkish",
        UK: "Ukrainian",
        VI: "Vietnamese (not tested)",
        VI_HUE: "Vietnamese (hue) (not tested)",
        VI_SGN: "Vietnamese (sgn) (not tested)",
        ZH: "Mandarin Chinese (not tested)",
        ZH_YUE: "Yue Chinese (not tested)",
    }

    CODE_TO_HUMAN_LIST = sorted(f"{k}\t{v}" for k, v in CODE_TO_HUMAN.items())

    LANGUAGE_TO_VOICE_CODE = {
        AF: "af",
        AN: "an",
        BG: "bg",
        BS: "bs",
        CA: "ca",
        CS: "cs",
        CY: "cy",
        DA: "da",
        DE: "de",
        EL: "el",
        EN: "en",
        EN_GB: "en-gb",
        EN_SC: "en-sc",
        EN_UK_NORTH: "en-uk-north",
        EN_UK_RP: "en-uk-rp",
        EN_UK_WMIDS: "en-uk-wmids",
        EN_US: "en-us",
        EN_WI: "en-wi",
        EO: "eo",
        ES: "es",
        ES_LA: "es-la",
        ET: "et",
        FA: "fa",
        FA_PIN: "fa-pin",
        FI: "fi",
        FR: "fr",
        FR_BE: "fr-be",
        FR_FR: "fr-fr",
        GA: "ga",
        # COMMENTED GRC: "grc",
        HI: "hi",
        HR: "hr",
        HU: "hu",
        HY: "hy",
        HY_WEST: "hy-west",
        ID: "id",
        IS: "is",
        IT: "it",
        # COMMENTED JBO: "jbo",
        KA: "ka",
        KN: "kn",
        KU: "ku",
        LA: "la",
        # COMMENTED LFN: "lfn",
        LT: "lt",
        LV: "lv",
        MK: "mk",
        ML: "ml",
        MS: "ms",
        NE: "ne",
        NL: "nl",
        NO: "no",
        PA: "pa",
        PL: "pl",
        PT: "pt",
        PT_BR: "pt-br",
        PT_PT: "pt-pt",
        RO: "ro",
        RU: "ru",
        SQ: "sq",
        SK: "sk",
        SR: "sr",
        SV: "sv",
        SW: "sw",
        TA: "ta",
        TR: "tr",
        UK: "ru",  # NOTE mocking support for Ukrainian with Russian voice
        VI: "vi",
        VI_HUE: "vi-hue",
        VI_SGN: "vi-sgn",
        ZH: "zh",
        ZH_YUE: "zh-yue",
        AFR: "af",
        ARG: "an",
        BOS: "bs",
        BUL: "bg",
        CAT: "ca",
        CES: "cs",
        CMN: "zh",
        CYM: "cy",
        DAN: "da",
        DEU: "de",
        ELL: "el",
        ENG: "en",
        EPO: "eo",
        EST: "et",
        FAS: "fa",
        FIN: "fi",
        FRA: "fr",
        GLE: "ga",
        GRC: "grc",
        HIN: "hi",
        HRV: "hr",
        HUN: "hu",
        HYE: "hy",
        IND: "id",
        ISL: "is",
        ITA: "it",
        JBO: "jbo",
        KAN: "kn",
        KAT: "ka",
        KUR: "ku",
        LAT: "la",
        LAV: "lv",
        LFN: "lfn",
        LIT: "lt",
        MAL: "ml",
        MKD: "mk",
        MSA: "ms",
        NEP: "ne",
        NLD: "nl",
        NOR: "no",
        PAN: "pa",
        POL: "pl",
        POR: "pt",
        RON: "ro",
        RUS: "ru",
        SLK: "sk",
        SPA: "es",
        SQI: "sq",
        SRP: "sr",
        SWA: "sw",
        SWE: "sv",
        TAM: "ta",
        TUR: "tr",
        UKR: "ru",  # NOTE mocking support for Ukrainian with Russian voice
        VIE: "vi",
        YUE: "zh-yue",
        ZHO: "zh",
        ENG_GBR: "en-gb",
        ENG_SCT: "en-sc",
        ENG_USA: "en-us",
        SPA_ESP: "es-es",
        FRA_BEL: "fr-be",
        FRA_FRA: "fr-fr",
        POR_BRA: "pt-br",
        POR_PRT: "pt-pt",
    }
    DEFAULT_LANGUAGE = ENG

    DEFAULT_TTS_PATH = "espeak"

    OUTPUT_AUDIO_FORMAT = ("pcm_s16le", 1, 22050)

    HAS_SUBPROCESS_CALL = True

    HAS_C_EXTENSION_CALL = True

    C_EXTENSION_NAME = "cew"

    def __init__(self, rconf=None):
        super().__init__(rconf=rconf)
        self.set_subprocess_arguments(
            [
                self.tts_path,
                "-v",
                self.CLI_PARAMETER_VOICE_CODE_STRING,
                "-w",
                self.CLI_PARAMETER_WAVE_PATH,
                self.CLI_PARAMETER_TEXT_STDIN,
            ]
        )

    def _synthesize_multiple_c_extension(
        self, text_file, output_file_path, quit_after=None, backwards=False
    ):
        """
        Synthesize multiple text fragments, using the cew extension.

        Return a tuple (anchors, total_time, num_chars).

        :rtype: (bool, (list, :class:`~aeneas.exacttiming.TimeValue`, int))
        """
        logger.debug("Synthesizing using C extension...")

        # convert parameters from Python values to C values
        try:
            c_quit_after = float(quit_after)
        except TypeError:
            c_quit_after = 0.0
        c_backwards = 0
        if backwards:
            c_backwards = 1
        logger.debug("output_file_path: %s", output_file_path)
        logger.debug("c_quit_after:     %.3f", c_quit_after)
        logger.debug("c_backwards:      %d", c_backwards)
        logger.debug("Preparing u_text...")
        u_text = []
        fragments = text_file.fragments
        for fragment in fragments:
            f_lang = fragment.language
            f_text = fragment.filtered_text
            if f_lang is None:
                f_lang = self.DEFAULT_LANGUAGE
            f_voice_code = self._language_to_voice_code(f_lang)
            if f_text is None:
                f_text = ""
            u_text.append((f_voice_code, f_text))
        logger.debug("Preparing u_text... done")

        # call C extension
        sample_rate = None
        synthesized_fragments = None
        intervals = None
        if self.rconf[RuntimeConfiguration.CEW_SUBPROCESS_ENABLED]:
            logger.debug("Using cewsubprocess to call aeneas.cew")
            try:
                logger.debug("Importing aeneas.cewsubprocess...")
                from aeneas.cewsubprocess import CEWSubprocess

                logger.debug("Importing aeneas.cewsubprocess... done")
                logger.debug("Calling aeneas.cewsubprocess...")
                cewsub = CEWSubprocess(rconf=self.rconf)
                sample_rate, synthesized_fragments, intervals = (
                    cewsub.synthesize_multiple(
                        output_file_path, c_quit_after, c_backwards, u_text
                    )
                )
                logger.debug("Calling aeneas.cewsubprocess... done")
            except Exception:
                logger.exception(
                    "An unexpected error occurred while running cewsubprocess",
                )
                # NOTE not critical, try calling aeneas.cew directly
                # COMMENTED return (False, None)

        if sample_rate is None:
            logger.debug("Preparing c_text...")
            c_text = [(gf.safe_unicode(t[0]), gf.safe_unicode(t[1])) for t in u_text]
            logger.debug("Preparing c_text... done")

            logger.debug("Calling aeneas.cew directly")
            try:
                logger.debug("Importing aeneas.cew...")
                import aeneas.cew.cew as cew

                logger.debug("Importing aeneas.cew... done")
                logger.debug("Calling aeneas.cew...")
                sample_rate, synthesized_fragments, intervals = cew.synthesize_multiple(
                    output_file_path, c_quit_after, c_backwards, c_text
                )
                logger.debug("Calling aeneas.cew... done")
            except Exception:
                logger.exception("An unexpected error occurred while running cew")
                return (False, None)

        logger.debug("sr: %d, sf: %d", sample_rate, synthesized_fragments)

        # create output
        anchors = []
        current_time = TimeValue("0.000")
        num_chars = 0
        if backwards:
            fragments = fragments[::-1]
        for i in range(synthesized_fragments):
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
        logger.debug("Returning %d time anchors", len(anchors))
        logger.debug("Current time %.3f", current_time)
        logger.debug("Synthesized %d characters", num_chars)
        logger.debug("Synthesizing using C extension... done")
        return (True, (anchors, current_time, num_chars))
