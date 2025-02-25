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

* :class:`~aeneas.ttswrappers.nuancettswrapper.NuanceTTSWrapper`,
  a wrapper for the Nuance TTS API engine.

Please refer to
https://developer.nuance.com/
for further details.

.. note:: This module requires Python module ``requests`` (``pip install requests``).

.. warning:: You will be billed according to your Nuance Developers account plan.

.. warning:: This module is experimental, use at your own risk.

.. versionadded:: 1.5.0
"""

import logging
import time
import uuid

import numpy

from aeneas.exacttiming import TimeValue
from aeneas.language import Language
from aeneas.runtimeconfiguration import RuntimeConfiguration
from aeneas.ttswrappers.basettswrapper import BaseTTSWrapper

logger = logging.getLogger(__name__)


class NuanceTTSWrapper(BaseTTSWrapper):
    """
    A wrapper for the Nuance Developers TTS API.

    This wrapper supports calling the TTS engine
    only via Python.

    In abstract terms, it performs one or more calls to the
    Nuance TTS API service, and concatenate the resulting WAVE files,
    returning their anchor times.

    To use this TTS engine, specify ::

        "tts=nuance|nuance_tts_api_id=...|nuance_tts_api_key=..."

    in the ``RuntimeConfiguration`` object,
    substituting your Nuance Developer API ID and Key.

    You might also want to enable the TTS caching,
    to reduce the number of API calls ::

        "tts=nuance|tts_cache=True"

    See :class:`~aeneas.ttswrappers.basettswrapper.BaseTTSWrapper`
    for the available functions.
    Below are listed the languages supported by this wrapper.

    :param rconf: a runtime configuration
    :type  rconf: :class:`~aeneas.runtimeconfiguration.RuntimeConfiguration`
    """

    ARA = Language.ARA
    """ Arabic """

    CAT = Language.CAT
    """ Catalan """

    CES = Language.CES
    """ Czech """

    CMN = Language.CMN
    """ Mandarin Chinese """

    DAN = Language.DAN
    """ Danish """

    DEU = Language.DEU
    """ German """

    ELL = Language.ELL
    """ Greek (Modern) """

    ENG = Language.ENG
    """ English """

    EUS = Language.EUS
    """ Basque """

    FIN = Language.FIN
    """ Finnish """

    FRA = Language.FRA
    """ French """

    GLG = Language.GLG
    """ Galician """

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

    YUE = Language.YUE
    """ Yue Chinese """

    CMN_CHN = "cmn-CHN"
    """ Mandarin Chinese (China) """

    CMN_TWN = "cmn-TWN"
    """ Mandarin Chinese (Taiwan) """

    ENG_AUS = "eng-AUS"
    """ English (Australia) """

    ENG_GBR = "eng-GBR"
    """ English (GB) """

    ENG_IND = "eng-IND"
    """ English (India) """

    ENG_IRL = "eng-IRL"
    """ English (Ireland) """

    ENG_SCT = "eng-SCT"
    """ English (Scotland) """

    ENG_ZAF = "eng-ZAF"
    """ English (South Africa) """

    ENG_USA = "eng-USA"
    """ English (USA) """

    FRA_CAN = "fra-CAN"
    """ French (Canada) """

    NLD_BEL = "nld-BEL"
    """ Dutch (Belgium) """

    POR_BRA = "por-BRA"
    """ Portuguese (Brazil) """

    POR_PRT = "por-PRT"
    """ Portuguese (Portugal) """

    SPA_COL = "spa-COL"
    """ Spanish (Colombia) """

    SPA_ESP = "spa-ESP"
    """ Spanish (Spain) """

    SPA_MEX = "spa-MEX"
    """ Spanish (Mexico) """

    CODE_TO_HUMAN = {
        ARA: "Arabic",
        CAT: "Catalan",
        CES: "Czech",
        CMN: "Mandarin Chinese",
        DAN: "Danish",
        DEU: "German",
        ELL: "Greek (Modern)",
        ENG: "English",
        EUS: "Basque",
        FIN: "Finnish",
        FRA: "French",
        GLG: "Galician",
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
        YUE: "Yue Chinese",
        CMN_CHN: "Mandarin Chinese (China)",
        CMN_TWN: "Mandarin Chinese (Taiwan)",
        ENG_AUS: "English (Australia)",
        ENG_GBR: "English (GB)",
        ENG_IND: "English (India)",
        ENG_IRL: "English (Ireland)",
        ENG_SCT: "English (Scotland)",
        ENG_USA: "English (USA)",
        ENG_ZAF: "English (South Africa)",
        FRA_CAN: "French (Canada)",
        NLD_BEL: "Dutch (Belgium)",
        POR_BRA: "Portuguese (Brazil)",
        POR_PRT: "Portuguese (Portugal)",
        SPA_COL: "Spanish (Colombia)",
        SPA_ESP: "Spanish (Spain)",
        SPA_MEX: "Spanish (Mexico)",
    }

    CODE_TO_HUMAN_LIST = sorted(f"{k}\t{v}" for k, v in CODE_TO_HUMAN.items())

    LANGUAGE_TO_VOICE_CODE = {
        ARA: "Laila",  # F, M: Maged, Tarik
        CAT: "Montserrat",  # F, M: Jordi
        CES: "Iveta",  # F, F: Zuzana
        CMN: "Tian-Tian",  # F
        DAN: "Ida",  # F, M: Magnus
        DEU: "Anna-ML",  # F-ML, F-ML: Petra-ML, M: Markus, Yannick
        ELL: "Melina",  # F, M: Nikos
        ENG: "Kate",  # F
        EUS: "Miren",  # F
        FIN: "Satu",  # F
        FRA: "Audrey-ML",  # F-ML, F: Aurelie, M: Thomas
        GLG: "Carmela",  # F
        HEB: "Carmit",  # F
        HIN: "Lekha",  # F
        HUN: "Mariska",  # F
        IND: "Damayanti",  # F
        ITA: "Alice-ML",  # F-ML, F: Federica, Paola, M: Luca
        JPN: "Kyoko",  # F, M: Otoya
        KOR: "Sora",  # F
        NLD: "Claire",  # F, M: Xander
        NOR: "Nora",  # F, M: Henrik
        POL: "Ewa",  # F, F: Zosia
        POR: "Catarina",  # F
        RON: "Ioana",  # F
        RUS: "Katya",  # F, F: Milena, M: Yuri
        SLK: "Laura",  # F
        SPA: "Monica",  # F, M: Jorge
        SWE: "Alva",  # F, M: Oskar
        THA: "Kanya",  # F
        TUR: "Yelda",  # F, M: Cem
        YUE: "Sin-Ji",  # F
        CMN_CHN: "Tian-Tian",  # F
        CMN_TWN: "Mei-Jia",  # F
        FRA_CAN: "Amelie",  # F, F: Chantal, M: Nicolas
        ENG_AUS: "Karen",  # F, M: Lee
        ENG_GBR: "Kate",  # F, F: Serena, M: Daniel, Oliver
        ENG_IND: "Veena",  # F
        ENG_IRL: "Moira",  # F
        ENG_SCT: "Fiona",  # F
        ENG_USA: "Ava",  # F, F: Allison, Samantha, Susan, Zoe, M: Tom
        ENG_ZAF: "Tessa",  # F
        NLD_BEL: "Ellen",  # F
        POR_BRA: "Luciana",  # F, M: Felipe
        POR_PRT: "Catarina",  # F, F: Joana
        SPA_COL: "Soledad",  # F, M: Carlos
        SPA_ESP: "Monica",  # F, F (Valencian): Empar
        SPA_MEX: "Angelica",  # F, F: Paulina, M: Juan
    }
    DEFAULT_LANGUAGE = ENG_GBR

    OUTPUT_AUDIO_FORMAT = ("pcm_s16le", 1, 16000)

    HAS_PYTHON_CALL = True

    # Nuance TTS API specific
    END_POINT = "NMDPTTSCmdServlet/tts"
    """ Nuance TTS API end point """

    SAMPLE_RATE = 16000
    """ Synthesize 16kHz PCM16 mono """

    URL = "https://tts.nuancemobility.net"
    """ Nuance TTS API URL """

    def __init__(self, rconf=None):
        super().__init__(rconf=rconf)

    def _synthesize_single_python_helper(
        self, text, voice_code, output_file_path=None, return_audio_data=True
    ):
        logger.debug("Importing requests...")
        import requests

        logger.debug("Importing requests... done")

        # prepare request header and contents
        request_id = str(uuid.uuid4()).replace("-", "")[0:16]
        headers = {
            "Content-Type": "text/plain; charset=utf-8",
            "Accept": "audio/x-wav;codec=pcm;bit=16;rate=%d" % self.SAMPLE_RATE,
        }
        text_to_synth = text.encode("utf-8")
        url = "{}/{}?appId={}&appKey={}&id={}&voice={}".format(
            self.URL,
            self.END_POINT,
            self.rconf[RuntimeConfiguration.NUANCE_TTS_API_ID],
            self.rconf[RuntimeConfiguration.NUANCE_TTS_API_KEY],
            request_id,
            voice_code,
        )

        # post request
        sleep_delay = self.rconf[RuntimeConfiguration.TTS_API_SLEEP]
        attempts = self.rconf[RuntimeConfiguration.TTS_API_RETRY_ATTEMPTS]
        logger.debug("Sleep delay:    %.3f", sleep_delay)
        logger.debug("Retry attempts: %d", attempts)
        while attempts > 0:
            logger.debug("Sleeping to throttle API usage...")
            time.sleep(sleep_delay)
            logger.debug("Sleeping to throttle API usage... done")
            logger.debug("Posting...")
            try:
                response = requests.post(url, data=text_to_synth, headers=headers)
            except Exception as exc:
                raise ValueError(
                    "Unexpected exception on HTTP POST. Are you offline?"
                ) from exc
            logger.debug("Posting... done")
            status_code = response.status_code
            logger.debug("Status code: %d", status_code)
            if status_code == 200:
                logger.debug("Got status code 200, break")
                break
            else:
                logger.warning("Got status code other than 200, retry")
                attempts -= 1

        if attempts <= 0:
            raise ValueError("All API requests returned status code != 200")

        # save to file if requested
        if output_file_path is None:
            logger.debug("output_file_path is None => not saving to file")
        else:
            logger.debug("output_file_path is not None => saving to file...")
            import wave

            output_file = wave.open(output_file_path, "wb")
            output_file.setframerate(self.SAMPLE_RATE)  # sample rate
            output_file.setnchannels(1)  # 1 channel, i.e. mono
            output_file.setsampwidth(2)  # 16 bit/sample, i.e. 2 bytes/sample
            output_file.writeframes(response.content)
            output_file.close()
            logger.debug("output_file_path is not None => saving to file... done")

        # get length and data
        audio_sample_rate = self.SAMPLE_RATE
        number_of_frames = len(response.content) / 2
        audio_length = TimeValue(number_of_frames / audio_sample_rate)
        logger.debug("Response (bytes): %d", len(response.content))
        logger.debug("Number of frames: %d", number_of_frames)
        logger.debug("Audio length (s): %.3f", audio_length)
        audio_format = "pcm16"
        audio_samples = (
            numpy.fromstring(response.content, dtype=numpy.int16).astype("float64")
            / 32768
        )

        # return data
        return (True, (audio_length, audio_sample_rate, audio_format, audio_samples))
