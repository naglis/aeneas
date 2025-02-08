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
Extract MFCCs from a given audio file.
"""

import sys
import numpy

from aeneas.audiofile import (
    AudioFileConverterError,
    AudioFileNotInitializedError,
    AudioFileUnsupportedFormatError,
)
from aeneas.audiofilemfcc import AudioFileMFCC
from aeneas.runtimeconfiguration import RuntimeConfiguration
from aeneas.tools.abstract_cli_program import AbstractCLIProgram
import aeneas.globalfunctions as gf


class ExtractMFCCCLI(AbstractCLIProgram):
    """
    Extract MFCCs from a given audio file.
    """

    INPUT_FILE = gf.relative_path("res/audio.wav", __file__)
    OUTPUT_FILE = "output/audio.wav.mfcc.txt"

    NAME = gf.file_name_without_extension(__file__)

    HELP = {
        "description": "Extract MFCCs from a given audio file as a fat matrix.",
        "synopsis": [("AUDIO_FILE OUTPUT_FILE", True)],
        "examples": [f"{INPUT_FILE} {OUTPUT_FILE}"],
        "options": [
            "-b, --binary : output MFCCs as a float64 binary file",
            "-d, --delete-first : do not output the 0th MFCC coefficient",
            "-n, --npy : output MFCCs as a NumPy .npy binary file",
            "-t, --transpose : transpose the MFCCs matrix, returning a tall matrix",
            "-z, --npz : output MFCCs as a NumPy compressed .npz binary file",
            "--format=FMT : output to text file using format FMT (default: '%.18e')",
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
        input_file_path = self.actual_arguments[0]
        output_file_path = self.actual_arguments[1]

        output_text_format = self.has_option_with_value("--format")
        if output_text_format is None:
            output_text_format = "%.18e"
        output_binary = self.has_option(["-b", "--binary"])
        output_npz = self.has_option(["-z", "--npz"])
        output_npy = self.has_option(["-n", "--npy"])
        delete_first = self.has_option(["-d", "--delete-first"])
        transpose = self.has_option(["-t", "--transpose"])

        self.check_c_extensions("cmfcc")
        if not self.check_input_file(input_file_path):
            return self.ERROR_EXIT_CODE

        try:
            mfccs = AudioFileMFCC(input_file_path, rconf=self.rconf).all_mfcc
            if delete_first:
                mfccs = mfccs[1:, :]
            if transpose:
                mfccs = mfccs.transpose()
            if output_binary:
                # save as a raw C float64 binary file
                mapped = numpy.memmap(
                    output_file_path, dtype="float64", mode="w+", shape=mfccs.shape
                )
                mapped[:] = mfccs[:]
                mapped.flush()
                del mapped
            elif output_npz:
                # save as a .npz compressed binary file
                with open(output_file_path, "wb") as output_file:
                    numpy.savez(output_file, mfccs)
            elif output_npy:
                # save as a .npy binary file
                with open(output_file_path, "wb") as output_file:
                    numpy.save(output_file, mfccs)
            else:
                # save as a text file
                # NOTE: in Python 2, passing the fmt value a Unicode string crashes NumPy
                #       hence, converting back to bytes, which works in Python 3 too
                numpy.savetxt(output_file_path, mfccs, fmt=output_text_format)
            self.print_info("MFCCs shape: %d %d" % (mfccs.shape))
            self.print_info(f"MFCCs saved to {output_file_path!r}")
            return self.NO_ERROR_EXIT_CODE
        except AudioFileConverterError:
            self.print_error(
                f"Unable to call the ffmpeg executable {self.rconf[RuntimeConfiguration.FFMPEG_PATH]!r}. "
                "Make sure the path to ffmpeg is correct."
            )
        except (AudioFileUnsupportedFormatError, AudioFileNotInitializedError):
            self.print_error(
                f"Cannot read file {input_file_path!r}. "
                "Check that its format is supported by ffmpeg."
            )
        except OSError as exc:
            self.print_error(f"Cannot write file {output_file_path!r}: {exc}")

        return self.ERROR_EXIT_CODE


def main():
    """
    Execute program.
    """
    ExtractMFCCCLI().run(arguments=sys.argv)


if __name__ == "__main__":
    main()
