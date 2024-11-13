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
This "hydra" tool invokes another aeneas.tool,
according to the specified tool switch.
"""

import sys

from aeneas.tools.abstract_cli_program import AbstractCLIProgram
from aeneas.tools.convert_syncmap import ConvertSyncMapCLI
from aeneas.tools.download import DownloadCLI
from aeneas.tools.execute_job import ExecuteJobCLI
from aeneas.tools.execute_task import ExecuteTaskCLI
from aeneas.tools.extract_mfcc import ExtractMFCCCLI
from aeneas.tools.ffmpeg_wrapper import FFMPEGWrapperCLI
from aeneas.tools.ffprobe_wrapper import FFPROBEWrapperCLI
from aeneas.tools.plot_waveform import PlotWaveformCLI
from aeneas.tools.read_audio import ReadAudioCLI
from aeneas.tools.read_text import ReadTextCLI
from aeneas.tools.run_sd import RunSDCLI
from aeneas.tools.run_vad import RunVADCLI
from aeneas.tools.synthesize_text import SynthesizeTextCLI
from aeneas.tools.validate import ValidateCLI
import aeneas.globalfunctions as gf


class HydraCLI(AbstractCLIProgram):
    """
    This "hydra" tool invokes another aeneas.tool,
    according to the specified tool switch.
    """
    NAME = gf.file_name_without_extension(__file__)

    HELP = {
        "description": "Invoke the specified aeneas tool",
        "synopsis": [
            ("TOOL_PARAMETER TOOL_ARGUMENTS", True)
        ],
        "options": [
        ],
        "parameters": [
            "--convert-syncmap: call aeneas.tools.convert_syncmap",
            "--download: call aeneas.tools.download",
            "--execute-job: call aeneas.tools.execute_job",
            "--execute-task: call aeneas.tools.execute_task (default)",
            "--extract-mfcc: call aeneas.tools.extract_mfcc",
            "--ffmpeg-wrapper: call aeneas.tools.ffmpeg_wrapper",
            "--ffprobe-wrapper: call aeneas.tools.ffprobe_wrapper",
            "--plot-waveform: call aeneas.tools.plot_waveform",
            "--read-audio: call aeneas.tools.read_audio",
            "--read-text: call aeneas.tools.read_text",
            "--run-sd: call aeneas.tools.run_sd",
            "--run-vad: call aeneas.tools.run_vad",
            "--synthesize-text: call aeneas.tools.synthesize_text",
            "--validate: call aeneas.tools.validate",
        ],
        "examples": [
            "--execute-task --help",
            "--execute-task --examples",
            "--execute-task --example-json",
            "--execute-job --help",
        ]
    }

    TOOLS = [
        (ConvertSyncMapCLI, ["--convert-syncmap"]),
        (DownloadCLI, ["--download"]),
        (ExecuteJobCLI, ["--execute-job"]),
        (ExecuteTaskCLI, ["--execute-task"]),
        (ExtractMFCCCLI, ["--extract-mfcc"]),
        (FFMPEGWrapperCLI, ["--ffmpeg-wrapper"]),
        (FFPROBEWrapperCLI, ["--ffprobe-wrapper"]),
        (PlotWaveformCLI, ["--plot-waveform"]),
        (ReadAudioCLI, ["--read-audio"]),
        (ReadTextCLI, ["--read-text"]),
        (RunSDCLI, ["--run-sd"]),
        (RunVADCLI, ["--run-vad"]),
        (SynthesizeTextCLI, ["--synthesize-text"]),
        (ValidateCLI, ["--validate"]),
    ]

    def perform_command(self):
        """
        Perform command and return the appropriate exit code.

        :rtype: int
        """
        # if no actual arguments, print help
        if len(self.actual_arguments) < 1:
            return self.print_help(short=True)

        # check if we have a recognized tool switch
        for cls, switches in self.TOOLS:
            if self.has_option(switches):
                arguments = [a for a in sys.argv if a not in switches]
                return cls(invoke=(self.invoke + " %s" % switches[0])).run(arguments=arguments)

        # check if we have -h, --help, or --version
        if "-h" in self.actual_arguments:
            return self.print_help(short=True)
        if "--help" in self.actual_arguments:
            return self.print_help(short=False)
        if "--version" in self.actual_arguments:
            return self.print_name_version()

        # default to run ExecuteTaskCLI
        return ExecuteTaskCLI(invoke=self.invoke).run(arguments=sys.argv)


def main():
    """
    Execute program.
    """
    HydraCLI().run(arguments=sys.argv, show_help=False)

if __name__ == '__main__':
    main()
