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

* :class:`~aeneas.validator.Validator`, assessing whether user input is well-formed;
* :class:`~aeneas.validator.ValidatorResult`, a record holding validation result and possibly messages.
"""

import logging
import os.path

from aeneas.executetask import AdjustBoundaryAlgorithm
from aeneas.idsortingalgorithm import IDSortingAlgorithm
from aeneas.logger import Configurable
from aeneas.syncmap import SyncMapFormat, SyncMapHeadTailFormat
from aeneas.textfile import TextFileFormat
import aeneas.globalconstants as gc
import aeneas.globalfunctions as gf

logger = logging.getLogger(__name__)


class Validator(Configurable):
    """
    A validator to assess whether user input is well-formed.

    :param rconf: a runtime configuration
    :type  rconf: :class:`~aeneas.runtimeconfiguration.RuntimeConfiguration`
    """

    ALLOWED_VALUES = [
        #
        # NOTE disabling the check on language since now we support multiple TTS
        # COMMENTED (
        # COMMENTED     gc.PPN_TASK_LANGUAGE,
        # COMMENTED     Language.ALLOWED_VALUES
        # COMMENTED ),
        #
        (gc.PPN_TASK_IS_TEXT_FILE_FORMAT, TextFileFormat.ALLOWED_VALUES),
        (gc.PPN_TASK_OS_FILE_FORMAT, SyncMapFormat.ALLOWED_VALUES),
        (gc.PPN_TASK_IS_TEXT_UNPARSED_ID_SORT, IDSortingAlgorithm.ALLOWED_VALUES),
        (gc.PPN_TASK_ADJUST_BOUNDARY_ALGORITHM, AdjustBoundaryAlgorithm.ALLOWED_VALUES),
        (gc.PPN_TASK_OS_FILE_HEAD_TAIL_FORMAT, SyncMapHeadTailFormat.ALLOWED_VALUES),
    ]

    IMPLIED_PARAMETERS = (
        (
            # is_text_type=unparsed => is_text_unparsed_id_sort
            gc.PPN_TASK_IS_TEXT_FILE_FORMAT,
            [TextFileFormat.UNPARSED],
            [gc.PPN_TASK_IS_TEXT_UNPARSED_ID_SORT],
        ),
        (
            # is_text_type=munparsed => is_text_munparsed_l1_id_regex
            gc.PPN_TASK_IS_TEXT_FILE_FORMAT,
            [TextFileFormat.MUNPARSED],
            [gc.PPN_TASK_IS_TEXT_MUNPARSED_L1_ID_REGEX],
        ),
        (
            # is_text_type=munparsed => is_text_munparsed_l2_id_regex
            gc.PPN_TASK_IS_TEXT_FILE_FORMAT,
            [TextFileFormat.MUNPARSED],
            [gc.PPN_TASK_IS_TEXT_MUNPARSED_L2_ID_REGEX],
        ),
        (
            # is_text_type=munparsed => is_text_munparsed_l3_id_regex
            gc.PPN_TASK_IS_TEXT_FILE_FORMAT,
            [TextFileFormat.MUNPARSED],
            [gc.PPN_TASK_IS_TEXT_MUNPARSED_L3_ID_REGEX],
        ),
        (
            # is_text_type=unparsed => is_text_unparsed_class_regex or
            #                          is_text_unparsed_id_regex
            gc.PPN_TASK_IS_TEXT_FILE_FORMAT,
            [TextFileFormat.UNPARSED],
            [
                gc.PPN_TASK_IS_TEXT_UNPARSED_CLASS_REGEX,
                gc.PPN_TASK_IS_TEXT_UNPARSED_ID_REGEX,
            ],
        ),
        (
            # os_task_file_format=smil  => os_task_file_smil_audio_ref
            # os_task_file_format=smilh => os_task_file_smil_audio_ref
            # os_task_file_format=smilm => os_task_file_smil_audio_ref
            gc.PPN_TASK_OS_FILE_FORMAT,
            [SyncMapFormat.SMIL, SyncMapFormat.SMILH, SyncMapFormat.SMILM],
            [gc.PPN_TASK_OS_FILE_SMIL_AUDIO_REF],
        ),
        (
            # os_task_file_format=smil  => os_task_file_smil_page_ref
            # os_task_file_format=smilh => os_task_file_smil_page_ref
            # os_task_file_format=smilm => os_task_file_smil_page_ref
            gc.PPN_TASK_OS_FILE_FORMAT,
            [SyncMapFormat.SMIL, SyncMapFormat.SMILH, SyncMapFormat.SMILM],
            [gc.PPN_TASK_OS_FILE_SMIL_PAGE_REF],
        ),
        (
            # task_adjust_boundary_algorithm=percent => task_adjust_boundary_percent_value
            gc.PPN_TASK_ADJUST_BOUNDARY_ALGORITHM,
            [AdjustBoundaryAlgorithm.PERCENT],
            [gc.PPN_TASK_ADJUST_BOUNDARY_PERCENT_VALUE],
        ),
        (
            # task_adjust_boundary_algorithm=rate => task_adjust_boundary_rate_value
            gc.PPN_TASK_ADJUST_BOUNDARY_ALGORITHM,
            [AdjustBoundaryAlgorithm.RATE],
            [gc.PPN_TASK_ADJUST_BOUNDARY_RATE_VALUE],
        ),
        (
            # task_adjust_boundary_algorithm=rate_aggressive => task_adjust_boundary_rate_value
            gc.PPN_TASK_ADJUST_BOUNDARY_ALGORITHM,
            [AdjustBoundaryAlgorithm.RATEAGGRESSIVE],
            [gc.PPN_TASK_ADJUST_BOUNDARY_RATE_VALUE],
        ),
        (
            # task_adjust_boundary_algorithm=currentend => task_adjust_boundary_currentend_value
            gc.PPN_TASK_ADJUST_BOUNDARY_ALGORITHM,
            [AdjustBoundaryAlgorithm.AFTERCURRENT],
            [gc.PPN_TASK_ADJUST_BOUNDARY_AFTERCURRENT_VALUE],
        ),
        (
            # task_adjust_boundary_algorithm=rate => task_adjust_boundary_nextstart_value
            gc.PPN_TASK_ADJUST_BOUNDARY_ALGORITHM,
            [AdjustBoundaryAlgorithm.BEFORENEXT],
            [gc.PPN_TASK_ADJUST_BOUNDARY_BEFORENEXT_VALUE],
        ),
        (
            # task_adjust_boundary_algorithm=offset => task_adjust_boundary_offset_value
            gc.PPN_TASK_ADJUST_BOUNDARY_ALGORITHM,
            [AdjustBoundaryAlgorithm.OFFSET],
            [gc.PPN_TASK_ADJUST_BOUNDARY_OFFSET_VALUE],
        ),
    )

    TASK_REQUIRED_PARAMETERS = (
        gc.PPN_TASK_IS_TEXT_FILE_FORMAT,
        gc.PPN_TASK_LANGUAGE,
        gc.PPN_TASK_OS_FILE_FORMAT,
        gc.PPN_TASK_OS_FILE_NAME,
    )

    TASK_REQUIRED_PARAMETERS_EXTERNAL_NAME = (
        gc.PPN_TASK_IS_TEXT_FILE_FORMAT,
        gc.PPN_TASK_LANGUAGE,
        gc.PPN_TASK_OS_FILE_FORMAT,
    )

    TXT_REQUIRED_PARAMETERS = (
        gc.PPN_TASK_IS_TEXT_FILE_FORMAT,
        gc.PPN_TASK_OS_FILE_FORMAT,
        gc.PPN_TASK_OS_FILE_NAME,
    )

    XML_TASK_REQUIRED_PARAMETERS = (
        gc.PPN_TASK_IS_AUDIO_FILE_XML,
        gc.PPN_TASK_IS_TEXT_FILE_FORMAT,
        gc.PPN_TASK_IS_TEXT_FILE_XML,
        gc.PPN_TASK_LANGUAGE,
        gc.PPN_TASK_OS_FILE_FORMAT,
        gc.PPN_TASK_OS_FILE_NAME,
    )

    def __init__(self, rconf=None):
        super().__init__(rconf=rconf)
        self.result = None

    def check_file_encoding(self, input_file_path):
        """
        Check whether the given file is UTF-8 encoded.

        :param string input_file_path: the path of the file to be checked
        :rtype: :class:`~aeneas.validator.ValidatorResult`
        """
        logger.debug("Checking encoding of file %r", input_file_path)

        self.result = ValidatorResult()

        if self._are_safety_checks_disabled("check_file_encoding"):
            return self.result

        if not os.path.isfile(input_file_path):
            self._failed(f"File {input_file_path!r} cannot be read.")
            return self.result

        with open(input_file_path, "rb") as file_object:
            bstring = file_object.read()
            self._check_utf8_encoding(bstring)

        return self.result

    def check_raw_string(self, string, is_bstring: bool = True):
        """
        Check whether the given string
        is properly UTF-8 encoded,
        it is not empty, and
        it does not contain reserved characters.

        :param string string: the byte string or Unicode string to be checked
        :param bool is_bstring: if True, string is a byte string
        :rtype: :class:`~aeneas.validator.ValidatorResult`
        """
        logger.debug("Checking the given byte string")

        self.result = ValidatorResult()

        if self._are_safety_checks_disabled("check_raw_string"):
            return self.result

        if is_bstring:
            self._check_utf8_encoding(string)
            if not self.result.passed:
                return self.result
            string = gf.safe_unicode(string)

        self._check_not_empty(string)

        if not self.result.passed:
            return self.result

        self._check_reserved_characters(string)

        return self.result

    def check_configuration_string(self, config_string, external_name: bool = False):
        """
        Check whether the given task configuration string
        is well-formed (if ``is_bstring`` is ``True``)
        and it has all the required parameters.

        :param string config_string: the byte string or Unicode string to be checked
        :param bool external_name: if ``True``, the task name is provided externally,
                                   and it is not required to appear
                                   in the config string
        :rtype: :class:`~aeneas.validator.ValidatorResult`
        """
        logger.debug("Checking task configuration string")

        self.result = ValidatorResult()

        if self._are_safety_checks_disabled("check_configuration_string"):
            return self.result

        if external_name:
            required_parameters: tuple[str, str, str, str] | tuple[str, str, str] = (
                self.TASK_REQUIRED_PARAMETERS_EXTERNAL_NAME
            )
        else:
            required_parameters = self.TASK_REQUIRED_PARAMETERS

        is_bstring = isinstance(config_string, bytes)
        if is_bstring:
            logger.debug("Checking that config_string is well formed")
            self.check_raw_string(config_string, is_bstring=True)
            if not self.result.passed:
                return self.result
            config_string = gf.safe_unicode(config_string)

        logger.debug("Checking required parameters")
        parameters = gf.config_string_to_dict(config_string, self.result)
        self._check_required_parameters(required_parameters, parameters)
        logger.debug("Checking config_string: returning %s", self.result.passed)
        return self.result

    def _are_safety_checks_disabled(self, caller="unknown_function"):
        """
        Return ``True`` if safety checks are disabled.

        :param string caller: the name of the caller function
        :rtype: bool
        """
        if self.rconf.safety_checks:
            return False

        logger.warning("Safety checks disabled => %s passed", caller)

        return True

    def _failed(self, msg):
        """
        Log a validation failure.

        :param string msg: the error message
        """
        logger.debug(msg)
        self.result.passed = False
        self.result.add_error(msg)
        logger.debug("Failed")

    def _check_utf8_encoding(self, bstring):
        """
        Check whether the given sequence of bytes
        is properly encoded in UTF-8.

        :param bytes bstring: the byte string to be checked
        """
        if not isinstance(bstring, bytes):
            self._failed("The given string is not a sequence of bytes")
            return
        if not gf.is_utf8_encoded(bstring):
            self._failed("The given string is not encoded in UTF-8.")

    def _check_not_empty(self, string):
        """
        Check whether the given string has zero length.

        :param string string: the byte string or Unicode string to be checked
        """
        if not string:
            self._failed("The given string has zero length")

    def _check_reserved_characters(self, ustring):
        """
        Check whether the given Unicode string contains reserved characters.

        :param string ustring: the string to be checked
        """
        forbidden = [c for c in gc.CONFIG_RESERVED_CHARACTERS if c in ustring]
        if forbidden:
            self._failed(
                "The given string contains the reserved characters %r."
                % " ".join(forbidden)
            )

    def _check_allowed_values(self, parameters):
        """
        Check whether the given parameter value is allowed.
        Log messages into ``self.result``.

        :param dict parameters: the given parameters
        """
        for key, allowed_values in self.ALLOWED_VALUES:
            logger.debug("Checking allowed values for parameter %r", key)
            if key in parameters:
                value = parameters[key]
                if value not in allowed_values:
                    self._failed(
                        f"Parameter {key!r} has value {value!r} which is not allowed."
                    )
                    return
        logger.debug("Passed")

    def _check_implied_parameters(self, parameters):
        """
        Check whether at least one of the keys in implied_keys
        is in ``parameters``,
        when a given ``key=value`` is present in ``parameters``,
        for some value in values.
        Log messages into ``self.result``.

        :param dict parameters: the given parameters
        """
        for key, values, implied_keys in self.IMPLIED_PARAMETERS:
            logger.debug("Checking implied parameters by %r=%r", key, values)
            if key in parameters and parameters[key] in values:
                found = False
                for implied_key in implied_keys:
                    if implied_key in parameters:
                        found = True
                if not found:
                    if len(implied_keys) == 1:
                        msg = "Parameter '{}' is required when '{}'='{}'.".format(
                            implied_keys[0], key, parameters[key]
                        )
                    else:
                        msg = "At least one of [{}] is required when '{}'='{}'.".format(
                            ",".join(implied_keys), key, parameters[key]
                        )
                    self._failed(msg)
                    return
        logger.debug("Passed")

    def _check_required_parameters(self, required_parameters, parameters):
        """
        Check whether the given parameter dictionary contains
        all the required paramenters.
        Log messages into ``self.result``.

        :param list required_parameters: required parameters
        :param dict parameters: parameters specified by the user
        """
        logger.debug("Checking required parameters %r", required_parameters)
        if not parameters:
            self._failed("No parameters supplied.")
            return
        logger.debug("Checking no required parameter is missing")
        for req_param in required_parameters:
            if req_param not in parameters:
                self._failed(f"Required parameter {req_param!r} not set.")
                return
        logger.debug("Checking all parameter values are allowed")
        self._check_allowed_values(parameters)
        logger.debug("Checking all implied parameters are present")
        self._check_implied_parameters(parameters)
        return self.result


class ValidatorResult:
    """
    A structure to contain the result of a validation.
    """

    def __init__(self):
        self.passed = True
        self.warnings = []
        self.errors = []

    def __str__(self):
        msg = ["Passed: %s" % self.passed, self.pretty_print(warnings=True)]
        return "\n".join(msg)

    def pretty_print(self, warnings=False):
        """
        Pretty print warnings and errors.

        :param bool warnings: if ``True``, also print warnings.
        :rtype: string
        """
        msg = []
        if (warnings) and (len(self.warnings) > 0):
            msg.append("Warnings:")
            for warning in self.warnings:
                msg.append("  %s" % warning)
        if len(self.errors) > 0:
            msg.append("Errors:")
            for error in self.errors:
                msg.append("  %s" % error)
        return "\n".join(msg)

    @property
    def passed(self):
        """
        The result of a validation.

        Return ``True`` if passed, possibly with emitted warnings.

        Return ``False`` if not passed, that is, at least one error emitted.

        :rtype: bool
        """
        return self.__passed

    @passed.setter
    def passed(self, passed):
        self.__passed = passed

    @property
    def warnings(self):
        """
        The list of emitted warnings.

        :rtype: list of strings
        """
        return self.__warnings

    @warnings.setter
    def warnings(self, warnings):
        self.__warnings = warnings

    @property
    def errors(self):
        """
        The list of emitted errors.

        :rtype: list of strings
        """
        return self.__errors

    @errors.setter
    def errors(self, errors):
        self.__errors = errors

    def add_warning(self, message):
        """
        Add a message to the warnings.

        :param string message: the message to be added
        """
        self.warnings.append(message)

    def add_error(self, message):
        """
        Add a message to the errors.

        :param string message: the message to be added
        """
        self.errors.append(message)
