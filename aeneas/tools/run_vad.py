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
Extract a list of speech intervals from the given audio file,
using the MFCC energy-based VAD algorithm.
"""

import sys

from aeneas.audiofile import (
    AudioFileConverterError,
    AudioFileNotInitializedError,
    AudioFileUnsupportedFormatError,
)
from aeneas.audiofilemfcc import AudioFileMFCC
from aeneas.runtimeconfiguration import RuntimeConfiguration
from aeneas.tools.abstract_cli_program import AbstractCLIProgram
import aeneas.globalfunctions as gf


class RunVADCLI(AbstractCLIProgram):
    """
    Extract a list of speech intervals from the given audio file,
    using the MFCC energy-based VAD algorithm.
    """

    INPUT_FILE = gf.relative_path("res/audio.mp3", __file__)
    OUTPUT_BOTH = "output/both.txt"
    OUTPUT_NONSPEECH = "output/nonspeech.txt"
    OUTPUT_SPEECH = "output/speech.txt"
    MODES = ["both", "nonspeech", "speech"]

    NAME = gf.file_name_without_extension(__file__)

    HELP = {
        "description": "Extract a list of speech intervals using the MFCC energy-based VAD.",
        "synopsis": [("AUDIO_FILE [%s] [OUTPUT_FILE]" % ("|".join(MODES)), True)],
        "examples": [
            f"{INPUT_FILE} both {OUTPUT_BOTH}",
            f"{INPUT_FILE} nonspeech {OUTPUT_NONSPEECH}",
            f"{INPUT_FILE} speech {OUTPUT_SPEECH}",
        ],
        "options": [
            "-i, --index : output intervals as indices instead of seconds",
        ],
        "parameters": [],
    }

    def perform_command(self):
        """
        Perform command and return the appropriate exit code.

        :rtype: int
        """
        if len(self.actual_arguments) < 2:
            return self.print_help()
        audio_file_path = self.actual_arguments[0]
        mode = self.actual_arguments[1]
        if mode not in ("speech", "nonspeech", "both"):
            return self.print_help()
        output_file_path = None
        if len(self.actual_arguments) >= 3:
            output_file_path = self.actual_arguments[2]
        output_time = not self.has_option(["-i", "--index"])

        self.check_c_extensions("cmfcc")
        if not self.check_input_file(audio_file_path):
            return self.ERROR_EXIT_CODE

        self.print_info("Reading audio...")
        try:
            audio_file_mfcc = AudioFileMFCC(audio_file_path, rconf=self.rconf)
        except AudioFileConverterError:
            self.print_error(
                "Unable to call the ffmpeg executable %r"
                % (self.rconf[RuntimeConfiguration.FFMPEG_PATH])
            )
            self.print_error("Make sure the path to ffmpeg is correct")
            return self.ERROR_EXIT_CODE
        except (AudioFileUnsupportedFormatError, AudioFileNotInitializedError):
            self.print_error(
                f"Cannot read file {audio_file_path!r}. "
                "Check that its format is supported by ffmpeg"
            )
            return self.ERROR_EXIT_CODE
        except Exception as exc:
            self.print_error(
                f"An unexpected error occurred while reading the audio file: {exc}"
            )
            return self.ERROR_EXIT_CODE
        self.print_info("Reading audio... done")

        self.print_info("Executing VAD...")
        audio_file_mfcc.run_vad()
        self.print_info("Executing VAD... done")

        speech = audio_file_mfcc.intervals(speech=True, time=output_time)
        nonspeech = audio_file_mfcc.intervals(speech=False, time=output_time)
        if mode == "speech":
            if output_time:
                intervals = [(i.begin, i.end) for i in speech]
                template = "%.3f\t%.3f"
            else:
                intervals = speech
                template = "%d\t%d"
        elif mode == "nonspeech":
            if output_time:
                intervals = [(i.begin, i.end) for i in nonspeech]
                template = "%.3f\t%.3f"
            else:
                intervals = nonspeech
                template = "%d\t%d"
        elif mode == "both":
            if output_time:
                speech = [(i.begin, i.end, "speech") for i in speech]
                nonspeech = [(i.begin, i.end, "nonspeech") for i in nonspeech]
                template = "%.3f\t%.3f\t%s"
            else:
                speech = [(i[0], i[1], "speech") for i in speech]
                nonspeech = [(i[0], i[1], "nonspeech") for i in nonspeech]
                template = "%d\t%d\t%s"
            intervals = sorted(speech + nonspeech)
        self.write_to_file(output_file_path, intervals, template)

        return self.NO_ERROR_EXIT_CODE

    def write_to_file(self, output_file_path, intervals, template):
        """
        Write intervals to file.

        :param output_file_path: path of the output file to be written;
                                 if ``None``, print to stdout
        :type  output_file_path: string (path)
        :param intervals: a list of tuples, each representing an interval
        :type  intervals: list of tuples
        """
        msg = [template % interval for interval in intervals]
        if output_file_path is None:
            self.print_info("Intervals detected:")
            for line in msg:
                self.print_generic(line)
        else:
            with open(output_file_path, "w", encoding="utf-8") as output_file:
                output_file.write("\n".join(msg))

            self.print_info(f"Created file {output_file_path!r}")


def main():
    """
    Execute program.
    """
    RunVADCLI().run(arguments=sys.argv)


if __name__ == "__main__":
    main()
