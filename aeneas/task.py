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

* :class:`~aeneas.task.Task`, representing a task;
* :class:`~aeneas.task.TaskConfiguration`, representing a task configuration.
"""

import decimal
import logging
import os
import uuid
import typing

from aeneas.adjustboundaryalgorithm import AdjustBoundaryAlgorithm
from aeneas.audiofile import AudioFile
from aeneas.configuration import Configuration
from aeneas.exacttiming import TimeValue
from aeneas.language import Language
from aeneas.textfile import TextFile
import aeneas.globalconstants as gc
import aeneas.globalfunctions as gf

logger = logging.getLogger(__name__)


class Task:
    """
    A structure representing a task, that is,
    an audio file and an ordered set of text fragments
    to be synchronized.

    :param string config_string: the task configuration string
    :raises: TypeError: if ``config_string`` is not ``None`` and
                        it is not a Unicode string
    """

    def __init__(
        self, config: typing.Optional[typing.Union[str, "TaskConfiguration"]] = None
    ):
        self.identifier = str(uuid.uuid4())
        # relative to input container root
        self.audio_file_path = None
        # concrete path, file will be read from this!
        self.audio_file_path_absolute = None
        self.audio_file = None
        # relative to input container root
        self.text_file_path = None
        # concrete path, file will be read from this!
        self.text_file_path_absolute = None
        self.text_file = None
        # relative to output container root
        self.sync_map_file_path = None
        # concrete path, file will be written to this!
        self.sync_map_file_path_absolute = None
        self.sync_map = None

        self.configuration = None
        if config is not None:
            if isinstance(config, TaskConfiguration):
                self.configuration = config
            else:
                self.configuration = TaskConfiguration(config)

    def __str__(self):
        return (
            f"{gc.RPN_TASK_IDENTIFIER}: {self.identifier!r}"
            "\n"
            f"Configuration:\n{self.configuration}"
            "\n"
            f"Audio file path: {self.audio_file_path}"
            "\n"
            f"Audio file path (absolute): {self.audio_file_path_absolute}"
            "\n"
            f"Text file path: {self.text_file_path}"
            "\n"
            f"Text file path (absolute): {self.text_file_path_absolute}"
            "\n"
            f"Sync map file path: {self.sync_map_file_path}"
            "\n"
            f"Sync map file path (absolute): {self.sync_map_file_path_absolute}"
        )

    @property
    def identifier(self) -> str:
        """
        The identifier of the task.
        """
        return self.__identifier

    @identifier.setter
    def identifier(self, value):
        self.__identifier = value

    @property
    def audio_file_path_absolute(self):
        """
        The absolute path of the audio file.

        :rtype: string
        """
        return self.__audio_file_path_absolute

    @audio_file_path_absolute.setter
    def audio_file_path_absolute(self, audio_file_path_absolute):
        self.__audio_file_path_absolute = audio_file_path_absolute
        self._populate_audio_file()

    @property
    def text_file_path_absolute(self):
        """
        The absolute path of the text file.

        :rtype: string
        """
        return self.__text_file_path_absolute

    @text_file_path_absolute.setter
    def text_file_path_absolute(self, text_file_path_absolute):
        self.__text_file_path_absolute = text_file_path_absolute
        self._populate_text_file()

    @property
    def sync_map_file_path_absolute(self):
        """
        The absolute path of the sync map file.

        :rtype: string
        """
        return self.__sync_map_file_path_absolute

    @sync_map_file_path_absolute.setter
    def sync_map_file_path_absolute(self, sync_map_file_path_absolute):
        self.__sync_map_file_path_absolute = sync_map_file_path_absolute

    def sync_map_leaves(self, fragment_type=None):
        """
        Return the list of non-empty leaves
        in the sync map associated with the task.

        If ``fragment_type`` has been specified,
        return only leaves of that fragment type.

        :param int fragment_type: type of fragment to return
        :rtype: list

        .. versionadded:: 1.7.0
        """
        if self.sync_map is None or self.sync_map.fragments_tree is None:
            return []
        return [f for f in self.sync_map.leaves(fragment_type)]

    def output_sync_map_file(self, container_root_path=None):
        """
        Output the sync map file for this task.

        If ``container_root_path`` is specified,
        the output sync map file will be created
        at the path obtained by joining
        the ``container_root_path`` and the relative path
        of the sync map inside the container.

        Otherwise, the sync map file will be created at the path
        ``self.sync_map_file_path_absolute``.

        Return the the path of the sync map file created,
        or ``None`` if an error occurred.

        :param string container_root_path: the path to the root directory
                                           for the output container
        :rtype: string
        """
        if self.sync_map is None:
            raise TypeError("The sync_map object has not been set")

        if container_root_path is not None and self.sync_map_file_path is None:
            raise TypeError("The (internal) path of the sync map has been set")

        logger.debug("container_root_path is %s", container_root_path)
        logger.debug("self.sync_map_file_path is %s", self.sync_map_file_path)
        logger.debug(
            "self.sync_map_file_path_absolute is %s", self.sync_map_file_path_absolute
        )

        if container_root_path is not None and self.sync_map_file_path is not None:
            path = os.path.join(container_root_path, self.sync_map_file_path)
        elif self.sync_map_file_path_absolute:
            path = self.sync_map_file_path_absolute
        gf.ensure_parent_directory(path)
        logger.debug("Output sync map to %s", path)

        eaf_audio_ref = self.configuration["o_eaf_audio_ref"]
        head_tail_format = self.configuration["o_h_t_format"]
        levels = self.configuration["o_levels"]
        smil_audio_ref = self.configuration["o_smil_audio_ref"]
        smil_page_ref = self.configuration["o_smil_page_ref"]
        sync_map_format = self.configuration["o_format"]

        logger.debug("eaf_audio_ref is %s", eaf_audio_ref)
        logger.debug("head_tail_format is %s", head_tail_format)
        logger.debug("levels is %s", levels)
        logger.debug("smil_audio_ref is %s", smil_audio_ref)
        logger.debug("smil_page_ref is %s", smil_page_ref)
        logger.debug("sync_map_format is %s", sync_map_format)

        with open(path, mode="w", encoding="utf-8") as f:
            self.sync_map.dump(
                f,
                sync_map_format,
                parameters={
                    gc.PPN_TASK_OS_FILE_EAF_AUDIO_REF: eaf_audio_ref,
                    gc.PPN_TASK_OS_FILE_HEAD_TAIL_FORMAT: head_tail_format,
                    gc.PPN_TASK_OS_FILE_LEVELS: levels,
                    gc.PPN_TASK_OS_FILE_SMIL_AUDIO_REF: smil_audio_ref,
                    gc.PPN_TASK_OS_FILE_SMIL_PAGE_REF: smil_page_ref,
                },
            )
        return path

    def _populate_audio_file(self):
        """
        Create the ``self.audio_file`` object by reading
        the audio file at ``self.audio_file_path_absolute``.
        """
        logger.debug("Populate audio file...")
        if self.audio_file_path_absolute is not None:
            logger.debug(
                "audio_file_path_absolute is %r", self.audio_file_path_absolute
            )
            self.audio_file = AudioFile(file_path=self.audio_file_path_absolute)
            self.audio_file.read_properties()
        else:
            logger.debug("audio_file_path_absolute is None")
        logger.debug("Populate audio file... done")

    def _populate_text_file(self):
        """
        Create the ``self.text_file`` object by reading
        the text file at ``self.text_file_path_absolute``.
        """
        logger.debug("Populate text file...")
        if (
            self.text_file_path_absolute is not None
            and self.configuration["language"] is not None
        ):
            # the following values might be None
            parameters = {
                gc.PPN_TASK_IS_TEXT_FILE_IGNORE_REGEX: self.configuration[
                    "i_t_ignore_regex"
                ],
                gc.PPN_TASK_IS_TEXT_FILE_TRANSLITERATE_MAP: self.configuration[
                    "i_t_transliterate_map"
                ],
                gc.PPN_TASK_IS_TEXT_MPLAIN_WORD_SEPARATOR: self.configuration[
                    "i_t_mplain_word_separator"
                ],
                gc.PPN_TASK_IS_TEXT_MUNPARSED_L1_ID_REGEX: self.configuration[
                    "i_t_munparsed_l1_id_regex"
                ],
                gc.PPN_TASK_IS_TEXT_MUNPARSED_L2_ID_REGEX: self.configuration[
                    "i_t_munparsed_l2_id_regex"
                ],
                gc.PPN_TASK_IS_TEXT_MUNPARSED_L3_ID_REGEX: self.configuration[
                    "i_t_munparsed_l3_id_regex"
                ],
                gc.PPN_TASK_IS_TEXT_UNPARSED_CLASS_REGEX: self.configuration[
                    "i_t_unparsed_class_regex"
                ],
                gc.PPN_TASK_IS_TEXT_UNPARSED_ID_REGEX: self.configuration[
                    "i_t_unparsed_id_regex"
                ],
                gc.PPN_TASK_IS_TEXT_UNPARSED_ID_SORT: self.configuration[
                    "i_t_unparsed_id_sort"
                ],
                gc.PPN_TASK_OS_FILE_ID_REGEX: self.configuration["o_id_regex"],
            }
            self.text_file = TextFile(
                file_path=self.text_file_path_absolute,
                file_format=self.configuration["i_t_format"],
                parameters=parameters,
            )
            self.text_file.set_language(self.configuration["language"])
        else:
            logger.debug("text_file_path_absolute and/or language is None")
        logger.debug("Populate text file... done")


class TaskConfiguration(Configuration):
    """
    A structure representing a configuration for a task, that is,
    a series of directives for I/O and processing the task.

    Allowed keys:

    * :data:`~aeneas.globalconstants.PPN_TASK_CUSTOM_ID`                          or ``custom_id``
    * :data:`~aeneas.globalconstants.PPN_TASK_DESCRIPTION`                        or ``description``
    * :data:`~aeneas.globalconstants.PPN_TASK_LANGUAGE`                           or ``language``
    * :data:`~aeneas.globalconstants.PPN_TASK_ADJUST_BOUNDARY_AFTERCURRENT_VALUE` or ``aba_aftercurrent_value``
    * :data:`~aeneas.globalconstants.PPN_TASK_ADJUST_BOUNDARY_ALGORITHM`          or ``aba_algorithm``
    * :data:`~aeneas.globalconstants.PPN_TASK_ADJUST_BOUNDARY_BEFORENEXT_VALUE`   or ``aba_beforenext_value``
    * :data:`~aeneas.globalconstants.PPN_TASK_ADJUST_BOUNDARY_NO_ZERO`            or ``aba_no_zero``
    * :data:`~aeneas.globalconstants.PPN_TASK_ADJUST_BOUNDARY_OFFSET_VALUE`       or ``aba_offset_value``
    * :data:`~aeneas.globalconstants.PPN_TASK_ADJUST_BOUNDARY_PERCENT_VALUE`      or ``aba_percent_value``
    * :data:`~aeneas.globalconstants.PPN_TASK_ADJUST_BOUNDARY_RATE_VALUE`         or ``aba_rate_value``
    * :data:`~aeneas.globalconstants.PPN_TASK_ADJUST_BOUNDARY_NONSPEECH_MIN`      or ``aba_nonspeech_min``
    * :data:`~aeneas.globalconstants.PPN_TASK_ADJUST_BOUNDARY_NONSPEECH_STRING`   or ``aba_nonspeech_string``
    * :data:`~aeneas.globalconstants.PPN_TASK_IS_AUDIO_FILE_DETECT_HEAD_MAX`      or ``i_a_head_max``
    * :data:`~aeneas.globalconstants.PPN_TASK_IS_AUDIO_FILE_DETECT_HEAD_MIN`      or ``i_a_head_min``
    * :data:`~aeneas.globalconstants.PPN_TASK_IS_AUDIO_FILE_DETECT_TAIL_MAX`      or ``i_a_tail_max``
    * :data:`~aeneas.globalconstants.PPN_TASK_IS_AUDIO_FILE_DETECT_TAIL_MIN`      or ``i_a_tail_min``
    * :data:`~aeneas.globalconstants.PPN_TASK_IS_AUDIO_FILE_HEAD_LENGTH`          or ``i_a_head``
    * :data:`~aeneas.globalconstants.PPN_TASK_IS_AUDIO_FILE_PROCESS_LENGTH`       or ``i_a_process``
    * :data:`~aeneas.globalconstants.PPN_TASK_IS_AUDIO_FILE_TAIL_LENGTH`          or ``i_a_tail``
    * :data:`~aeneas.globalconstants.PPN_TASK_IS_TEXT_FILE_FORMAT`                or ``i_t_format``
    * :data:`~aeneas.globalconstants.PPN_TASK_IS_TEXT_FILE_IGNORE_REGEX`          or ``i_t_ignore_regex``
    * :data:`~aeneas.globalconstants.PPN_TASK_IS_TEXT_FILE_TRANSLITERATE_MAP`     or ``i_t_transliterate_map``
    * :data:`~aeneas.globalconstants.PPN_TASK_IS_TEXT_MPLAIN_WORD_SEPARATOR`      or ``i_t_mplain_word_separator``
    * :data:`~aeneas.globalconstants.PPN_TASK_IS_TEXT_MUNPARSED_L1_ID_REGEX`      or ``i_t_munparsed_l1_id_regex``
    * :data:`~aeneas.globalconstants.PPN_TASK_IS_TEXT_MUNPARSED_L2_ID_REGEX`      or ``i_t_munparsed_l2_id_regex``
    * :data:`~aeneas.globalconstants.PPN_TASK_IS_TEXT_MUNPARSED_L3_ID_REGEX`      or ``i_t_munparsed_l3_id_regex``
    * :data:`~aeneas.globalconstants.PPN_TASK_IS_TEXT_UNPARSED_CLASS_REGEX`       or ``i_t_unparsed_class_regex``
    * :data:`~aeneas.globalconstants.PPN_TASK_IS_TEXT_UNPARSED_ID_REGEX`          or ``i_t_unparsed_id_regex``
    * :data:`~aeneas.globalconstants.PPN_TASK_IS_TEXT_UNPARSED_ID_SORT`           or ``i_t_unparsed_id_sort``
    * :data:`~aeneas.globalconstants.PPN_TASK_OS_FILE_EAF_AUDIO_REF`              or ``o_eaf_audio_ref``
    * :data:`~aeneas.globalconstants.PPN_TASK_OS_FILE_FORMAT`                     or ``o_format``
    * :data:`~aeneas.globalconstants.PPN_TASK_OS_FILE_HEAD_TAIL_FORMAT`           or ``o_h_t_format``
    * :data:`~aeneas.globalconstants.PPN_TASK_OS_FILE_ID_REGEX`                   or ``o_id_regex``
    * :data:`~aeneas.globalconstants.PPN_TASK_OS_FILE_LEVELS`                     or ``o_levels``
    * :data:`~aeneas.globalconstants.PPN_TASK_OS_FILE_NAME`                       or ``o_name``
    * :data:`~aeneas.globalconstants.PPN_TASK_OS_FILE_SMIL_AUDIO_REF`             or ``o_smil_audio_ref``
    * :data:`~aeneas.globalconstants.PPN_TASK_OS_FILE_SMIL_PAGE_REF`              or ``o_smil_page_ref``

    :param string config_string: the configuration string
    :raises: TypeError: if ``config_string`` is not ``None`` and
                        it is not a Unicode string
    :raises: KeyError: if trying to access a key not listed above
    """

    FIELDS = (
        (gc.PPN_TASK_CUSTOM_ID, (None, None, ["custom_id"], "custom ID")),
        (gc.PPN_TASK_DESCRIPTION, (None, None, ["description"], "description")),
        (gc.PPN_TASK_LANGUAGE, (None, Language, ["language"], "language (REQ, *)")),
        (
            gc.PPN_TASK_ADJUST_BOUNDARY_AFTERCURRENT_VALUE,
            (
                None,
                TimeValue,
                ["aba_aftercurrent_value"],
                "offset value, in s (aftercurrent)",
            ),
        ),
        (
            gc.PPN_TASK_ADJUST_BOUNDARY_ALGORITHM,
            (None, None, ["aba_algorithm"], "algorithm to adjust sync map values (*)"),
        ),
        (
            gc.PPN_TASK_ADJUST_BOUNDARY_BEFORENEXT_VALUE,
            (
                None,
                TimeValue,
                ["aba_beforenext_value"],
                "offset value, in s (beforenext)",
            ),
        ),
        (
            gc.PPN_TASK_ADJUST_BOUNDARY_OFFSET_VALUE,
            (None, TimeValue, ["aba_offset_value"], "offset value, in s (offset)"),
        ),
        (
            gc.PPN_TASK_ADJUST_BOUNDARY_NO_ZERO,
            (
                None,
                bool,
                ["aba_no_zero"],
                "if True, do not allow zero-length fragments",
            ),
        ),
        (
            gc.PPN_TASK_ADJUST_BOUNDARY_PERCENT_VALUE,
            (None, int, ["aba_percent_value"], "percent value in [0..100] (percent)"),
        ),
        (
            gc.PPN_TASK_ADJUST_BOUNDARY_RATE_VALUE,
            (
                None,
                decimal.Decimal,
                ["aba_rate_value"],
                "max rate, in chars/s (rate, rateaggressive)",
            ),
        ),
        (
            gc.PPN_TASK_ADJUST_BOUNDARY_NONSPEECH_MIN,
            (
                None,
                TimeValue,
                ["aba_nonspeech_min"],
                "minimum long nonspeech duration, in s",
            ),
        ),
        (
            gc.PPN_TASK_ADJUST_BOUNDARY_NONSPEECH_STRING,
            (
                None,
                None,
                ["aba_nonspeech_string"],
                "replace long nonspeech with this string or specify REMOVE",
            ),
        ),
        (
            gc.PPN_TASK_IS_AUDIO_FILE_DETECT_HEAD_MAX,
            (
                None,
                TimeValue,
                ["i_a_head_max"],
                "detect audio head, at most this many seconds",
            ),
        ),
        (
            gc.PPN_TASK_IS_AUDIO_FILE_DETECT_HEAD_MIN,
            (
                None,
                TimeValue,
                ["i_a_head_min"],
                "detect audio head, at least this many seconds",
            ),
        ),
        (
            gc.PPN_TASK_IS_AUDIO_FILE_DETECT_TAIL_MAX,
            (
                None,
                TimeValue,
                ["i_a_tail_max"],
                "detect audio tail, at most this many seconds",
            ),
        ),
        (
            gc.PPN_TASK_IS_AUDIO_FILE_DETECT_TAIL_MIN,
            (
                None,
                TimeValue,
                ["i_a_tail_min"],
                "detect audio tail, at least this many seconds",
            ),
        ),
        (
            gc.PPN_TASK_IS_AUDIO_FILE_HEAD_LENGTH,
            (
                None,
                TimeValue,
                ["i_a_head"],
                "ignore this many seconds at begin of audio",
            ),
        ),
        (
            gc.PPN_TASK_IS_AUDIO_FILE_PROCESS_LENGTH,
            (None, TimeValue, ["i_a_process"], "process this many seconds of audio"),
        ),
        (
            gc.PPN_TASK_IS_AUDIO_FILE_TAIL_LENGTH,
            (None, TimeValue, ["i_a_tail"], "ignore this many seconds at end of audio"),
        ),
        (
            gc.PPN_TASK_IS_TEXT_FILE_FORMAT,
            (None, None, ["i_t_format"], "text format (REQ, *)"),
        ),
        (
            gc.PPN_TASK_IS_TEXT_FILE_IGNORE_REGEX,
            (
                None,
                None,
                ["i_t_ignore_regex"],
                "for the alignment, ignore text matched by regex",
            ),
        ),
        (
            gc.PPN_TASK_IS_TEXT_FILE_TRANSLITERATE_MAP,
            (
                None,
                None,
                ["i_t_transliterate_map"],
                "for the alignment, apply this transliteration map to text",
            ),
        ),
        (
            gc.PPN_TASK_IS_TEXT_MPLAIN_WORD_SEPARATOR,
            (None, None, ["i_t_mplain_word_separator"], "word separator (mplain)"),
        ),
        (
            gc.PPN_TASK_IS_TEXT_MUNPARSED_L1_ID_REGEX,
            (
                None,
                None,
                ["i_t_munparsed_l1_id_regex"],
                "regex matching level 1 id attributes (munparsed)",
            ),
        ),
        (
            gc.PPN_TASK_IS_TEXT_MUNPARSED_L2_ID_REGEX,
            (
                None,
                None,
                ["i_t_munparsed_l2_id_regex"],
                "regex matching level 2 id attributes (munparsed)",
            ),
        ),
        (
            gc.PPN_TASK_IS_TEXT_MUNPARSED_L3_ID_REGEX,
            (
                None,
                None,
                ["i_t_munparsed_l3_id_regex"],
                "regex matching level 3 id attributes (munparsed)",
            ),
        ),
        (
            gc.PPN_TASK_IS_TEXT_UNPARSED_CLASS_REGEX,
            (
                None,
                None,
                ["i_t_unparsed_class_regex"],
                "regex matching class attributes (unparsed, unparsed_img)",
            ),
        ),
        (
            gc.PPN_TASK_IS_TEXT_UNPARSED_ID_REGEX,
            (
                None,
                None,
                ["i_t_unparsed_id_regex"],
                "regex matching id attributes (unparsed, unparsed_img)",
            ),
        ),
        (
            gc.PPN_TASK_IS_TEXT_UNPARSED_ID_SORT,
            (
                None,
                None,
                ["i_t_unparsed_id_sort"],
                "algorithm to sort matched element (unparsed, unparsed_img) (*)",
            ),
        ),
        (
            gc.PPN_TASK_OS_FILE_EAF_AUDIO_REF,
            (None, None, ["o_eaf_audio_ref"], "audio ref value (eaf)"),
        ),
        (
            gc.PPN_TASK_OS_FILE_FORMAT,
            (None, None, ["o_format"], "sync map format (REQ, *)"),
        ),
        (
            gc.PPN_TASK_OS_FILE_HEAD_TAIL_FORMAT,
            (None, None, ["o_h_t_format"], "audio head/tail format (*)"),
        ),
        (
            gc.PPN_TASK_OS_FILE_ID_REGEX,
            (
                None,
                None,
                ["o_id_regex"],
                "regex to build sync map id's (subtitles, plain)",
            ),
        ),
        (
            gc.PPN_TASK_OS_FILE_LEVELS,
            (
                None,
                None,
                ["o_levels"],
                "output the specified levels only (mplain, munparserd)",
            ),
        ),
        (
            gc.PPN_TASK_OS_FILE_NAME,
            (None, None, ["o_name"], "sync map file name (ignored)"),
        ),
        (
            gc.PPN_TASK_OS_FILE_SMIL_AUDIO_REF,
            (None, None, ["o_smil_audio_ref"], "audio ref value (smil, smilh, smilm)"),
        ),
        (
            gc.PPN_TASK_OS_FILE_SMIL_PAGE_REF,
            (None, None, ["o_smil_page_ref"], "text ref value (smil, smilh, smilm)"),
        ),
    )

    def aba_parameters(self):
        """
        Return a dictionary representing the
        :class:`~aeneas.adjustboundaryalgorithm.AdjustBoundaryAlgorithm`
        parameters stored in this task configuration.

        Available keys:

        * ``algorithm``, tuple: (string, list)
        * ``nonspeech``, tuple: (TimeValue or None, string)
        * ``nozero``, bool

        :rtype: dict
        """
        ABA_MAP = {
            AdjustBoundaryAlgorithm.AFTERCURRENT: [
                self[gc.PPN_TASK_ADJUST_BOUNDARY_AFTERCURRENT_VALUE]
            ],
            AdjustBoundaryAlgorithm.AUTO: [],
            AdjustBoundaryAlgorithm.BEFORENEXT: [
                self[gc.PPN_TASK_ADJUST_BOUNDARY_BEFORENEXT_VALUE]
            ],
            AdjustBoundaryAlgorithm.OFFSET: [
                self[gc.PPN_TASK_ADJUST_BOUNDARY_OFFSET_VALUE]
            ],
            AdjustBoundaryAlgorithm.PERCENT: [
                self[gc.PPN_TASK_ADJUST_BOUNDARY_PERCENT_VALUE]
            ],
            AdjustBoundaryAlgorithm.RATE: [
                self[gc.PPN_TASK_ADJUST_BOUNDARY_RATE_VALUE]
            ],
            AdjustBoundaryAlgorithm.RATEAGGRESSIVE: [
                self[gc.PPN_TASK_ADJUST_BOUNDARY_RATE_VALUE]
            ],
        }
        aba_algorithm = (
            self[gc.PPN_TASK_ADJUST_BOUNDARY_ALGORITHM] or AdjustBoundaryAlgorithm.AUTO
        )
        ns_min = self[gc.PPN_TASK_ADJUST_BOUNDARY_NONSPEECH_MIN]
        ns_string = self[gc.PPN_TASK_ADJUST_BOUNDARY_NONSPEECH_STRING]
        nozero = self[gc.PPN_TASK_ADJUST_BOUNDARY_NO_ZERO] or False
        return {
            "algorithm": (aba_algorithm, ABA_MAP[aba_algorithm]),
            "nonspeech": (ns_min, ns_string),
            "nozero": nozero,
        }
