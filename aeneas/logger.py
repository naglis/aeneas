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
This module contains the following classes:

* :class:`~aeneas.logger.Loggable`, a base class supporting logging and runtime configuration;
* :class:`~aeneas.logger.Logger`, a logger class for debugging and performance profiling.

"""

import datetime

from aeneas.runtimeconfiguration import RuntimeConfiguration
import aeneas.globalfunctions as gf


class Logger:
    """
    A logger class for debugging and performance profiling.

    :param bool tee: if ``True``, tee (i.e., log and print to stdout)
    :param int indentation: the initial indentation of the log
    :param bool tee_show_datetime: if ``True``, print date and time when teeing
    """

    DEBUG = "DEBU"
    """ ``DEBUG`` severity """

    INFO = "INFO"
    """ ``INFO`` severity """

    WARNING = "WARN"
    """ ``WARNING`` severity """

    CRITICAL = "CRIT"
    """ ``CRITICAL`` severity """

    ERROR = "ERRO"
    """ ``ERROR`` message """

    SUCCESS = "SUCC"
    """ ``SUCCESS`` message """

    def __init__(
        self, tee: bool = False, indentation: int = 0, tee_show_datetime: bool = True
    ):
        self.entries = []
        self.tee = tee
        self.indentation = indentation
        self.tee_show_datetime = tee_show_datetime

    def __len__(self) -> int:
        return len(self.entries)

    def __str__(self):
        return self.pretty_print()

    def __repr__(self):
        return f"Logger(tee={self.tee}, indentation={self.indentation:d}, tee_show_datetime={self.tee_show_datetime})"

    @property
    def tee(self) -> bool:
        """
        If ``True``, tee (i.e., log and print to stdout).

        :rtype: bool
        """
        return self.__tee

    @tee.setter
    def tee(self, tee: bool):
        self.__tee = tee

    @property
    def tee_show_datetime(self) -> bool:
        """
        If ``True``, print date and time when teeing.

        :rtype: bool
        """
        return self.__tee_show_datetime

    @tee_show_datetime.setter
    def tee_show_datetime(self, tee_show_datetime: bool):
        self.__tee_show_datetime = tee_show_datetime

    @property
    def indentation(self) -> int:
        """
        The current indentation of the log.
        Useful to visually distinguish log levels.

        :rtype: int
        """
        return self.__indentation

    @indentation.setter
    def indentation(self, indentation: int):
        self.__indentation = indentation

    def pretty_print(self, as_list=False, show_datetime=True) -> str | list[str]:
        """
        Return a string pretty print of the log entries.

        :param bool as_list: if ``True``, return a list of strings,
                             one for each entry, instead of a Unicode string
        :param bool show_datetime: if ``True``, show the date and time of the entries
        :rtype: string or list of strings
        """
        ppl = [entry.pretty_print(show_datetime) for entry in self.entries]
        if as_list:
            return ppl
        return "\n".join(ppl)

    def log(self, message, severity=INFO, tag=""):
        """
        Add a given message to the log, and return its time.

        :param string message: the message to be added
        :param severity: the severity of the message
        :type  severity: :class:`~aeneas.logger.Logger`
        :param string tag: the tag associated with the message;
                           usually, the name of the class generating the entry
        :rtype: datetime
        """
        entry = _LogEntry(
            severity=severity,
            time=datetime.datetime.now(),
            tag=tag,
            indentation=self.indentation,
            message=self._sanitize(message),
        )
        self.entries.append(entry)
        if self.tee:
            gf.safe_print(entry.pretty_print(show_datetime=self.tee_show_datetime))
        return entry.time

    def clear(self):
        """
        Clear the contents of the log.
        """
        self.entries = []

    def write(self, path):
        """
        Output the log to file.

        :param string path: the path of the log file to be written
        """
        with open(path, "w", encoding="utf-8") as log_file:
            log_file.write(self.pretty_print())

    @classmethod
    def _sanitize(cls, message):
        """
        Sanitize the given message,
        dealing with multiple arguments
        and/or string formatting.

        :param message: the log message to be sanitized
        :type  message: string or list of strings
        :rtype: string
        """
        if isinstance(message, list):
            if len(message) == 0:
                sanitized = "Empty log message"
            elif len(message) == 1:
                sanitized = message[0]
            else:
                sanitized = message[0] % tuple(message[1:])
        else:
            sanitized = message
        if not isinstance(sanitized, str):
            raise TypeError("The given log message is not a string")
        return sanitized


class _LogEntry:
    """
    A structure for a log entry.
    """

    def __init__(self, message, severity, tag, indentation, time):
        self.message = message
        self.severity = severity
        self.tag = tag
        self.indentation = indentation
        self.time = time

    def pretty_print(self, show_datetime=True):
        """
        Returns a Unicode string containing
        the pretty printing of a given log entry.

        :param bool show_datetime: if ``True``, print the date and time of the entry
        :rtype: string
        """
        if show_datetime:
            return "[{}] {} {}{}: {}".format(
                self.severity,
                self.time,
                " " * self.indentation,
                self.tag,
                self.message,
            )
        return "[{}] {}{}: {}".format(
            self.severity, " " * self.indentation, self.tag, self.message
        )

    @property
    def message(self):
        """
        The message of this log entry.

        :rtype: string
        """
        return self.__message

    @message.setter
    def message(self, message):
        self.__message = message

    @property
    def severity(self):
        """
        The severity of this log entry.

        :rtype: :class:`~aeneas.logger.Logger`
        """
        return self.__severity

    @severity.setter
    def severity(self, severity):
        self.__severity = severity

    @property
    def tag(self):
        """
        The tag of this log entry.

        :rtype: string
        """
        return self.__tag

    @tag.setter
    def tag(self, tag):
        self.__tag = tag

    @property
    def indentation(self):
        """
        The indentation of this log entry.

        :rtype: string
        """
        return self.__indentation

    @indentation.setter
    def indentation(self, indentation):
        self.__indentation = indentation

    @property
    def time(self):
        """
        The date and time of this log entry.

        :rtype: datetime.time
        """
        return self.__time

    @time.setter
    def time(self, time):
        self.__time = time


class Loggable:
    """
    A base class supporting logging and runtime configuration.

    :param logger: the logger object
    :type  logger: :class:`~aeneas.logger.Logger`
    :param rconf: the runtime configuration object
    :type  rconf: :class:`~aeneas.runtimeconfiguration.RuntimeConfiguration`
    """

    TAG = "Loggable"

    def __init__(self, logger=None, rconf=None):
        self.logger = logger if logger is not None else Logger()
        self.rconf = rconf if rconf is not None else RuntimeConfiguration()

    def _log(self, message, severity=Logger.DEBUG):
        """
        Log generic message

        :param string message: the message to log
        :param string severity: the message severity
        :rtype: datetime
        """
        return self.logger.log(message, severity, self.TAG)

    def log_exc(self, message, exc=None, critical=True, raise_type=None):
        """
        Log exception, and possibly raise exception.

        :param string message: the message to log
        :param Exception exc: the original exception
        :param bool critical: if ``True``, log as :data:`aeneas.logger.Logger.CRITICAL`;
                              otherwise as :data:`aeneas.logger.Logger.WARNING`
        :param Exception raise_type: if not ``None``, raise this Exception type
        """
        log_function = self.log_crit if critical else self.log_warn
        log_function(message)
        if exc is not None:
            log_function(["%s", exc])
        if raise_type is not None:
            raise_message = message
            if exc is not None:
                raise_message = f"{message} : {exc}"
            raise raise_type(raise_message)

    def log(self, message):
        """
        Log DEBUG message, and return its time.

        :param string message: the message to log
        :rtype: datetime
        """
        return self._log(message)

    def log_info(self, message):
        """
        Log INFO message, and return its time.

        :param string message: the message to log
        :rtype: datetime
        """
        return self._log(message, Logger.INFO)

    def log_warn(self, message):
        """
        Log WARNING message, and return its time.

        :param string message: the message to log
        :rtype: datetime
        """
        return self._log(message, Logger.WARNING)

    def log_crit(self, message):
        """
        Log CRITICAL message, and return its time.

        :param string message: the message to log
        :rtype: datetime
        """
        return self._log(message, Logger.CRITICAL)
