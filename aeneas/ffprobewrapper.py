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

* :class:`~aeneas.ffprobewrapper.FFPROBEWrapper`, a wrapper around ``ffprobe`` to read the properties of an audio file;
* :class:`~aeneas.ffprobewrapper.FFPROBEParsingError`,
* :class:`~aeneas.ffprobewrapper.FFPROBEPathError`, and
* :class:`~aeneas.ffprobewrapper.FFPROBEUnsupportedFormatError`,
  representing errors while reading the properties of audio files.
"""

import json
import logging
import subprocess
import typing

from aeneas.exacttiming import TimeValue
from aeneas.logger import Configurable
from aeneas.runtimeconfiguration import RuntimeConfiguration

logger = logging.getLogger(__name__)


class Properties(typing.NamedTuple):
    duration: TimeValue
    codec_name: str | None
    sample_rate: int | None
    channels: int | None
    bit_rate: int | None


class FFPROBEParsingError(Exception):
    """
    Error raised when the call to ``ffprobe`` does not produce any output or parsing the output as JSON fails.
    """


class FFPROBEPathError(Exception):
    """
    Error raised when the path to ``ffprobe`` is not a valid executable.

    .. versionadded:: 1.4.1
    """


class FFPROBEUnsupportedFormatError(Exception):
    """
    Error raised when ``ffprobe`` cannot decode the format of the given file.
    """


class FFPROBEWrapper(Configurable):
    """
    Wrapper around ``ffprobe`` to read the properties of an audio file.

    It will perform a call like::

        $ ffprobe -select_streams a -show_streams /path/to/audio/file.mp3

    and it will parse the first ``[STREAM]`` element returned::

            [STREAM]
            index=0
            codec_name=mp3
            codec_long_name=MP3 (MPEG audio layer 3)
            profile=unknown
            codec_type=audio
            codec_time_base=1/44100
            codec_tag_string=[0][0][0][0]
            codec_tag=0x0000
            sample_fmt=s16p
            sample_rate=44100
            channels=1
            channel_layout=mono
            bits_per_sample=0
            id=N/A
            r_frame_rate=0/0
            avg_frame_rate=0/0
            time_base=1/14112000
            start_pts=0
            start_time=0.000000
            duration_ts=1545083190
            duration=109.487188
            bit_rate=128000
            max_bit_rate=N/A
            bits_per_raw_sample=N/A
            nb_frames=N/A
            nb_read_frames=N/A
            nb_read_packets=N/A
            DISPOSITION:default=0
            DISPOSITION:dub=0
            DISPOSITION:original=0
            DISPOSITION:comment=0
            DISPOSITION:lyrics=0
            DISPOSITION:karaoke=0
            DISPOSITION:forced=0
            DISPOSITION:hearing_impaired=0
            DISPOSITION:visual_impaired=0
            DISPOSITION:clean_effects=0
            DISPOSITION:attached_pic=0
            [/STREAM]

    :param rconf: a runtime configuration
    :type  rconf: :class:`~aeneas.runtimeconfiguration.RuntimeConfiguration`
    """

    FFPROBE_PARAMETERS = (
        "-hide_banner",
        "-select_streams",
        "a",
        "-show_streams",
        "-show_format",
        "-print_format",
        "json",
    )
    """ ``ffprobe`` parameters """

    def read_properties(self, audio_file_path: str) -> Properties:
        """
        Read the properties of an audio file
        and return them as a Properties named tuple.

        :param string audio_file_path: the path of the audio file to analyze
        :rtype: dict
        :raises: FFPROBEParsingError: if the call to ``ffprobe`` does not produce any output
        :raises: FFPROBEPathError: if the path to the ``ffprobe`` executable cannot be called
        :raises: FFPROBEUnsupportedFormatError: if the file has a format not supported by ``ffprobe``
        """
        # call ffprobe
        arguments = [
            self.rconf[RuntimeConfiguration.FFPROBE_PATH],
            *self.FFPROBE_PARAMETERS,
            audio_file_path,
        ]
        logger.debug("Calling with arguments %r", arguments)
        try:
            output = subprocess.check_output(
                arguments,
                text=True,
                stderr=subprocess.PIPE,
            )
        except OSError as exc:
            raise FFPROBEPathError(
                "Unable to call the %r ffprobe executable"
                % self.rconf[RuntimeConfiguration.FFPROBE_PATH]
            ) from exc
        except subprocess.CalledProcessError as exc:
            stderr = exc.stderr.strip()
            if stderr.endswith("No such file or directory"):
                raise OSError(f"Path {audio_file_path!r} does not exist") from exc
            else:
                raise FFPROBEUnsupportedFormatError(
                    f"ffprobe exited with status {exc.returncode!r}: {stderr}"
                ) from exc
        logger.debug("Call completed")

        # check there is some output
        if not output:
            raise FFPROBEParsingError("ffprobe produced no output")

        return self._parse_properties_json(output)

    def _parse_properties_json(self, data: str) -> Properties:
        duration = codec_name = sample_rate = channels = bit_rate = None
        try:
            json_data = json.loads(data)
        except json.JSONDecodeError as exc:
            raise FFPROBEParsingError(
                f"Failed to parse ffprobe output {data!r} as JSON"
            ) from exc

        try:
            stream = (json_data.get("streams") or [])[0]
        except IndexError:
            raise FFPROBEUnsupportedFormatError(
                "No streams could be detected",
            )

        def analyze_dict(d: dict):
            nonlocal duration, codec_name, sample_rate, channels, bit_rate
            for k, v in d.items():
                if k == "duration" and duration is None:
                    duration = TimeValue(v)
                elif k == "codec_name" and codec_name is None:
                    codec_name = v
                elif k == "sample_rate" and sample_rate is None:
                    sample_rate = int(v)
                elif k == "channels" and channels is None:
                    channels = int(v)
                elif k == "bit_rate" and bit_rate is None:
                    bit_rate = int(v)

        analyze_dict(stream)
        analyze_dict(json_data.get("format") or {})

        if duration is None:
            raise FFPROBEUnsupportedFormatError(
                "No duration could be detected. Unsupported audio file format?",
            )

        return Properties(
            duration=duration,
            codec_name=codec_name,
            sample_rate=sample_rate,
            channels=channels,
            bit_rate=bit_rate,
        )
