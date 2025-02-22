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
An abstract class containing functions common
to the CLI programs in aeneas.tools.
"""

import abc
import logging
import os
import os.path
import sys
import tempfile
import typing

from aeneas import __version__ as aeneas_version
from aeneas.logger import Configurable
from aeneas.runtimeconfiguration import RuntimeConfiguration
from aeneas.textfile import TextFile, TextFileFormat
import aeneas.globalfunctions as gf

logger = logging.getLogger(__name__)


class CLIHelp(typing.TypedDict):
    description: str
    synopsis: typing.Sequence[tuple[str, bool]]
    options: typing.Sequence[str]
    parameters: typing.Sequence[str]
    examples: typing.Sequence[str]


class CLIProgram(Configurable, abc.ABC):
    """
    This class is an "abstract" CLI program.

    To create a new CLI program, create a new class,
    derived from this one, and overload
    ``NAME``, ``HELP``, and ``perform_command()``.

    :param use_sys: if ``True``, call ``sys.exit`` when needed;
                    otherwise, never call ``sys.exit`` and
                    just return a return code/value
    :type  use_sys: bool
    :param string invoke: the CLI command to be invoked
    :param rconf: a runtime configuration. Default: ``None``, meaning that
                  default settings will be used.
    :type  rconf: :class:`aeneas.runtimeconfiguration.RuntimeConfiguration`
    """

    NAME: typing.ClassVar[str] = os.path.splitext(__file__)[0]

    AENEAS_URL = "https://www.readbeyond.it/aeneas/"
    DOCS_URL = "https://www.readbeyond.it/aeneas/docs/"
    GITHUB_URL = "https://github.com/ReadBeyond/aeneas/"
    ISSUES_URL = "https://github.com/ReadBeyond/aeneas/issues/"
    RB_URL = "https://www.readbeyond.it"

    NO_ERROR_EXIT_CODE: typing.ClassVar[int] = 0
    ERROR_EXIT_CODE: typing.ClassVar[int] = 1
    HELP_EXIT_CODE: typing.ClassVar[int] = 2

    HELP: typing.ClassVar[CLIHelp] = {
        "description": "An abstract CLI program",
        "synopsis": [],
        "options": [],
        "parameters": [],
        "examples": [],
    }

    RCONF_PARAMETERS = RuntimeConfiguration.parameters(sort=True, as_strings=True)

    def __init__(self, use_sys: bool = True, invoke: str | None = None, rconf=None):
        super().__init__(rconf=rconf)
        self.invoke = (
            f"python -m aeneas.tools.{self.NAME}" if invoke is None else invoke
        )
        self.use_sys = use_sys
        self.formal_arguments_raw: list[str] = []
        self.formal_arguments: list[str] = []
        self.actual_arguments: list[str] = []

    PREFIX_TO_PRINT_FUNCTION = {
        logging.CRITICAL: gf.print_error,
        logging.DEBUG: gf.print_info,
        logging.ERROR: gf.print_error,
        logging.INFO: gf.print_info,
        logging.WARNING: gf.print_warning,
    }

    def print_generic(self, msg, prefix: int | None = None):
        """
        Print a message and log it.

        :param msg: the message
        :type  msg: Unicode string
        :param prefix: the (optional) prefix
        :type  prefix: Unicode string
        """
        if prefix is None:
            logger.info(msg)
        else:
            logger.log(prefix, msg)
        if self.use_sys:
            if prefix is not None and prefix in self.PREFIX_TO_PRINT_FUNCTION:
                self.PREFIX_TO_PRINT_FUNCTION[prefix](msg)
            else:
                gf.safe_print(msg)

    def print_error(self, msg: str):
        """
        Print an error message and log it.

        :param string msg: the message
        """
        self.print_generic(msg, logging.ERROR)

    def print_info(self, msg: str):
        """
        Print an info message and log it.

        :param string msg: the message
        """
        self.print_generic(msg, logging.INFO)

    def print_warning(self, msg: str):
        """
        Print a warning message and log it.

        :param string msg: the message
        """
        self.print_generic(msg, logging.WARNING)

    def exit(self, code: int):
        """
        Exit with the given exit code,
        possibly with ``sys.exit()``.

        :param code: the exit code
        :type  code: int
        :rtype: int
        """
        if self.use_sys:
            sys.exit(code)
        return code

    def print_help(self, short: bool = False):
        """
        Print help message and exit.

        :param short: print short help only
        :type  short: bool
        """
        header = [
            "",
            "NAME",
            f"  {self.NAME} - {self.HELP['description']}",
            "",
        ]

        synopsis = [
            "SYNOPSIS",
            f"  {self.invoke} [-h|--help|--help-rconf|--version]",
        ]
        if "synopsis" in self.HELP:
            for syn, opt in self.HELP["synopsis"]:
                synopsis.append(f"  {self.invoke} {syn}{' [OPTIONS]' if opt else ''}")

        synopsis.append("")

        options = [
            "  -h : print short help and exit",
            "  --help : print full help and exit",
            "  --help-rconf : list all runtime configuration parameters",
            "  --version : print the program name and version and exit",
            "  -l[=FILE], --log[=FILE] : log verbose output to tmp file or FILE if specified",
            "  -r=CONF, --runtime-configuration=CONF : apply runtime configuration CONF",
            "  -v, --verbose : verbose output",
            "  -vv, --very-verbose : verbose output, print date/time values",
        ]
        if "options" in self.HELP:
            for help_opt in self.HELP["options"]:
                options.append(f"  {help_opt}")
        options = ["OPTIONS"] + sorted(options) + [""]

        parameters = []
        if "parameters" in self.HELP and self.HELP["parameters"]:
            parameters.append("PARAMETERS")
            for par in self.HELP["parameters"]:
                parameters.append(f"  {par}")
            parameters.append("")

        examples = []
        if "examples" in self.HELP and self.HELP["examples"]:
            examples.append("EXAMPLES")
            for exa in self.HELP["examples"]:
                examples.append(f"  {self.invoke} {exa}")
            examples.append("")

        footer = [
            "EXIT CODES",
            f"  {self.NO_ERROR_EXIT_CODE:d} : no error",
            f"  {self.ERROR_EXIT_CODE:d} : error",
            f"  {self.HELP_EXIT_CODE:d} : help shown, no command run",
            "",
            "AUTHOR",
            "  Alberto Pettarin, http://www.albertopettarin.it/",
            "",
            "REPORTING BUGS",
            f"  Please use the GitHub Issues Web page : {self.ISSUES_URL}",
            "",
            "COPYRIGHT",
            "  2012-2017, Alberto Pettarin and ReadBeyond Srl",
            "  This software is available under the terms of the GNU Affero General Public License Version 3",
            "",
            "SEE ALSO",
            f"  Code repository  : {self.GITHUB_URL}",
            f"  Documentation    : {self.DOCS_URL}",
            f"  Project Web page : {self.AENEAS_URL}",
            "",
        ]

        msg = header + synopsis + options + parameters + examples
        if not short:
            msg += footer
        if self.use_sys:
            self.print_generic("\n".join(msg))
        return self.exit(self.HELP_EXIT_CODE)

    def print_name_version(self):
        """
        Print program name and version and exit.

        :rtype: int
        """
        if self.use_sys:
            self.print_generic(f"{self.NAME} v{aeneas_version}")
        return self.exit(self.HELP_EXIT_CODE)

    def print_rconf_parameters(self):
        """
        Print the list of runtime configuration parameters and exit.
        """
        if self.use_sys:
            self.print_info("Available runtime configuration parameters:")
            self.print_generic("\n" + "\n".join(self.RCONF_PARAMETERS) + "\n")
        return self.exit(self.HELP_EXIT_CODE)

    def run(self, arguments: list[str], *, show_help: bool = True) -> int:
        """
        Program entry point.

        Please note that the first item in ``arguments`` is discarded,
        as it is assumed to be the script/invocation name;
        pass a "dumb" placeholder if you call this method with
        an argument different that ``sys.argv``.

        :param arguments: the list of arguments
        :type  arguments: list
        :param show_help: if ``False``, do not show help on ``-h`` and ``--help``
        :type  show_help: bool
        :rtype: int
        """
        self.print_warning("CLIProgram commands are deprecated, use `python -m aeneas`")

        args = arguments[:]

        if show_help:
            if "-h" in args:
                return self.print_help(short=True)

            if "--help" in args:
                return self.print_help(short=False)

            if "--help-rconf" in args:
                return self.print_rconf_parameters()

            if "--version" in args:
                return self.print_name_version()

        # store formal arguments
        self.formal_arguments_raw = arguments
        self.formal_arguments = args

        # to obtain the actual arguments,
        # remove the first one and "special" switches
        args = args[1:]
        set_args = set(args)

        # set verbosity, if requested
        loglevel = logging.WARNING
        logformat = "%(levelname)s %(name)s %(message)s"
        for flag in {"-v", "--verbose"} & set_args:
            loglevel = logging.INFO
            args.remove(flag)
        for flag in {"-vv", "--very-verbose"} & set_args:
            loglevel = logging.DEBUG
            logformat = "%(asctime)s %(levelname)s %(name)s %(message)s"
            args.remove(flag)

        # set RuntimeConfiguration string, if specified
        for flag in ("-r", "--runtime-configuration"):
            rconf_string = self.has_option_with_value(flag, actual_arguments=False)
            if rconf_string is not None:
                self.rconf = RuntimeConfiguration(rconf_string)
                args.remove(f"{flag}={rconf_string}")

        # set log file path, if requested
        log_path = None
        for flag in ("-l", "--log"):
            log_path = self.has_option_with_value(flag, actual_arguments=False)
            if log_path is not None:
                args.remove(f"{flag}={log_path}")
            elif flag in set_args:
                with tempfile.NamedTemporaryFile(
                    prefix="aeneas.",
                    suffix=".log",
                    dir=self.rconf[RuntimeConfiguration.TMP_PATH],
                ) as tmp_file:
                    log_path = tmp_file.name

                args.remove(flag)

        logging.basicConfig(filename=log_path, level=loglevel, format=logformat)

        # if no actual arguments left, print help
        if not args and show_help:
            return self.print_help(short=True)

        # store actual arguments
        self.actual_arguments = args

        # create logger
        logger.debug("Running aeneas %s", aeneas_version)
        logger.debug("Formal arguments: %s", self.formal_arguments)
        logger.debug("Actual arguments: %s", self.actual_arguments)
        logger.debug("Runtime configuration: %r", self.rconf.config_string)

        # perform command
        exit_code = self.perform_command()
        logger.debug("Execution completed with code %d", exit_code)

        return self.exit(exit_code)

    def has_option(self, target: str | typing.Sequence[str]) -> bool:
        """
        Return ``True`` if the actual arguments include
        the specified ``target`` option or,
        if ``target`` is a list of options,
        at least one of them.

        :param target: the option or a list of options
        :type  target: Unicode string or list of Unicode strings
        :rtype: bool
        """
        if isinstance(target, str):
            target_set = {target}
        else:
            target_set = set(target)
        return len(target_set & set(self.actual_arguments)) > 0

    def has_option_with_value(
        self, prefix: str, *, actual_arguments: bool = True
    ) -> str | None:
        """
        Check if the actual arguments include an option
        starting with the given ``prefix`` and having a value,
        e.g. ``--format=ogg`` for ``prefix="--format"``.

        :param prefix: the option prefix
        :type  prefix: string
        :param actual_arguments: if ``True``, check among actual arguments;
                                 otherwise check among formal arguments
        :rtype actual_arguments: bool
        :rtype: string or None
        """
        if actual_arguments:
            args = self.actual_arguments
        else:
            args = self.formal_arguments
        for arg in [
            arg for arg in args if (arg is not None) and (arg.startswith(prefix + "="))
        ]:
            lis = arg.split("=")
            if len(lis) >= 2:
                return "=".join(lis[1:])
        return None

    @abc.abstractmethod
    def perform_command(self) -> int:
        """
        Perform command and return the appropriate exit code.

        :rtype: int
        """

    def check_c_extensions(self, name: str | None = None) -> bool:
        """
        If C extensions cannot be run, emit a warning
        and return ``False``. Otherwise return ``True``.
        If ``name`` is not ``None``, check just
        the C extension with that name.

        :param name: the name of the Python C extension to test
        :type  name: string
        :rtype: bool
        """
        if not gf.can_run_c_extension(name=name):
            if name is None:
                self.print_warning("Unable to load Python C Extensions")
            else:
                self.print_warning("Unable to load Python C Extension %s" % (name))
            self.print_warning("Running the slower pure Python code")
            self.print_warning(
                "See the documentation for directions to compile the Python C Extensions"
            )
            return False
        return True

    def check_input_file_or_directory(self, path: str) -> bool:
        """
        If the given path does not exist, emit an error
        and return ``False``. Otherwise return ``True``.

        :param path: the path of the input file or directory
        :type  path: string (path)
        :rtype: bool
        """
        if not (os.path.isfile(path) or os.path.isdir(path)):
            self.print_error(
                f"Path {path!r} does not exist or is not a file or directory"
            )
            return False
        return True

    def check_input_file(self, path: str) -> bool:
        """
        If the given path does not exist, emit an error
        and return ``False``. Otherwise return ``True``.

        :param path: the path of the input file
        :type  path: string (path)
        :rtype: bool
        """
        if not os.path.isfile(path):
            self.print_error(f"Path {path!r} does not exist or is not a file")
            return False
        return True

    def check_output_directory(self, path: str) -> bool:
        """
        If the given directory cannot be written, emit an error
        and return ``False``. Otherwise return ``True``.

        :param path: the path of the output directory
        :type  path: string (path)
        :rtype: bool
        """
        if not os.path.isdir(path):
            self.print_error(f"Directory {path!r} does not exist")
            return False
        return True

    def get_text_file(self, text_format: str, text, parameters):
        if text_format == "list":
            text_file = TextFile()
            text_file.read_from_list(text.split("|"))
            return text_file
        else:
            if text_format not in TextFileFormat.ALLOWED_VALUES:
                self.print_error(
                    f"File format {text_format!r} is not allowed. "
                    f"Allowed text file formats: {' '.join(TextFileFormat.ALLOWED_VALUES)}."
                )
                return None
            try:
                return TextFile(text, text_format, parameters)
            except OSError:
                self.print_error(f"Cannot read file {text!r}")
            return None
