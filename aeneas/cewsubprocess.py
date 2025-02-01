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

* :class:`aeneas.cewsubprocess.CEWSubprocess` which is an
  helper class executes the :mod:`aeneas.cew` C extension
  in a separate process via ``subprocess``.

This module works around a problem with the ``eSpeak`` library,
which seems to generate different audio data for the same
input parameters/text, when run multiple times in the same process.
See the following discussions for details:

#. https://groups.google.com/d/msg/aeneas-forced-alignment/NLbtSRf2_vg/mMHuTQiFEgAJ
#. https://sourceforge.net/p/espeak/mailman/message/34861696/

.. warning:: This module might be removed in a future version.

.. versionadded:: 1.5.0
"""

import argparse
import logging
import subprocess
import sys
import tempfile

from aeneas.exacttiming import TimeValue
from aeneas.logger import Configurable
from aeneas.runtimeconfiguration import RuntimeConfiguration

logger = logging.getLogger(__name__)


class CEWSubprocess(Configurable):
    """
    This helper class executes the ``aeneas.cew`` C extension
    in a separate process by running
    the :func:`aeneas.cewsubprocess.CEWSubprocess.main` function
    via ``subprocess``.

    :param rconf: a runtime configuration
    :type  rconf: :class:`~aeneas.runtimeconfiguration.RuntimeConfiguration`
    """

    def synthesize_multiple(self, audio_file_path, c_quit_after, c_backwards, u_text):
        """
        Synthesize the text contained in the given fragment list
        into a ``wav`` file.

        :param string audio_file_path: the path to the output audio file
        :param float c_quit_after: stop synthesizing as soon as
                                   reaching this many seconds
        :param bool c_backwards: synthesizing from the end of the text file
        :param object u_text: a list of ``(voice_code, text)`` tuples
        :rtype: tuple ``(sample_rate, synthesized, intervals)``
        """
        logger.debug("Audio file path: %r", audio_file_path)
        logger.debug("c_quit_after: '%.3f'", c_quit_after)
        logger.debug("c_backwards: '%d'", c_backwards)

        with (
            tempfile.NamedTemporaryFile(suffix=".text") as tmp_text_file,
            tempfile.NamedTemporaryFile(suffix=".data") as tmp_data_file,
        ):
            text_file_path = tmp_text_file.name
            data_file_path = tmp_data_file.name

            logger.debug("Temporary text file path: %r", text_file_path)
            logger.debug("Temporary data file path: %r", data_file_path)

            logger.debug("Populating the text file...")
            with open(text_file_path, "w", encoding="utf-8") as tmp_text_file:
                for f_voice_code, f_text in u_text:
                    tmp_text_file.write(f"{f_voice_code} {f_text}\n")
            logger.debug("Populating the text file... done")

            arguments = [
                self.rconf[RuntimeConfiguration.CEW_SUBPROCESS_PATH],
                "-m",
                "aeneas.cewsubprocess",
                f"{c_quit_after:.3f}",
                f"{c_backwards:d}",
                text_file_path,
                audio_file_path,
                data_file_path,
            ]
            logger.debug("Calling with arguments: '%s'", " ".join(arguments))
            subprocess.check_call(
                arguments,
                stdout=subprocess.PIPE,
                stdin=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
            )

            logger.debug("Reading output data...")
            with open(data_file_path, encoding="utf-8") as data_file:
                lines = data_file.read().splitlines()
                sample_rate = int(lines[0])
                synthesized_frames = int(lines[1])
                intervals = []
                for line in lines[2:]:
                    values = line.split(" ")
                    if len(values) == 2:
                        intervals.append((TimeValue(values[0]), TimeValue(values[1])))
            logger.debug("Reading output data... done")

        return (sample_rate, synthesized_frames, intervals)


def main() -> int:
    """
    Run ``aeneas.cew``, reading input text from file and writing audio and interval data to file.
    """

    parser = argparse.ArgumentParser()
    parser.add_argument("quit_after", type=float)
    parser.add_argument("backwards", type=int)
    parser.add_argument("text_file_path")
    parser.add_argument("audio_file_path")
    parser.add_argument("data_file_path")
    args = parser.parse_args()

    # read (voice_code, text) from file
    c_text = []
    with open(args.text_file_path, encoding="utf-8") as text:
        for line in text.readlines():
            # NOTE: not using strip() to avoid removing trailing blank characters
            line = line.replace("\n", "").replace("\r", "")
            idx = line.find(" ")
            if idx > 0:
                f_voice_code = line[:idx]
                f_text = line[(idx + 1) :]
                c_text.append((f_voice_code, f_text))

    import aeneas.cew.cew as cew

    sample_rate, synthesized_frames, intervals = cew.synthesize_multiple(
        args.audio_file_path, args.quit_after, args.backwards, c_text
    )
    with open(args.data_file_path, mode="w", encoding="utf-8") as data:
        data.write(f"{sample_rate}\n")
        data.write(f"{synthesized_frames}\n")
        data.write("\n".join([f"{begin:.3f} {end:.3f}" for begin, end in intervals]))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
