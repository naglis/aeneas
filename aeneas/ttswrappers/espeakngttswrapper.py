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

* :class:`~aeneas.ttswrappers.espeakngttswrapper.ESPEAKNGTTSWrapper`,
  a wrapper for the ``eSpeak-ng`` TTS engine.

Please refer to
https://github.com/espeak-ng/espeak-ng/
for further details.
"""

import logging

from aeneas.exacttiming import TimeValue
from aeneas.language import Language
from aeneas.ttswrappers.basettswrapper import BaseTTSWrapper
import aeneas.globalfunctions as gf

logger = logging.getLogger(__name__)


class ESPEAKNGTTSWrapper(BaseTTSWrapper):
    """
    A wrapper for the ``eSpeak-ng`` TTS engine.

    This wrapper supports calling the TTS engine
    via ``subprocess``.

    Future support for calling via Python C extension
    is planned.

    In abstract terms, it performs one or more calls like ::

        $ espeak-ng -v voice_code -w /tmp/output_file.wav < text

    To use this TTS engine, specify ::

        "tts=espeak-ng"

    in the ``RuntimeConfiguration`` object.
    To execute from a non-default location: ::

        "tts=espeak-ng|tts_path=/path/to/espeak-ng"

    See :class:`~aeneas.ttswrappers.basettswrapper.BaseTTSWrapper`
    for the available functions.
    Below are listed the languages supported by this wrapper.

    :param rconf: a runtime configuration
    :type  rconf: :class:`~aeneas.runtimeconfiguration.RuntimeConfiguration`
    """

    AFR = Language.AFR
    """ Afrikaans """

    AMH = Language.AMH
    """ Amharic (not tested) """

    ARG = Language.ARG
    """ Aragonese (not tested) """

    ASM = Language.ASM
    """ Assamese (not tested) """

    AZE = Language.AZE
    """ Azerbaijani (not tested) """

    BEN = Language.BEN
    """ Bengali (not tested) """

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

    EUS = "eus"
    """ Basque (not tested) """

    FAS = Language.FAS
    """ Persian """

    FIN = Language.FIN
    """ Finnish """

    FRA = Language.FRA
    """ French """

    GLA = Language.GLA
    """ Scottish Gaelic (not tested) """

    GLE = Language.GLE
    """ Irish """

    GRC = Language.GRC
    """ Greek (Ancient) """

    GRN = Language.GRN
    """ Guarani (not tested) """

    GUJ = Language.GUJ
    """ Gujarati (not tested) """

    HIN = Language.HIN
    """ Hindi (not tested) """

    HRV = Language.HRV
    """ Croatian """

    HUN = Language.HUN
    """ Hungarian """

    HYE = Language.HYE
    """ Armenian (not tested) """

    INA = Language.INA
    """ Interlingua (not tested) """

    IND = Language.IND
    """ Indonesian (not tested) """

    ISL = Language.ISL
    """ Icelandic """

    ITA = Language.ITA
    """ Italian """

    JBO = Language.JBO
    """ Lojban (not tested) """

    KAL = Language.KAL
    """ Greenlandic (not tested) """

    KAN = Language.KAN
    """ Kannada (not tested) """

    KAT = Language.KAT
    """ Georgian (not tested) """

    KIR = Language.KIR
    """ Kirghiz (not tested) """

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

    MAR = Language.MAR
    """ Marathi (not tested) """

    MKD = Language.MKD
    """ Macedonian (not tested) """

    MLT = Language.MLT
    """ Maltese (not tested) """

    MSA = Language.MSA
    """ Malay (not tested) """

    MYA = Language.MYA
    """ Burmese (not tested) """

    NAH = Language.NAH
    """ Nahuatl (not tested) """

    NEP = Language.NEP
    """ Nepali (not tested) """

    NLD = Language.NLD
    """ Dutch """

    NOR = Language.NOR
    """ Norwegian """

    ORI = Language.ORI
    """ Oriya (not tested) """

    ORM = Language.ORM
    """ Oromo (not tested) """

    PAN = Language.PAN
    """ Panjabi (not tested) """

    PAP = Language.PAP
    """ Papiamento (not tested) """

    POL = Language.POL
    """ Polish """

    POR = Language.POR
    """ Portuguese """

    RON = Language.RON
    """ Romanian """

    RUS = Language.RUS
    """ Russian """

    SIN = Language.SIN
    """ Sinhala (not tested) """

    SLK = Language.SLK
    """ Slovak """

    SLV = Language.SLV
    """ Slovenian (not tested) """

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

    TAT = Language.TAT
    """ Tatar (not tested) """

    TEL = Language.TEL
    """ Telugu (not tested) """

    TSN = Language.TSN
    """ Tswana (not tested) """

    TUR = Language.TUR
    """ Turkish """

    UKR = Language.UKR
    """ Ukrainian """

    URD = Language.URD
    """ Urdu (not tested) """

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

    AM = "am"
    """ Amharic (not tested) """

    AS = "as"
    """ Assamese (not tested) """

    AZ = "az"
    """ Azerbaijani (not tested) """

    BG = "bg"
    """ Bulgarian """

    BN = "bn"
    """ Bengali (not tested) """

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

    EN_GB_SCOTLAND = "en-gb-scotland"
    """ English (Scotland) (not tested) """

    EN_GB_X_GBCLAN = "en-gb-x-gbclan"
    """ English (Northern) (not tested) """

    EN_GB_X_GBCWMD = "en-gb-x-gbcwmd"
    """ English (Midlands) (not tested) """

    EN_GB_X_RP = "en-gb-x-rp"
    """ English (Received Pronunciation) (not tested) """

    EN_US = "en-us"
    """ English (USA) """

    EN_029 = "en-029"
    """ English (West Indies) (not tested) """

    EO = "eo"
    """ Esperanto (not tested) """

    ES = "es"
    """ Spanish (Castillan) """

    ES_419 = "es-419"
    """ Spanish (Latin America) (not tested) """

    ET = "et"
    """ Estonian """

    EU = "eu"
    """ Basque (not tested) """

    FA = "fa"
    """ Persian """

    FA_LATN = "fa-Latn"
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

    GD = "gd"
    """ Scottish Gaelic (not tested) """

    GN = "gn"
    """ Guarani (not tested) """

    # NOTE already defined
    # COMMENTED GRC = "grc"
    # COMMENTED """ Greek (Ancient) """

    GU = "gu"
    """ Gujarati (not tested) """

    HI = "hi"
    """ Hindi (not tested) """

    HR = "hr"
    """ Croatian """

    HU = "hu"
    """ Hungarian """

    HY = "hy"
    """ Armenian (not tested) """

    HY_AREVMDA = "hy-arevmda"
    """ Armenian (West) (not tested) """

    IA = "ia"
    """ Interlingua (not tested) """

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

    KL = "kl"
    """ Greenlandic (not tested) """

    KN = "kn"
    """ Kannada (not tested) """

    KU = "ku"
    """ Kurdish (not tested) """

    KY = "ky"
    """ Kirghiz (not tested) """

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

    MR = "mr"
    """ Marathi (not tested) """

    MS = "ms"
    """ Malay (not tested) """

    MT = "mt"
    """ Maltese (not tested) """

    MY = "my"
    """ Burmese (not tested) """

    NCI = "nci"
    """ Nahuatl (not tested) """

    NE = "ne"
    """ Nepali (not tested) """

    NL = "nl"
    """ Dutch """

    NO = "no"
    """ Norwegian """

    OM = "om"
    """ Oromo (not tested) """

    OR = "or"
    """ Oriya (not tested) """

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

    SI = "si"
    """ Sinhala (not tested) """

    SK = "sk"
    """ Slovak """

    SL = "sl"
    """ Slovenian (not tested) """

    SQ = "sq"
    """ Albanian (not tested) """

    SR = "sr"
    """ Serbian """

    SV = "sv"
    """ Swedish """

    SW = "sw"
    """ Swahili """

    TA = "ta"
    """ Tamil (not tested) """

    TE = "te"
    """ Telugu (not tested) """

    TN = "tn"
    """ Tswana (not tested) """

    TR = "tr"
    """ Turkish """

    TT = "tt"
    """ Tatar (not tested) """

    UK = "uk"
    """ Ukrainian """

    UR = "ur"
    """ Urdu (not tested) """

    VI = "vi"
    """ Vietnamese (not tested) """

    VI_VN_X_CENTRAL = "vi-vn-x-central"
    """ Vietnamese (hue) (not tested) """

    VI_VN_X_SOUTH = "vi-vn-x-south"
    """ Vietnamese (sgn) (not tested) """

    ZH = "zh"
    """ Mandarin Chinese (not tested) """

    ZH_YUE = "zh-yue"
    """ Yue Chinese (not tested) """

    CODE_TO_HUMAN = {
        AFR: "Afrikaans",
        AMH: "Amharic (not tested)",
        ARG: "Aragonese (not tested)",
        ASM: "Assamese (not tested)",
        AZE: "Azerbaijani (not tested)",
        BEN: "Bengali (not tested)",
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
        EUS: "Basque (not tested)",
        FAS: "Persian",
        FIN: "Finnish",
        FRA: "French",
        GLA: "Scottish Gaelic (not tested)",
        GLE: "Irish",
        GRC: "Greek (Ancient)",
        GRN: "Guarani (not tested)",
        GUJ: "Gujarati (not tested)",
        HIN: "Hindi (not tested)",
        HRV: "Croatian",
        HUN: "Hungarian",
        HYE: "Armenian (not tested)",
        INA: "Interlingua (not tested)",
        IND: "Indonesian (not tested)",
        ISL: "Icelandic",
        ITA: "Italian",
        JBO: "Lojban (not tested)",
        KAL: "Greenlandic (not tested)",
        KAN: "Kannada (not tested)",
        KAT: "Georgian (not tested)",
        KIR: "Kirghiz (not tested)",
        KUR: "Kurdish (not tested)",
        LAT: "Latin",
        LAV: "Latvian",
        LFN: "Lingua Franca Nova (not tested)",
        LIT: "Lithuanian",
        MAL: "Malayalam (not tested)",
        MAR: "Marathi (not tested)",
        MKD: "Macedonian (not tested)",
        MLT: "Maltese (not tested)",
        MSA: "Malay (not tested)",
        MYA: "Burmese (not tested)",
        NAH: "Nahuatl (not tested)",
        NEP: "Nepali (not tested)",
        NLD: "Dutch",
        NOR: "Norwegian",
        ORI: "Oriya (not tested)",
        ORM: "Oromo (not tested)",
        PAN: "Panjabi (not tested)",
        PAP: "Papiamento (not tested)",
        POL: "Polish",
        POR: "Portuguese",
        RON: "Romanian",
        RUS: "Russian",
        SIN: "Sinhala (not tested)",
        SLK: "Slovak",
        SLV: "Slovenian (not tested)",
        SPA: "Spanish",
        SQI: "Albanian (not tested)",
        SRP: "Serbian",
        SWA: "Swahili",
        SWE: "Swedish",
        TAM: "Tamil (not tested)",
        TAT: "Tatar (not tested)",
        TEL: "Telugu (not tested)",
        TSN: "Tswana (not tested)",
        TUR: "Turkish",
        UKR: "Ukrainian",
        URD: "Urdu (not tested)",
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
        AM: "Amharic (not tested)",
        AS: "Assamese (not tested)",
        AZ: "Azerbaijani (not tested)",
        BG: "Bulgarian",
        BN: "Bengali (not tested)",
        BS: "Bosnian (not tested)",
        CA: "Catalan",
        CS: "Czech",
        CY: "Welsh",
        DA: "Danish",
        DE: "German",
        EL: "Greek (Modern)",
        EN: "English",
        EN_GB: "English (GB)",
        EN_GB_SCOTLAND: "English (Scotland) (not tested)",
        EN_GB_X_GBCLAN: "English (Northern) (not tested)",
        EN_GB_X_GBCWMD: "English (Midlands) (not tested)",
        EN_GB_X_RP: "English (Received Pronunciation) (not tested)",
        EN_US: "English (USA)",
        EN_029: "English (West Indies) (not tested)",
        EO: "Esperanto (not tested)",
        ES: "Spanish (Castillan)",
        ES_419: "Spanish (Latin America) (not tested)",
        ET: "Estonian",
        EU: "Basque (not tested)",
        FA: "Persian",
        FA_LATN: "Persian (Pinglish)",
        FI: "Finnish",
        FR: "French",
        FR_BE: "French (Belgium) (not tested)",
        FR_FR: "French (France)",
        GA: "Irish",
        GD: "Scottish Gaelic (not tested)",
        GN: "Guarani (not tested)",
        GU: "Gujarati (not tested)",
        HI: "Hindi (not tested)",
        HR: "Croatian",
        HU: "Hungarian",
        HY: "Armenian (not tested)",
        HY_AREVMDA: "Armenian (West) (not tested)",
        IA: "Interlingua (not tested)",
        ID: "Indonesian (not tested)",
        IS: "Icelandic",
        IT: "Italian",
        KA: "Georgian (not tested)",
        KL: "Greenlandic (not tested)",
        KN: "Kannada (not tested)",
        KU: "Kurdish (not tested)",
        KY: "Kirghiz (not tested)",
        LA: "Latin",
        LT: "Lithuanian",
        LV: "Latvian",
        MK: "Macedonian (not tested)",
        ML: "Malayalam (not tested)",
        MR: "Marathi (not tested)",
        MS: "Malay (not tested)",
        MT: "Maltese (not tested)",
        MY: "Burmese (not tested)",
        NCI: "Nahuatl (not tested)",
        NE: "Nepali (not tested)",
        NL: "Dutch",
        NO: "Norwegian",
        OM: "Oromo (not tested)",
        OR: "Oriya (not tested)",
        PA: "Panjabi (not tested)",
        PL: "Polish",
        PT: "Portuguese",
        PT_BR: "Portuguese (Brazil) (not tested)",
        PT_PT: "Portuguese (Portugal)",
        RO: "Romanian",
        RU: "Russian",
        SI: "Sinhala (not tested)",
        SK: "Slovak",
        SL: "Slovenian (not tested)",
        SQ: "Albanian (not tested)",
        SR: "Serbian",
        SV: "Swedish",
        SW: "Swahili",
        TA: "Tamil (not tested)",
        TE: "Telugu (not tested)",
        TN: "Tswana (not tested)",
        TR: "Turkish",
        TT: "Tatar (not tested)",
        UK: "Ukrainian",
        UR: "Urdu (not tested)",
        VI: "Vietnamese (not tested)",
        VI_VN_X_CENTRAL: "Vietnamese (hue) (not tested)",
        VI_VN_X_SOUTH: "Vietnamese (sgn) (not tested)",
        ZH: "Mandarin Chinese (not tested)",
        ZH_YUE: "Yue Chinese (not tested)",
    }

    CODE_TO_HUMAN_LIST = sorted(f"{k}\t{v}" for k, v in CODE_TO_HUMAN.items())

    LANGUAGE_TO_VOICE_CODE = {
        AF: "af",
        AM: "am",
        AN: "an",
        AS: "as",
        AZ: "az",
        BG: "bg",
        BN: "bn",
        BS: "bs",
        CA: "ca",
        CS: "cs",
        CY: "cy",
        DA: "da",
        DE: "de",
        EL: "el",
        EN: "en",
        EN_029: "en-029",
        EN_GB: "en-gb",
        EN_GB_SCOTLAND: "en-gb-scotland",
        EN_GB_X_GBCLAN: "en-gb-x-gbclan",
        EN_GB_X_GBCWMD: "en-gb-x-gbcwmd",
        EN_GB_X_RP: "en-gb-x-rp",
        EN_US: "en-us",
        EO: "eo",
        ES: "es",
        ES_419: "es-419",
        ET: "et",
        EU: "eu",
        FA: "fa",
        FA_LATN: "fa-Latn",
        FI: "fi",
        FR: "fr",
        FR_BE: "fr-be",
        FR_FR: "fr-fr",
        GA: "ga",
        GD: "gd",
        # COMMENTED GRC: "grc",
        GN: "gn",
        GU: "gu",
        HI: "hi",
        HR: "hr",
        HU: "hu",
        HY: "hy",
        HY_AREVMDA: "hy-arevmda",
        IA: "ia",
        ID: "id",
        IS: "is",
        IT: "it",
        # COMMENTED JBO: "jbo",
        KA: "ka",
        KL: "kl",
        KN: "kn",
        KU: "ku",
        KY: "ky",
        LA: "la",
        # COMMENTED LFN: "lfn",
        LT: "lt",
        LV: "lv",
        MK: "mk",
        ML: "ml",
        MR: "mr",
        MS: "ms",
        MT: "mt",
        MY: "my",
        NCI: "nci",
        NE: "ne",
        NL: "nl",
        NO: "no",
        OM: "om",
        OR: "or",
        PA: "pa",
        # COMMENTED PAP: "pap",
        PL: "pl",
        PT: "pt",
        PT_BR: "pt-br",
        PT_PT: "pt-pt",
        RO: "ro",
        RU: "ru",
        SI: "si",
        SK: "sk",
        SL: "sl",
        SQ: "sq",
        SR: "sr",
        SV: "sv",
        SW: "sw",
        TA: "ta",
        TE: "te",
        TN: "tn",
        TR: "tr",
        TT: "tt",
        UK: "ru",  # NOTE mocking support for Ukrainian with Russian voice
        UR: "ur",
        VI: "vi",
        VI_VN_X_CENTRAL: "vi-vn-x-central",
        VI_VN_X_SOUTH: "vi-vn-x-south",
        ZH: "zh",
        ZH_YUE: "zh-yue",
        AFR: "af",
        AMH: "am",
        ARG: "an",
        ASM: "as",
        AZE: "az",
        BEN: "bn",
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
        GLA: "gd",
        GLE: "ga",
        GRC: "grc",
        GRN: "gn",
        GUJ: "gu",
        HIN: "hi",
        HRV: "hr",
        HUN: "hu",
        HYE: "hy",
        INA: "ia",
        IND: "id",
        ISL: "is",
        ITA: "it",
        JBO: "jbo",
        KAL: "kl",
        KAN: "kn",
        KAT: "ka",
        KIR: "ky",
        KUR: "ku",
        LAT: "la",
        LAV: "lv",
        LFN: "lfn",
        LIT: "lt",
        MAL: "ml",
        MAR: "mr",
        MKD: "mk",
        MLT: "mt",
        MSA: "ms",
        MYA: "my",
        NAH: "nci",
        NEP: "ne",
        NLD: "nl",
        NOR: "no",
        ORI: "or",
        ORM: "om",
        PAN: "pa",
        PAP: "pap",
        POL: "pl",
        POR: "pt",
        RON: "ro",
        RUS: "ru",
        SIN: "si",
        SLK: "sk",
        SLV: "sl",
        SPA: "es",
        SQI: "sq",
        SRP: "sr",
        SWA: "sw",
        SWE: "sv",
        TAM: "ta",
        TAT: "tt",
        TEL: "te",
        TSN: "tn",
        TUR: "tr",
        UKR: "ru",  # NOTE mocking support for Ukrainian with Russian voice
        URD: "ur",
        VIE: "vi",
        YUE: "zh-yue",
        ZHO: "zh",
        ENG_GBR: "en-gb",
        ENG_SCT: "en-gb-scotland",
        ENG_USA: "en-us",
        SPA_ESP: "es-es",
        FRA_BEL: "fr-be",
        FRA_FRA: "fr-fr",
        POR_BRA: "pt-br",
        POR_PRT: "pt-pt",
    }
    DEFAULT_LANGUAGE = ENG

    DEFAULT_TTS_PATH = "espeak-ng"

    OUTPUT_AUDIO_FORMAT = ("pcm_s16le", 1, 22050)

    HAS_SUBPROCESS_CALL = True

    HAS_C_EXTENSION_CALL = True

    C_EXTENSION_NAME = "cengw"

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
        Synthesize multiple text fragments, using the cengw extension.

        Return a tuple (anchors, total_time, num_chars).

        :rtype: (bool, (list, :class:`~aeneas.exacttiming.TimeValue`, int))
        """
        logger.debug("Synthesizing using C extension...")

        # convert parameters from Python values to C values
        try:
            c_quit_after = float(quit_after)
        except TypeError:
            c_quit_after = 0.0
        c_backwards = int(backwards)
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

        if sample_rate is None:
            logger.debug("Preparing c_text...")
            c_text = [(gf.safe_unicode(t[0]), gf.safe_unicode(t[1])) for t in u_text]
            logger.debug("Preparing c_text... done")

            logger.debug("Calling aeneas.cengw directly")
            try:
                logger.debug("Importing aeneas.cengw...")
                import aeneas.cengw.cengw as cengw

                logger.debug("Importing aeneas.cengw... done")
                logger.debug("Calling aeneas.cengw...")
                sample_rate, synthesized_fragments, intervals = (
                    cengw.synthesize_multiple(
                        output_file_path, c_quit_after, c_backwards, c_text
                    )
                )
                logger.debug("Calling aeneas.cengw... done")
            except Exception:
                logger.exception("An unexpected error occurred while running cengw")
                return (False, None)

        logger.debug(
            "Sample rate: %s, synthesized fragments: %s",
            sample_rate,
            synthesized_fragments,
        )

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
