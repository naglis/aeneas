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
Perform validation in one of the following modes:

1. a container
2. a job configuration string
3. a task configuration string
4. a container + configuration string from wizard
5. a job TXT configuration file
6. a job XML configuration file
"""

import sys

from aeneas.tools.abstract_cli_program import AbstractCLIProgram
from aeneas.validator import Validator
import aeneas.globalfunctions as gf


class ValidateCLI(AbstractCLIProgram):
    """
    Perform validation in one of the following modes:

    1. a container
    2. a job configuration string
    3. a task configuration string
    4. a container + configuration string from wizard
    5. a job TXT configuration file
    6. a job XML configuration file
    """

    CONFIG_FILE_TXT = gf.relative_path("res/config.txt", __file__)
    CONFIG_FILE_XML = gf.relative_path("res/config.xml", __file__)
    CONTAINER_FILE = gf.relative_path("res/job.zip", __file__)
    JOB_CONFIG_STRING = "job_language=ita|os_job_file_name=output.zip|os_job_file_container=zip|is_hierarchy_type=flat"
    TASK_CONFIG_STRING = "task_language=ita|is_text_type=plain|os_task_file_name=output.txt|os_task_file_format=txt"
    WRONG_CONFIG_STRING = "job_language=ita|invalid=string"
    GOOD_CONFIG_STRING = "is_hierarchy_type=flat|is_hierarchy_prefix=assets/|is_text_file_relative_path=.|is_text_file_name_regex=.*\\.xhtml|is_text_type=unparsed|is_audio_file_relative_path=.|is_audio_file_name_regex=.*\\.mp3|is_text_unparsed_id_regex=f[0-9]+|is_text_unparsed_id_sort=numeric|os_job_file_name=demo_sync_job_output|os_job_file_container=zip|os_job_file_hierarchy_type=flat|os_job_file_hierarchy_prefix=assets/|os_task_file_name=\\$PREFIX.xhtml.smil|os_task_file_format=smil|os_task_file_smil_page_ref=\\$PREFIX.xhtml|os_task_file_smil_audio_ref=../Audio/\\$PREFIX.mp3|job_language=eng|job_description=Demo Sync Job"

    NAME = gf.file_name_without_extension(__file__)

    HELP = {
        "description": "Perform validation of a config string or a container",
        "synopsis": [
            ("config CONFIG.TXT", True),
            ("config CONFIG.XML", True),
            ("container CONTAINER", True),
            ("job CONFIG_STRING", True),
            ("task CONFIG_STRING", True),
            ("wizard CONFIG_STRING CONTAINER", True),
        ],
        "options": [],
        "examples": [
            f"config {CONFIG_FILE_TXT}",
            f"config {CONFIG_FILE_XML}",
            f"container {CONTAINER_FILE}",
            f'job "{JOB_CONFIG_STRING}"',
            f'task "{TASK_CONFIG_STRING}"',
            f'wizard "{GOOD_CONFIG_STRING}" {CONTAINER_FILE}',
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
        mode = self.actual_arguments[0]

        validator = Validator(rconf=self.rconf)
        if mode == "config":
            config_file_path = self.actual_arguments[1]
            config_txt = None
            if config_file_path.lower().endswith(".txt"):
                config_txt = True
            elif config_file_path.lower().endswith(".xml"):
                config_txt = False
            else:
                return self.print_help()
            if not self.check_input_file(config_file_path):
                return self.ERROR_EXIT_CODE
            contents = gf.read_file_bytes(config_file_path)
            if contents is None:
                return self.ERROR_EXIT_CODE
            if config_txt:
                result = validator.check_config_txt(contents)
                msg = "TXT configuration"
            else:
                result = validator.check_config_xml(contents)
                msg = "XML configuration"
        elif mode == "container":
            container_path = self.actual_arguments[1]
            result = validator.check_container(container_path)
            msg = "container"
        elif mode == "job":
            config_string = self.actual_arguments[1]
            result = validator.check_configuration_string(config_string, is_job=True)
            msg = "job configuration string"
        elif mode == "task":
            config_string = self.actual_arguments[1]
            result = validator.check_configuration_string(
                config_string, is_job=False, external_name=True
            )
            msg = "task configuration string"
        elif mode == "wizard":
            if (len(self.actual_arguments) < 3) or (
                self.actual_arguments[2].startswith("-")
            ):
                return self.print_help()
            config_string = self.actual_arguments[1]
            container_path = self.actual_arguments[2]
            if not self.check_input_file(container_path):
                return self.ERROR_EXIT_CODE
            result = validator.check_container(
                container_path, config_string=config_string
            )
            msg = "container with configuration string from wizard"
        else:
            return self.print_help()

        if result.passed:
            self.print_info(f"Valid {msg}")
            for warning in result.warnings:
                self.print_warning(str(warning))
            return self.NO_ERROR_EXIT_CODE
        else:
            self.print_error(f"Invalid {msg}")
            for error in result.errors:
                self.print_error(str(error))

        return self.ERROR_EXIT_CODE


def main():
    """
    Execute program.
    """
    ValidateCLI().run(arguments=sys.argv)


if __name__ == "__main__":
    main()
