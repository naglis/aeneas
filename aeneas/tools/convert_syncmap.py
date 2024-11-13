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
Convert a sync map from a format to another.
"""

import sys

from aeneas.syncmap import SyncMap
from aeneas.syncmap import SyncMapFormat
from aeneas.tools.abstract_cli_program import AbstractCLIProgram
import aeneas.globalconstants as gc
import aeneas.globalfunctions as gf


class ConvertSyncMapCLI(AbstractCLIProgram):
    """
    Convert a sync map from a format to another.
    """
    AUDIO = gf.relative_path("res/audio.mp3", __file__)
    SMIL_PARAMETERS = "--audio-ref=audio/sonnet001.mp3 --page-ref=text/sonnet001.xhtml"
    SYNC_MAP_CSV = gf.relative_path("res/sonnet.csv", __file__)
    SYNC_MAP_JSON = gf.relative_path("res/sonnet.json", __file__)
    SYNC_MAP_ZZZ = gf.relative_path("res/sonnet.zzz", __file__)
    OUTPUT_HTML = "output/sonnet.html"
    OUTPUT_MAP_DAT = "output/syncmap.dat"
    OUTPUT_MAP_JSON = "output/syncmap.json"
    OUTPUT_MAP_SMIL = "output/syncmap.smil"
    OUTPUT_MAP_SRT = "output/syncmap.srt"
    OUTPUT_MAP_TXT = "output/syncmap.txt"

    NAME = gf.file_name_without_extension(__file__)

    HELP = {
        "description": "Convert a sync map from a format to another.",
        "synopsis": [
            ("INPUT_SYNCMAP OUTPUT_SYNCMAP", True),
            ("INPUT_SYNCMAP OUTPUT_HTML AUDIO_FILE --output-html", True),
        ],
        "examples": [
            "{} {}".format(SYNC_MAP_JSON, OUTPUT_MAP_SRT),
            "{} {} --output-format=txt".format(SYNC_MAP_JSON, OUTPUT_MAP_DAT),
            "{} {} --input-format=csv".format(SYNC_MAP_ZZZ, OUTPUT_MAP_TXT),
            "{} {} --language=en".format(SYNC_MAP_CSV, OUTPUT_MAP_JSON),
            "{} {} {}".format(SYNC_MAP_JSON, OUTPUT_MAP_SMIL, SMIL_PARAMETERS),
            "{} {} {} --output-html".format(SYNC_MAP_JSON, OUTPUT_HTML, AUDIO)
        ],
        "options": [
            "--audio-ref=REF : use REF for the audio ref attribute (smil, smilh, smilm)",
            "--input-format=FMT : input sync map file has format FMT",
            "--language=CODE : set language to CODE",
            "--output-format=FMT : output sync map file has format FMT",
            "--output-html : output HTML file for fine tuning",
            "--page-ref=REF : use REF for the text ref attribute (smil, smilh, smilm)"
        ]
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
        output_html = self.has_option("--output-html")

        if not self.check_input_file(input_file_path):
            return self.ERROR_EXIT_CODE
        input_sm_format = self.has_option_with_value("--input-format")
        if input_sm_format is None:
            input_sm_format = gf.file_extension(input_file_path)
        if not self.check_format(input_sm_format):
            return self.ERROR_EXIT_CODE

        if not self.check_output_file(output_file_path):
            return self.ERROR_EXIT_CODE

        if output_html:
            if len(self.actual_arguments) < 3:
                return self.print_help()
            audio_file_path = self.actual_arguments[2]
            if not self.check_input_file(audio_file_path):
                return self.ERROR_EXIT_CODE
        else:
            output_sm_format = self.has_option_with_value("--output-format")
            if output_sm_format is None:
                output_sm_format = gf.file_extension(output_file_path)
            if not self.check_format(output_sm_format):
                return self.ERROR_EXIT_CODE

        # TODO add a way to specify a text file for input formats like SMIL
        #      that do not carry the source text
        language = self.has_option_with_value("--language")
        audio_ref = self.has_option_with_value("--audio-ref")
        page_ref = self.has_option_with_value("--page-ref")
        parameters = {
            gc.PPN_SYNCMAP_LANGUAGE: language,
            gc.PPN_TASK_OS_FILE_SMIL_AUDIO_REF: audio_ref,
            gc.PPN_TASK_OS_FILE_SMIL_PAGE_REF: page_ref
        }

        try:
            self.print_info("Reading sync map in '{}' format from file '{}'".format(input_sm_format, input_file_path))
            self.print_info("Reading sync map...")
            syncmap = SyncMap(logger=self.logger)
            syncmap.read(input_sm_format, input_file_path, parameters)
            self.print_info("Reading sync map... done")
            self.print_info("Read %d sync map fragments" % (len(syncmap)))
        except Exception as exc:
            self.print_error("An unexpected error occurred while reading the input sync map:")
            self.print_error("%s" % (exc))
            return self.ERROR_EXIT_CODE

        if output_html:
            try:
                self.print_info("Writing HTML file...")
                syncmap.output_html_for_tuning(audio_file_path, output_file_path, parameters)
                self.print_info("Writing HTML file... done")
                self.print_success("Created HTML file '%s'" % (output_file_path))
                return self.NO_ERROR_EXIT_CODE
            except Exception as exc:
                self.print_error("An unexpected error occurred while writing the output HTML file:")
                self.print_error("%s" % (exc))
        else:
            try:
                self.print_info("Writing sync map...")
                syncmap.write(output_sm_format, output_file_path, parameters)
                self.print_info("Writing sync map... done")
                self.print_success("Created '{}' sync map file '{}'".format(output_sm_format, output_file_path))
                return self.NO_ERROR_EXIT_CODE
            except Exception as exc:
                self.print_error("An unexpected error occurred while writing the output sync map:")
                self.print_error("%s" % (exc))

        return self.ERROR_EXIT_CODE

    def check_format(self, sm_format):
        """
        Return ``True`` if the given sync map format is allowed,
        and ``False`` otherwise.

        :param sm_format: the sync map format to be checked
        :type  sm_format: Unicode string
        :rtype: bool
        """
        if sm_format not in SyncMapFormat.ALLOWED_VALUES:
            self.print_error("Sync map format '%s' is not allowed" % (sm_format))
            self.print_info("Allowed formats:")
            self.print_generic(" ".join(SyncMapFormat.ALLOWED_VALUES))
            return False
        return True


def main():
    """
    Execute program.
    """
    ConvertSyncMapCLI().run(arguments=sys.argv)

if __name__ == '__main__':
    main()
