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

* :class:`~aeneas.synthesizer.Synthesizer`,
  for synthesizing text fragments into an audio file,
  along with the corresponding time anchors.

.. warning:: This module might be refactored in a future version
"""

import importlib.util
import os.path

from aeneas.logger import Loggable
from aeneas.runtimeconfiguration import RuntimeConfiguration
from aeneas.textfile import TextFile
from aeneas.ttswrappers.awsttswrapper import AWSTTSWrapper
from aeneas.ttswrappers.espeakngttswrapper import ESPEAKNGTTSWrapper
from aeneas.ttswrappers.espeakttswrapper import ESPEAKTTSWrapper
from aeneas.ttswrappers.festivalttswrapper import FESTIVALTTSWrapper
from aeneas.ttswrappers.macosttswrapper import MacOSTTSWrapper
from aeneas.ttswrappers.nuancettswrapper import NuanceTTSWrapper
import aeneas.globalfunctions as gf


class Synthesizer(Loggable):
    """
    A class to synthesize text fragments into
    an audio file,
    along with the corresponding time anchors.

    :param rconf: a runtime configuration
    :type  rconf: :class:`~aeneas.runtimeconfiguration.RuntimeConfiguration`
    :param logger: the logger object
    :type  logger: :class:`~aeneas.logger.Logger`
    :raises: OSError: if a custom TTS engine is requested
                      but it cannot be loaded
    :raises: ImportError: if the AWS Polly TTS API wrapper is requested
                          but the ``boto3`` module is not installed, or
                          if the Nuance TTS API wrapper is requested
                          but the``requests`` module is not installed
    """

    AWS = "aws"
    """ Select AWS Polly TTS API wrapper """

    CUSTOM = "custom"
    """ Select custom TTS engine wrapper """

    ESPEAK = "espeak"
    """ Select eSpeak wrapper """

    ESPEAKNG = "espeak-ng"
    """ Select eSpeak-ng wrapper """

    FESTIVAL = "festival"
    """ Select Festival wrapper """

    MACOS = "macos"
    """ Select macOS "say" wrapper """

    NUANCE = "nuance"
    """ Select Nuance TTS API wrapper """

    ALLOWED_VALUES = [AWS, CUSTOM, ESPEAK, ESPEAKNG, FESTIVAL, MACOS, NUANCE]
    """ List of all the allowed values """

    TAG = "Synthesizer"

    def __init__(self, rconf=None, logger=None):
        super().__init__(rconf=rconf, logger=logger)
        self.tts_engine = None
        self._select_tts_engine()

    def _select_tts_engine(self):
        """
        Select the TTS engine to be used by looking at the rconf object.
        """
        self.log("Selecting TTS engine...")
        requested_tts_engine = self.rconf[RuntimeConfiguration.TTS]
        tts_cls = None
        match requested_tts_engine:
            case self.CUSTOM:
                self.log("TTS engine: custom")
                tts_path = self.rconf[RuntimeConfiguration.TTS_PATH]
                if tts_path is None:
                    self.log_exc(
                        "You must specify a value for tts_path", None, True, ValueError
                    )
                if not gf.file_can_be_read(tts_path):
                    self.log_exc("Cannot read tts_path", None, True, OSError)
                try:
                    import imp

                    self.log(["Loading CustomTTSWrapper module from '%s'...", tts_path])
                    imp.load_source("CustomTTSWrapperModule", tts_path)
                    self.log(
                        ["Loading CustomTTSWrapper module from '%s'... done", tts_path]
                    )
                    self.log("Importing CustomTTSWrapper...")
                    from CustomTTSWrapperModule import CustomTTSWrapper

                    self.log("Importing CustomTTSWrapper... done")
                    tts_cls = CustomTTSWrapper
                except Exception as exc:
                    self.log_exc(
                        "Unable to load custom TTS wrapper", exc, True, OSError
                    )
            case self.AWS:
                if importlib.util.find_spec("boto3") is None:
                    self.log_exc(
                        "Unable to import boto3 for AWS Polly TTS API wrapper",
                        critical=True,
                        raise_type=ImportError,
                    )
                tts_cls = AWSTTSWrapper
            case self.NUANCE:
                if importlib.util.find_spec("requests") is None:
                    self.log_exc(
                        "Unable to import requests for Nuance TTS API wrapper",
                        critical=True,
                        raise_type=ImportError,
                    )
                tts_cls = NuanceTTSWrapper
            case self.ESPEAK:
                tts_cls = ESPEAKTTSWrapper
            case self.ESPEAKNG:
                tts_cls = ESPEAKNGTTSWrapper
            case self.FESTIVAL:
                tts_cls = FESTIVALTTSWrapper
            case self.MACOS:
                tts_cls = MacOSTTSWrapper
            case _ as other:
                self.log_exc(
                    f"Invalid TTS engine type {other!r}",
                    critical=True,
                    raise_type=ValueError,
                )

        self.log(f"Creating {type(tts_cls)} instance...")
        self.tts_engine = tts_cls(rconf=self.rconf, logger=self.logger)
        self.log(f"Creating {type(tts_cls)} instance... done")
        self.log("Selecting TTS engine... done")

    @property
    def output_audio_format(self):
        """
        Return a tuple ``(codec, channels, rate)``
        specifying the audio format
        generated by the actual TTS engine.

        :rtype: tuple
        """
        if self.tts_engine is not None:
            return self.tts_engine.OUTPUT_AUDIO_FORMAT
        return None

    def clear_cache(self):
        """
        Clear the TTS cache, removing all cache files from disk.

        .. versionadded:: 1.6.0
        """
        if self.tts_engine is not None:
            self.tts_engine.clear_cache()

    def synthesize(
        self,
        text_file: TextFile,
        audio_file_path: str,
        quit_after=None,
        backwards=False,
    ):
        """
        Synthesize the text contained in the given fragment list
        into a ``wav`` file.

        Return a tuple ``(anchors, total_time, num_chars)``.

        :param text_file: the text file to be synthesized
        :type  text_file: :class:`~aeneas.textfile.TextFile`
        :param string audio_file_path: the path to the output audio file
        :param float quit_after: stop synthesizing as soon as
                                 reaching this many seconds
        :param bool backwards: if ``True``, synthesizing from the end of the text file
        :rtype: tuple
        :raises: TypeError: if ``text_file`` is ``None`` or not an instance of ``TextFile``
        :raises: OSError: if ``audio_file_path`` cannot be written
        :raises: OSError: if ``tts=custom`` in the RuntimeConfiguration and ``tts_path`` cannot be read
        :raises: ValueError: if the TTS engine has not been set yet
        """
        if text_file is None:
            self.log_exc("text_file is None", None, True, TypeError)
        if not isinstance(text_file, TextFile):
            self.log_exc(
                "text_file is not an instance of TextFile", None, True, TypeError
            )
        if not gf.file_can_be_written(audio_file_path):
            self.log_exc(
                ["Audio file path '%s' cannot be written", audio_file_path],
                None,
                True,
                OSError,
            )
        if self.tts_engine is None:
            self.log_exc("Cannot select the TTS engine", None, True, ValueError)

        # synthesize
        self.log("Synthesizing text...")
        result = self.tts_engine.synthesize_multiple(
            text_file=text_file,
            output_file_path=audio_file_path,
            quit_after=quit_after,
            backwards=backwards,
        )
        self.log("Synthesizing text... done")

        # check that the output file has been written
        if not os.path.isfile(audio_file_path):
            self.log_exc(
                ["Audio file path '%s' cannot be read", audio_file_path],
                None,
                True,
                OSError,
            )

        return result
