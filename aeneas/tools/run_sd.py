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
Detect the audio head and/or tail of the given audio file.
"""

import os.path
import sys

from aeneas.audiofile import (
    AudioFileConverterError,
    AudioFileNotInitializedError,
    AudioFileUnsupportedFormatError,
)
from aeneas.audiofilemfcc import AudioFileMFCC
from aeneas.runtimeconfiguration import RuntimeConfiguration
from aeneas.sd import SD
from aeneas.textfile import TextFileFormat
from aeneas.tools.cli_program import CLIProgram
import aeneas.globalconstants as gc
import aeneas.globalfunctions as gf


class RunSDCLI(CLIProgram):
    """
    Detect the audio head and/or tail of the given audio file.
    """

    AUDIO_FILE = gf.relative_path("res/audio.mp3", __file__)
    PARAMETERS_HEAD = "--min-head=0.0 --max-head=5.0"
    PARAMETERS_TAIL = "--min-tail=1.0 --max-tail=5.0"
    TEXT_FILE = gf.relative_path("res/parsed.txt", __file__)

    NAME = os.path.splitext(__file__)[0]

    HELP = {
        "description": "Detect the audio head and/or tail of the given audio file.",
        "synopsis": [
            ("list 'fragment 1|fragment 2|...|fragment N' LANGUAGE AUDIO_FILE", True),
            (
                "[mplain|munparsed|parsed|plain|subtitles|unparsed] TEXT_FILE LANGUAGE AUDIO_FILE",
                True,
            ),
        ],
        "examples": [
            f"parsed {TEXT_FILE} eng {AUDIO_FILE}",
            f"parsed {TEXT_FILE} eng {AUDIO_FILE} {PARAMETERS_HEAD}",
            f"parsed {TEXT_FILE} eng {AUDIO_FILE} {PARAMETERS_TAIL}",
            "parsed {} eng {} {} {}".format(
                TEXT_FILE, AUDIO_FILE, PARAMETERS_HEAD, PARAMETERS_TAIL
            ),
        ],
        "options": [
            "--class-regex=REGEX : extract text from elements with class attribute matching REGEX (unparsed)",
            "--id-regex=REGEX : extract text from elements with id attribute matching REGEX (unparsed)",
            "--l1-id-regex=REGEX : extract text from level 1 elements with id attribute matching REGEX (munparsed)",
            "--l2-id-regex=REGEX : extract text from level 2 elements with id attribute matching REGEX (munparsed)",
            "--l3-id-regex=REGEX : extract text from level 3 elements with id attribute matching REGEX (munparsed)",
            "--max-head=DUR : audio head has at most DUR seconds",
            "--max-tail=DUR : audio tail has at most DUR seconds",
            "--min-head=DUR : audio head has at least DUR seconds",
            "--min-tail=DUR : audio tail has at least DUR seconds",
            "--sort=ALGORITHM : sort the matched element id attributes using ALGORITHM (lexicographic, numeric, unsorted)",
        ],
        "parameters": [],
    }

    def perform_command(self):
        """
        Perform command and return the appropriate exit code.

        :rtype: int
        """
        if len(self.actual_arguments) < 4:
            return self.print_help()
        text_format = gf.safe_unicode(self.actual_arguments[0])
        if text_format == "list":
            text = gf.safe_unicode(self.actual_arguments[1])
        elif text_format in TextFileFormat.ALLOWED_VALUES:
            text = self.actual_arguments[1]
            if not self.check_input_file(text):
                return self.ERROR_EXIT_CODE
        else:
            return self.print_help()

        l1_id_regex = self.has_option_with_value("--l1-id-regex")
        l2_id_regex = self.has_option_with_value("--l2-id-regex")
        l3_id_regex = self.has_option_with_value("--l3-id-regex")
        id_regex = self.has_option_with_value("--id-regex")
        sort = self.has_option_with_value("--sort")
        parameters = {
            gc.PPN_TASK_IS_TEXT_MUNPARSED_L1_ID_REGEX: l1_id_regex,
            gc.PPN_TASK_IS_TEXT_MUNPARSED_L2_ID_REGEX: l2_id_regex,
            gc.PPN_TASK_IS_TEXT_MUNPARSED_L3_ID_REGEX: l3_id_regex,
            gc.PPN_TASK_IS_TEXT_UNPARSED_ID_REGEX: id_regex,
            gc.PPN_TASK_IS_TEXT_UNPARSED_ID_SORT: sort,
        }
        if text_format == TextFileFormat.MUNPARSED and (
            l1_id_regex is None or l2_id_regex is None or l3_id_regex is None
        ):
            self.print_error(
                "You must specify --l1-id-regex and --l2-id-regex and --l3-id-regex for munparsed format"
            )
            return self.ERROR_EXIT_CODE
        if (
            text_format in (TextFileFormat.UNPARSED, TextFileFormat.UNPARSED_IMG)
            and id_regex is None
        ):
            self.print_error(
                "You must specify --id-regex for unparsed or unparsed_img formats"
            )
            return self.ERROR_EXIT_CODE

        language = gf.safe_unicode(self.actual_arguments[2])

        audio_file_path = self.actual_arguments[3]
        if not self.check_input_file(audio_file_path):
            return self.ERROR_EXIT_CODE

        text_file = self.get_text_file(text_format, text, parameters)
        if text_file is None:
            self.print_error("Unable to build a TextFile from the given parameters")
            return self.ERROR_EXIT_CODE
        elif len(text_file) == 0:
            self.print_error("No text fragments found")
            return self.ERROR_EXIT_CODE
        text_file.set_language(language)
        self.print_info(f"Read input text with {len(text_file):d} fragments")

        self.print_info("Reading audio...")
        try:
            audio_file_mfcc = AudioFileMFCC(audio_file_path, rconf=self.rconf)
        except AudioFileConverterError:
            self.print_error(
                f"Unable to call the ffmpeg executable {self.rconf[RuntimeConfiguration.FFMPEG_PATH]!r}. "
                "Make sure the path to ffmpeg is correct"
            )
            return self.ERROR_EXIT_CODE
        except (AudioFileUnsupportedFormatError, AudioFileNotInitializedError):
            self.print_error(
                f"Cannot read file {audio_file_path!r}. "
                "Check that its format is supported by ffmpeg."
            )
            return self.ERROR_EXIT_CODE
        except Exception as exc:
            self.print_error(
                f"An unexpected error occurred while reading the audio file: {exc}"
            )
            return self.ERROR_EXIT_CODE

        self.print_info("Running VAD...")
        audio_file_mfcc.run_vad()

        min_head = gf.safe_float(self.has_option_with_value("--min-head"), None)
        max_head = gf.safe_float(self.has_option_with_value("--max-head"), None)
        min_tail = gf.safe_float(self.has_option_with_value("--min-tail"), None)
        max_tail = gf.safe_float(self.has_option_with_value("--max-tail"), None)

        self.print_info("Detecting audio interval...")
        start_detector = SD(audio_file_mfcc, text_file, rconf=self.rconf)
        start, end = start_detector.detect_interval(
            min_head, max_head, min_tail, max_tail
        )
        self.print_info("Detecting audio interval... done")

        self.print_result(audio_file_mfcc.audio_length, start, end)
        return self.NO_ERROR_EXIT_CODE

    def print_result(self, audio_len, start, end):
        """
        Print result of SD.

        :param audio_len: the length of the entire audio file, in seconds
        :type  audio_len: float
        :param start: the start position of the spoken text
        :type  start: float
        :param end: the end position of the spoken text
        :type  end: float
        """
        msg = []
        zero = 0
        head_len = start
        text_len = end - start
        tail_len = audio_len - end
        msg.append("")
        msg.append(f"Head: {zero:.3f} {start:.3f} ({head_len:.3f})")
        msg.append(f"Text: {start:.3f} {end:.3f} ({text_len:.3f})")
        msg.append(f"Tail: {end:.3f} {audio_len:.3f} ({tail_len:.3f})")
        msg.append("")
        zero_h = gf.time_to_hhmmssmmm(0)
        start_h = gf.time_to_hhmmssmmm(start)
        end_h = gf.time_to_hhmmssmmm(end)
        audio_len_h = gf.time_to_hhmmssmmm(audio_len)
        head_len_h = gf.time_to_hhmmssmmm(head_len)
        text_len_h = gf.time_to_hhmmssmmm(text_len)
        tail_len_h = gf.time_to_hhmmssmmm(tail_len)
        msg.append(f"Head: {zero_h} {start_h} ({head_len_h})")
        msg.append(f"Text: {start_h} {end_h} ({text_len_h})")
        msg.append(f"Tail: {end_h} {audio_len_h} ({tail_len_h})")
        msg.append("")
        self.print_info("\n".join(msg))


def main():
    """
    Execute program.
    """
    RunSDCLI().run(arguments=sys.argv)


if __name__ == "__main__":
    main()
