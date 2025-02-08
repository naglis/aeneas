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
Read audio file properties using the ``ffprobe`` wrapper.
"""

import os.path
import sys

from aeneas.ffprobewrapper import (
    FFPROBEParsingError,
    FFPROBEPathError,
    FFPROBEUnsupportedFormatError,
    FFPROBEWrapper,
)
from aeneas.runtimeconfiguration import RuntimeConfiguration
from aeneas.tools.abstract_cli_program import AbstractCLIProgram
import aeneas.globalfunctions as gf


class FFPROBEWrapperCLI(AbstractCLIProgram):
    """
    Read audio file properties using the ``ffprobe`` wrapper.
    """

    AUDIO_FILE = gf.relative_path("res/audio.mp3", __file__)

    NAME = os.path.splitext(__file__)[0]

    HELP = {
        "description": "Read audio file properties using the ffprobe wrapper.",
        "synopsis": [("AUDIO_FILE", True)],
        "options": [],
        "examples": [str(AUDIO_FILE)],
        "parameters": [],
    }

    def perform_command(self):
        """
        Perform command and return the appropriate exit code.

        :rtype: int
        """
        if len(self.actual_arguments) < 1:
            return self.print_help()
        audio_file_path = self.actual_arguments[0]

        if not self.check_input_file(audio_file_path):
            return self.ERROR_EXIT_CODE

        try:
            prober = FFPROBEWrapper(rconf=self.rconf)
            properties = prober.read_properties(audio_file_path)
            self.print_generic(f"duration {properties.duration}")
            self.print_generic(f"codec_name {properties.codec_name}")
            self.print_generic(f"sample_rate {properties.sample_rate}")
            self.print_generic(f"channels {properties.channels}")
            return self.NO_ERROR_EXIT_CODE
        except FFPROBEPathError:
            self.print_error(
                f"Unable to call the ffprobe executable {self.rconf[RuntimeConfiguration.FFPROBE_PATH]!r}. "
                "Make sure the path to ffprobe is correct."
            )
        except (FFPROBEUnsupportedFormatError, FFPROBEParsingError):
            self.print_error(
                f"Cannot read properties of file {audio_file_path!r}. "
                "Make sure the input file has a format supported by ffprobe."
            )

        return self.ERROR_EXIT_CODE


def main():
    """
    Execute program.
    """
    FFPROBEWrapperCLI().run(arguments=sys.argv)


if __name__ == "__main__":
    main()
