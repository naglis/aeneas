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
Execute a Job, passed as a container or
as a container and a configuration string
(i.e., from a wizard).
"""

import logging
import sys

from aeneas.executejob import ExecuteJob
from aeneas.job import JobConfiguration
from aeneas.runtimeconfiguration import RuntimeConfiguration
from aeneas.tools.abstract_cli_program import AbstractCLIProgram
from aeneas.validator import Validator
import aeneas.globalfunctions as gf

logger = logging.getLogger(__name__)


class ExecuteJobCLI(AbstractCLIProgram):
    """
    Execute a Job, passed as a container or
    as a container and a configuration string
    (i.e., from a wizard).
    """

    CONTAINER_FILE = gf.relative_path("res/job.zip", __file__)
    CONTAINER_FILE_NO_CONFIG = gf.relative_path("res/job_no_config.zip", __file__)
    OUTPUT_DIRECTORY = "output/"
    CONFIG_STRING = "is_hierarchy_type=flat|is_hierarchy_prefix=assets/|is_text_file_relative_path=.|is_text_file_name_regex=.*\\.xhtml|is_text_type=unparsed|is_audio_file_relative_path=.|is_audio_file_name_regex=.*\\.mp3|is_text_unparsed_id_regex=f[0-9]+|is_text_unparsed_id_sort=numeric|os_job_file_name=demo_sync_job_output|os_job_file_container=zip|os_job_file_hierarchy_type=flat|os_job_file_hierarchy_prefix=assets/|os_task_file_name=\\$PREFIX.xhtml.smil|os_task_file_format=smil|os_task_file_smil_page_ref=\\$PREFIX.xhtml|os_task_file_smil_audio_ref=../Audio/\\$PREFIX.mp3|job_language=eng|job_description=Demo Sync Job"

    PARAMETERS = JobConfiguration.parameters(sort=True, as_strings=True)

    NAME = gf.file_name_without_extension(__file__)

    HELP = {
        "description": "Execute a Job, passed as a container.",
        "synopsis": [
            ("--list-parameters", False),
            ("CONTAINER OUTPUT_DIR [CONFIG_STRING]", True),
        ],
        "examples": [
            f"{CONTAINER_FILE} {OUTPUT_DIRECTORY}",
            f"{CONTAINER_FILE} {OUTPUT_DIRECTORY} --cewsubprocess",
            '{} {} "{}"'.format(
                CONTAINER_FILE_NO_CONFIG, OUTPUT_DIRECTORY, CONFIG_STRING
            ),
        ],
        "options": [
            "--cewsubprocess : run cew in separate process (see docs)",
            "--skip-validator : do not validate the given container and/or config string",
        ],
        "parameters": [],
    }

    def perform_command(self):
        """
        Perform command and return the appropriate exit code.

        :rtype: int
        """
        if self.has_option(["--list-parameters"]):
            return self.print_parameters()

        if len(self.actual_arguments) < 2:
            return self.print_help()

        container_path = self.actual_arguments[0]
        output_directory_path = self.actual_arguments[1]
        config_string = None
        if len(self.actual_arguments) > 2 and not self.actual_arguments[2].startswith(
            "-"
        ):
            config_string = self.actual_arguments[2]
        validate = not self.has_option("--skip-validator")
        if self.has_option("--cewsubprocess"):
            self.rconf[RuntimeConfiguration.CEW_SUBPROCESS_ENABLED] = True

        if not self.check_input_file_or_directory(container_path):
            return self.ERROR_EXIT_CODE

        if not self.check_output_directory(output_directory_path):
            return self.ERROR_EXIT_CODE

        if validate:
            try:
                self.print_info(
                    "Validating the container (specify --skip-validator to bypass)..."
                )
                validator = Validator(rconf=self.rconf)
                result = validator.check_container(
                    container_path, config_string=config_string
                )
                if not result.passed:
                    self.print_error(
                        f"The given container is not valid: {result.pretty_print()}"
                    )
                    return self.ERROR_EXIT_CODE
            except Exception:
                logger.exception(
                    "An unexpected error occurred while validating the container"
                )
                return self.ERROR_EXIT_CODE

        try:
            self.print_info("Loading job from container...")
            executor = ExecuteJob(rconf=self.rconf)
            executor.load_job_from_container(container_path, config_string)
        except Exception:
            logger.exception("An unexpected error occurred while loading the job")
            return self.ERROR_EXIT_CODE

        try:
            self.print_info("Executing...")
            executor.execute()
        except Exception:
            logger.exception("An unexpected error occurred while executing the job")
            return self.ERROR_EXIT_CODE

        try:
            self.print_info("Creating output container...")
            path = executor.write_output_container(output_directory_path)
            self.print_info(f"Created output file {path!r}")
            executor.clean(True)
            return self.NO_ERROR_EXIT_CODE
        except Exception:
            logger.exception(
                "An unexpected error occurred while writing the output container"
            )

        return self.ERROR_EXIT_CODE

    def print_parameters(self):
        """
        Print the list of parameters and exit.
        """
        self.print_info("Available parameters:")
        self.print_generic("\n" + "\n".join(self.PARAMETERS) + "\n")
        return self.HELP_EXIT_CODE


def main():
    """
    Execute program.
    """
    ExecuteJobCLI().run(arguments=sys.argv)


if __name__ == "__main__":
    main()
