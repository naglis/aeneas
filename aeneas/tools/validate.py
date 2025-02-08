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
Perform validation on a task configuration string
"""

import os.path
import sys

from aeneas.tools.abstract_cli_program import AbstractCLIProgram
from aeneas.validator import Validator


class ValidateCLI(AbstractCLIProgram):
    """
    Perform validation on a task configuration string
    """

    TASK_CONFIG_STRING = "task_language=ita|is_text_type=plain|os_task_file_name=output.txt|os_task_file_format=txt"

    NAME = os.path.splitext(__file__)[0]

    HELP = {
        "description": "Perform validation of a config string",
        "synopsis": [
            ("task CONFIG_STRING", True),
        ],
        "options": [],
        "examples": [
            f'task "{TASK_CONFIG_STRING}"',
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
        if mode == "task":
            config_string = self.actual_arguments[1]
            result = validator.check_configuration_string(
                config_string, external_name=True
            )
            msg = "task configuration string"
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
