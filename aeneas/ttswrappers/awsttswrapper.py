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

* :class:`~aeneas.ttswrappers.awsttswrapper.AWSTTSWrapper`,
  a wrapper for the AWS Polly TTS API engine.

Please refer to
https://aws.amazon.com/polly/
for further details.

.. note:: This module requires Python module ``boto3`` (``pip install boto3``).

.. warning:: You will be billed according to your AWS account plan.
             Your AWS credentials and configuration settings
             to access the AWS Polly service must be
             either stored on disk
             (e.g., in ``~/.aws/credentials`` and ``~/.aws/config``)
             or set in environment variables.
             Please refer to
             http://boto3.readthedocs.io/en/latest/guide/configuration.html
             for further details.

.. warning:: This module is experimental, use at your own risk.

.. versionadded:: 1.7.0
"""

import logging
import time

import numpy

from aeneas.exacttiming import TimeValue
from aeneas.language import Language
from aeneas.runtimeconfiguration import RuntimeConfiguration
from aeneas.ttswrappers.basettswrapper import BaseTTSWrapper

logger = logging.getLogger(__name__)


class AWSTTSWrapper(BaseTTSWrapper):
    """
    A wrapper for the AWS Polly TTS API.

    This wrapper supports calling the TTS engine
    only via Python.

    In abstract terms, it performs one or more calls to the
    AWS Polly TTS API service, and concatenate the resulting WAVE files,
    returning their anchor times.

    To use this TTS engine, specify ::

        "tts=aws"

    in the ``RuntimeConfiguration`` object.

    Your AWS credentials and configuration settings
    to access the AWS Polly service must be
    either stored on disk
    (e.g., in ``~/.aws/credentials`` and ``~/.aws/config``)
    or set in environment variables.
    Please refer to
    http://boto3.readthedocs.io/en/latest/guide/configuration.html
    for further details.

    You might also want to enable the TTS caching,
    to reduce the number of API calls ::

        "tts=aws|tts_cache=True"

    See :class:`~aeneas.ttswrappers.basettswrapper.BaseTTSWrapper`
    for the available functions.
    Below are listed the languages supported by this wrapper.

    :param rconf: a runtime configuration
    :type  rconf: :class:`~aeneas.runtimeconfiguration.RuntimeConfiguration`
    """

    CYM = Language.CYM
    """ Welsh """

    DAN = Language.DAN
    """ Danish """

    DEU = Language.DEU
    """ German """

    ENG = Language.ENG
    """ English """

    FRA = Language.FRA
    """ French """

    ISL = Language.ISL
    """ Icelandic """

    ITA = Language.ITA
    """ Italian """

    JPN = Language.JPN
    """ Japanese """

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

    SPA = Language.SPA
    """ Spanish """

    SWE = Language.SWE
    """ Swedish """

    TUR = Language.TUR
    """ Turkish """

    ENG_AUS = "eng-AUS"
    """ English (Australia) """

    ENG_GBR = "eng-GBR"
    """ English (GB) """

    ENG_IND = "eng-IND"
    """ English (India) """

    ENG_USA = "eng-USA"
    """ English (USA) """

    ENG_WLS = "eng-WLS"
    """ English (Wales) """

    FRA_CAN = "fra-CAN"
    """ French (Canada) """

    FRA_FRA = "fra-FRA"
    """ French (France) """

    POR_BRA = "por-BRA"
    """ Portuguese (Brazil) """

    POR_PRT = "por-PRT"
    """ Portuguese (Portugal) """

    SPA_ESP = "spa-ESP"
    """ Spanish (Spain) """

    SPA_USA = "spa-USA"
    """ Spanish (USA) """

    CODE_TO_HUMAN = {
        CYM: "Welsh",
        DAN: "Danish",
        DEU: "German",
        ENG: "English",
        FRA: "French",
        ISL: "Icelandic",
        ITA: "Italian",
        JPN: "Japanese",
        NLD: "Dutch",
        NOR: "Norwegian",
        POL: "Polish",
        POR: "Portuguese",
        RON: "Romanian",
        RUS: "Russian",
        SPA: "Spanish",
        SWE: "Swedish",
        TUR: "Turkish",
        ENG_AUS: "English (Australia)",
        ENG_GBR: "English (GB)",
        ENG_IND: "English (India)",
        ENG_USA: "English (USA)",
        ENG_WLS: "English (Wales)",
        FRA_CAN: "French (Canada)",
        FRA_FRA: "French (France)",
        POR_BRA: "Portuguese (Brazil)",
        POR_PRT: "Portuguese (Portugal)",
        SPA_ESP: "Spanish (Spain)",
        SPA_USA: "Spanish (USA)",
    }

    CODE_TO_HUMAN_LIST = sorted(f"{k}\t{v}" for k, v in CODE_TO_HUMAN.items())

    LANGUAGE_TO_VOICE_CODE = {
        CYM: "Gwyneth",  # F
        DAN: "Naja",  # F, M: Mads
        DEU: "Marlene",  # F, M: Hans
        ENG: "Joanna",  # F
        FRA: "Celine",  # F, M: Mathieu
        ISL: "Dora",  # F, M: Karl
        ITA: "Carla",  # F, M: Giorgio
        JPN: "Mizuki",  # F
        NLD: "Lotte",  # F, M: Ruben
        NOR: "Liv",  # F
        POL: "Maja",  # F, F: Ewa, M: Jan, Jacek
        POR: "Ines",  # F
        RON: "Carmen",  # F
        RUS: "Tatyana",  # F, M: Maxim
        SPA: "Conchita",  # F, M: Enrique
        SWE: "Astrid",  # F
        TUR: "Filiz",  # F
        ENG_AUS: "Nicole",  # F, M: Russell
        ENG_GBR: "Emma",  # F, F: Amy, M: Brian
        ENG_IND: "Raveena",  # F
        ENG_USA: "Joanna",  # F, F: Salli, Kimberly, Kendra, Ivy, M: Justin, Joey
        ENG_WLS: "Geraint",  # M
        FRA_FRA: "Celine",  # F, M: Mathieu
        FRA_CAN: "Chantal",  # F
        POR_BRA: "Vitoria",  # F, M: Ricardo
        POR_PRT: "Ines",  # F, M: Cristiano
        SPA_ESP: "Conchita",  # F, M: Enrique
        SPA_USA: "Penelope",  # F, M: Miguel
    }
    DEFAULT_LANGUAGE = ENG_USA

    OUTPUT_AUDIO_FORMAT = ("pcm_s16le", 1, 16000)

    HAS_PYTHON_CALL = True

    SAMPLE_FORMAT = "pcm"
    """ Synthesize 16kHz PCM16 mono """

    SAMPLE_RATE = 16000
    """ Synthesize 16kHz PCM16 mono """

    def __init__(self, rconf=None):
        super().__init__(rconf=rconf)

    def _synthesize_single_python_helper(
        self, text, voice_code, output_file_path=None, return_audio_data=True
    ):
        logger.debug("Importing boto3...")
        import boto3

        logger.debug("Importing boto3... done")

        # prepare client
        polly_client = boto3.client("polly")

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
                response = polly_client.synthesize_speech(
                    Text=text,
                    OutputFormat=self.SAMPLE_FORMAT,
                    SampleRate="%d" % self.SAMPLE_RATE,
                    VoiceId=voice_code,
                )
            except Exception as exc:
                raise ValueError(
                    "Unexpected exception on HTTP POST. Are you offline?"
                ) from exc
            logger.debug("Posting... done")
            logger.debug("Reading response...")
            try:
                status_code = response["ResponseMetadata"]["HTTPStatusCode"]
                response_content = response["AudioStream"].read()
            except Exception:
                logger.warning(
                    "Error while reading the response status code or the response content",
                    exc_info=True,
                )
                status_code = 999
            logger.debug("Reading response... done")
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
            output_file.writeframes(response_content)
            output_file.close()
            logger.debug("output_file_path is not None => saving to file... done")

        # get length and data
        audio_sample_rate = self.SAMPLE_RATE
        number_of_frames = len(response_content) / 2
        audio_length = TimeValue(number_of_frames / audio_sample_rate)
        logger.debug("Response (bytes): %d", len(response_content))
        logger.debug("Number of frames: %d", number_of_frames)
        logger.debug("Audio length (s): %.3f", audio_length)
        audio_format = "pcm16"
        audio_samples = (
            numpy.fromstring(response_content, dtype=numpy.int16).astype("float64")
            / 32768
        )

        # return data
        return (True, (audio_length, audio_sample_rate, audio_format, audio_samples))
