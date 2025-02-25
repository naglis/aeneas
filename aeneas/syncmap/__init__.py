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
A synchronization map, or sync map,
is a map from text fragments to time intervals.

This package contains the following classes:

* :class:`~aeneas.syncmap.SyncMap`, represents a sync map as a tree of sync map fragments;
* :class:`~aeneas.syncmap.format.SyncMapFormat`, an enumeration of the supported output formats;
* :class:`~aeneas.syncmap.fragment.SyncMapFragment`, connects a text fragment with a ``begin`` and ``end`` time values;
* :class:`~aeneas.syncmap.fragmentlist.SyncMapFragmentList`, a list of sync map fragments with order constraints;
* :class:`~aeneas.syncmap.headtailformat.SyncMapHeadTailFormat`, an enumeration of the supported formats for the sync map head/tail.
* :class:`~aeneas.syncmap.missingparametererror.SyncMapMissingParameterError`, an error raised when reading sync maps from file;
"""

import copy
import itertools
import json
import logging
import os

from aeneas.syncmap.format import SyncMapFormat
from aeneas.syncmap.fragment import SyncMapFragment, FragmentType
from aeneas.syncmap.fragmentlist import SyncMapFragmentList
from aeneas.syncmap.headtailformat import SyncMapHeadTailFormat
from aeneas.tree import Tree
import aeneas.globalconstants as gc
import aeneas.globalfunctions as gf

logger = logging.getLogger(__name__)


class SyncMap:
    """
    A synchronization map, that is, a tree of
    :class:`~aeneas.syncmap.fragment.SyncMapFragment`
    objects.

    :param tree: the tree of fragments; if ``None``, an empty one will be created
    :type  tree: :class:`~aeneas.tree.Tree`
    """

    FINETUNEAS_REPLACEMENTS = [
        ["<!-- AENEAS_REPLACE_COMMENT_BEGIN -->", "<!-- AENEAS_REPLACE_COMMENT_BEGIN"],
        ["<!-- AENEAS_REPLACE_COMMENT_END -->", "AENEAS_REPLACE_COMMENT_END -->"],
        [
            "<!-- AENEAS_REPLACE_UNCOMMENT_BEGIN",
            "<!-- AENEAS_REPLACE_UNCOMMENT_BEGIN -->",
        ],
        ["AENEAS_REPLACE_UNCOMMENT_END -->", "<!-- AENEAS_REPLACE_UNCOMMENT_END -->"],
        ["// AENEAS_REPLACE_SHOW_ID", "showID = true;"],
        ["// AENEAS_REPLACE_ALIGN_TEXT", 'alignText = "left"'],
        ["// AENEAS_REPLACE_CONTINUOUS_PLAY", "continuousPlay = true;"],
        ["// AENEAS_REPLACE_TIME_FORMAT", "timeFormatHHMMSSmmm = true;"],
    ]
    FINETUNEAS_REPLACE_AUDIOFILEPATH = "// AENEAS_REPLACE_AUDIOFILEPATH"
    FINETUNEAS_REPLACE_FRAGMENTS = "// AENEAS_REPLACE_FRAGMENTS"
    FINETUNEAS_REPLACE_OUTPUT_FORMAT = "// AENEAS_REPLACE_OUTPUT_FORMAT"
    FINETUNEAS_REPLACE_SMIL_AUDIOREF = "// AENEAS_REPLACE_SMIL_AUDIOREF"
    FINETUNEAS_REPLACE_SMIL_PAGEREF = "// AENEAS_REPLACE_SMIL_PAGEREF"
    FINETUNEAS_REPLACE_SUGGESTED_FILENAME = "// AENEAS_REPLACE_SUGGESTED_FILENAME"
    FINETUNEAS_ALLOWED_FORMATS = [
        "csv",
        "json",
        "smil",
        "srt",
        "ssv",
        "ttml",
        "tsv",
        "txt",
        "vtt",
        "xml",
    ]
    FINETUNEAS_PATH = "../res/finetuneas.html"

    def __init__(self, tree: Tree | None = None):
        if tree is not None and not isinstance(tree, Tree):
            raise TypeError("tree is not an instance of Tree")
        if tree is None:
            tree = Tree()
        self.fragments_tree = tree

    def __len__(self) -> int:
        return len(self.fragments)

    def __str__(self):
        return "\n".join([f.__str__() for f in self.fragments])

    @property
    def fragments_tree(self) -> Tree:
        """
        Return the current tree of fragments.

        :rtype: :class:`~aeneas.tree.Tree`
        """
        return self.__fragments_tree

    @fragments_tree.setter
    def fragments_tree(self, fragments_tree: Tree):
        self.__fragments_tree = fragments_tree

    @property
    def is_single_level(self) -> bool:
        """
        Return ``True`` if the sync map
        has only one level, that is,
        if it is a list of fragments
        rather than a hierarchical tree.

        :rtype: bool
        """
        return self.fragments_tree.height <= 2

    @property
    def fragments(self) -> list[SyncMapFragment]:
        """
        The current list of sync map fragments
        which are (the values of) the children of the root node
        of the sync map tree.

        :rtype: list of :class:`~aeneas.syncmap.fragment.SyncMapFragment`
        """
        return self.fragments_tree.vchildren_not_empty

    def leaves(
        self, fragment_type: FragmentType | None = None
    ) -> list[SyncMapFragment]:
        """
        The current list of sync map fragments
        which are (the values of) the leaves
        of the sync map tree.

        :rtype: list of :class:`~aeneas.syncmap.fragment.SyncMapFragment`

        .. versionadded:: 1.7.0
        """
        leaves = self.fragments_tree.vleaves_not_empty
        if fragment_type is None:
            return leaves
        return [leaf for leaf in leaves if leaf.fragment_type == fragment_type]

    @property
    def has_adjacent_leaves_only(self) -> bool:
        """
        Return ``True`` if the sync map fragments
        which are the leaves of the sync map tree
        are all adjacent.

        :rtype: bool

        .. versionadded:: 1.7.0
        """
        for cur, nxt in itertools.pairwise(self.leaves()):
            if not cur.interval.is_adjacent_before(nxt.interval):
                return False
        return True

    @property
    def has_zero_length_leaves(self) -> bool:
        """
        Return ``True`` if there is at least one sync map fragment
        which has zero length
        among the leaves of the sync map tree.

        :rtype: bool

        .. versionadded:: 1.7.0
        """
        for leaf in self.leaves():
            if leaf.has_zero_length:
                return True
        return False

    @property
    def leaves_are_consistent(self) -> bool:
        """
        Return ``True`` if the sync map fragments
        which are the leaves of the sync map tree
        (except for HEAD and TAIL leaves)
        are all consistent, that is,
        their intervals do not overlap in forbidden ways.

        :rtype: bool

        .. versionadded:: 1.7.0
        """
        logger.debug("Checking if leaves are consistent")
        leaves = self.leaves()
        if not leaves:
            logger.debug("Empty leaves => return True")
            return True
        min_time = min(leaf.interval.begin for leaf in leaves)
        logger.debug("  Min time: %.3f", min_time)
        max_time = max(leaf.interval.end for leaf in leaves)
        logger.debug("  Max time: %.3f", max_time)
        logger.debug("  Creating SyncMapFragmentList...")
        smf = SyncMapFragmentList(begin=min_time, end=max_time)
        logger.debug("  Creating SyncMapFragmentList... done")
        logger.debug("  Sorting SyncMapFragmentList...")
        result = True
        not_head_tail = [leaf for leaf in leaves if not leaf.is_head_or_tail]
        for leaf in not_head_tail:
            smf.add(leaf, sort=False)
        try:
            smf.sort()
            logger.debug("  Sorting completed => return True")
        except ValueError:
            logger.debug("  Exception while sorting => return False")
            result = False
        logger.debug("  Sorting SyncMapFragmentList... done")
        return result

    @property
    def json_string(self) -> str:
        """
        Return a JSON representation of the sync map.

        :rtype: string

        .. versionadded:: 1.3.1
        """

        def visit_children(node):
            """Recursively visit the fragments_tree"""
            output_fragments = []
            for child in node.children_not_empty:
                fragment = child.value
                text = fragment.text_fragment
                output_fragments.append(
                    {
                        "id": text.identifier,
                        "language": text.language,
                        "lines": text.lines,
                        "begin": gf.time_to_ssmmm(fragment.begin),
                        "end": gf.time_to_ssmmm(fragment.end),
                        "children": visit_children(child),
                    }
                )
            return output_fragments

        output_fragments = visit_children(self.fragments_tree)
        return json.dumps({"fragments": output_fragments}, indent=1, sort_keys=True)

    def add_fragment(self, fragment: SyncMapFragment, *, as_last: bool = True):
        """
        Add the given sync map fragment,
        as the first or last child of the root node
        of the sync map tree.

        :param fragment: the sync map fragment to be added
        :type  fragment: :class:`~aeneas.syncmap.fragment.SyncMapFragment`
        :param bool as_last: if ``True``, append fragment; otherwise prepend it
        :raises: TypeError: if ``fragment`` is ``None`` or
                            it is not an instance of :class:`~aeneas.syncmap.fragment.SyncMapFragment`
        """
        if not isinstance(fragment, SyncMapFragment):
            raise TypeError("fragment is not an instance of SyncMapFragment")
        self.fragments_tree.add_child(Tree(value=fragment), as_last=as_last)

    def clear(self):
        """
        Clear the sync map, removing all the current fragments.
        """
        logger.debug("Clearing sync map")
        self.fragments_tree = Tree()

    def clone(self):
        """
        Return a deep copy of this sync map.

        .. versionadded:: 1.7.0

        :rtype: :class:`~aeneas.syncmap.SyncMap`
        """
        return copy.deepcopy(self)

    def output_html_for_tuning(
        self,
        audio_file_path: str,
        output_file_path: str,
        parameters: dict | None = None,
    ):
        """
        Output an HTML file for fine tuning the sync map manually.

        :param string audio_file_path: the path to the associated audio file
        :param string output_file_path: the path to the output file to write
        :param dict parameters: additional parameters

        .. versionadded:: 1.3.1
        """
        if parameters is None:
            parameters = {}

        audio_file_path_absolute = gf.fix_slash(os.path.abspath(audio_file_path))
        template_path_absolute = gf.absolute_path(self.FINETUNEAS_PATH, __file__)

        with open(template_path_absolute, encoding="utf-8") as file_obj:
            template = file_obj.read()

        # Remove the `.html` and the output format suffix (if any).
        basename = os.path.splitext(
            os.path.splitext(os.path.basename(output_file_path))[0]
        )[0]

        for search_string, replacement in (
            *self.FINETUNEAS_REPLACEMENTS,
            (
                self.FINETUNEAS_REPLACE_AUDIOFILEPATH,
                f'audioFilePath = "file://{audio_file_path_absolute}";',
            ),
            (
                self.FINETUNEAS_REPLACE_FRAGMENTS,
                f"fragments = ({self.json_string}).fragments;",
            ),
            (
                self.FINETUNEAS_REPLACE_SUGGESTED_FILENAME,
                f'suggestedFileName = "{basename}." + outputFormat;',
            ),
        ):
            template = template.replace(search_string, replacement)

        if gc.PPN_TASK_OS_FILE_FORMAT in parameters:
            output_format = parameters[gc.PPN_TASK_OS_FILE_FORMAT]
            if output_format in self.FINETUNEAS_ALLOWED_FORMATS:
                template = template.replace(
                    self.FINETUNEAS_REPLACE_OUTPUT_FORMAT,
                    f'outputFormat = "{output_format}";',
                )
                if output_format == "smil":
                    for key, placeholder, replacement in [
                        (
                            gc.PPN_TASK_OS_FILE_SMIL_AUDIO_REF,
                            self.FINETUNEAS_REPLACE_SMIL_AUDIOREF,
                            'audioref = "%s";',
                        ),
                        (
                            gc.PPN_TASK_OS_FILE_SMIL_PAGE_REF,
                            self.FINETUNEAS_REPLACE_SMIL_PAGEREF,
                            'pageref = "%s";',
                        ),
                    ]:
                        if key in parameters:
                            template = template.replace(
                                placeholder, replacement % parameters[key]
                            )

        with open(output_file_path, "w", encoding="utf-8") as file_obj:
            file_obj.write(template)

    def read(
        self,
        sync_map_format: str,
        input_file_path: str,
        parameters: dict | None = None,
    ):
        """
        Read sync map fragments from the given file in the specified format,
        and add them the current (this) sync map.

        Return ``True`` if the call succeeded,
        ``False`` if an error occurred.

        :param sync_map_format: the format of the sync map
        :type  sync_map_format: :class:`~aeneas.syncmap.SyncMapFormat`
        :param string input_file_path: the path to the input file to read
        :param dict parameters: additional parameters (e.g., for ``SMIL`` input)
        :raises: ValueError: if ``sync_map_format`` is ``None`` or it is not an allowed value
        :raises: OSError: if ``input_file_path`` does not exist
        """
        if sync_map_format is None:
            raise ValueError("Sync map format is None")
        if sync_map_format not in SyncMapFormat.CODE_TO_CLASS:
            raise ValueError(f"Sync map format {sync_map_format!r} is not allowed")

        logger.debug("Input format:     %r", sync_map_format)
        logger.debug("Input path:       %r", input_file_path)
        logger.debug("Input parameters: %r", parameters)

        reader = (SyncMapFormat.CODE_TO_CLASS[sync_map_format])(
            variant=sync_map_format,
            parameters=parameters,
        )

        # open file for reading
        logger.debug("Reading input file...")
        with open(input_file_path, encoding="utf-8") as input_file:
            input_text = input_file.read()
        reader.parse(input_text=input_text, syncmap=self)
        logger.debug("Reading input file... done")

        # overwrite language if requested
        language = gf.safe_get(parameters, gc.PPN_SYNCMAP_LANGUAGE, None)
        if language is not None:
            logger.debug("Overwriting language to %r", language)
            for fragment in self.fragments:
                if fragment.text_fragment is not None:
                    fragment.text_fragment.language = language

    def write(
        self,
        sync_map_format: str,
        output_file_path: str,
        parameters: dict | None = None,
    ):
        """
        Write the current sync map to file in the requested format.

        Return ``True`` if the call succeeded,
        ``False`` if an error occurred.

        :param sync_map_format: the format of the sync map
        :type  sync_map_format: :class:`~aeneas.syncmap.SyncMapFormat`
        :param string output_file_path: the path to the output file to write
        :param dict parameters: additional parameters (e.g., for ``SMIL`` output)
        :raises: ValueError: if ``sync_map_format`` is ``None`` or it is not an allowed value
        :raises: TypeError: if a required parameter is missing
        :raises: OSError: if ``output_file_path`` cannot be written
        """

        def select_levels(syncmap, levels):
            """
            Select the given levels of the fragments tree,
            modifying the given syncmap (always pass a copy of it!).
            """
            logger.debug("Levels: %r", levels)
            if levels is None:
                return
            try:
                levels = [int(level) for level in levels if int(level) > 0]
                syncmap.fragments_tree.keep_levels(levels)
                logger.debug("Selected levels: %s", levels)
            except ValueError:
                logger.warning(
                    "Cannot convert levels to list of int, returning unchanged"
                )

        def set_head_tail_format(syncmap, head_tail_format=None):
            """
            Set the appropriate head/tail nodes of the fragments tree,
            modifying the given syncmap (always pass a copy of it!).
            """
            logger.debug("Head/tail format: %r", head_tail_format)
            tree = syncmap.fragments_tree
            head = tree.get_child(0)
            first = tree.get_child(1)
            last = tree.get_child(-2)
            tail = tree.get_child(-1)
            # mark HEAD as REGULAR if needed
            if head_tail_format == SyncMapHeadTailFormat.ADD:
                head.value.fragment_type = FragmentType.REGULAR
                logger.debug("Marked HEAD as REGULAR")
            # stretch first and last fragment timings if needed
            if head_tail_format == SyncMapHeadTailFormat.STRETCH:
                logger.debug(
                    "Stretched first.begin: %.3f => %.3f (head)",
                    first.value.begin,
                    head.value.begin,
                )
                logger.debug(
                    "Stretched last.end:    %.3f => %.3f (tail)",
                    last.value.end,
                    tail.value.end,
                )
                first.value.begin = head.value.begin
                last.value.end = tail.value.end
            # mark TAIL as REGULAR if needed
            if head_tail_format == SyncMapHeadTailFormat.ADD:
                tail.value.fragment_type = FragmentType.REGULAR
                logger.debug("Marked TAIL as REGULAR")
            # remove all fragments that are not REGULAR
            for node in list(tree.dfs):
                if (node.value is not None) and (
                    node.value.fragment_type != FragmentType.REGULAR
                ):
                    node.remove()

        if sync_map_format is None:
            raise ValueError("Sync map format is None")
        if sync_map_format not in SyncMapFormat.CODE_TO_CLASS:
            raise ValueError(f"Sync map format {sync_map_format!r} is not allowed")

        logger.debug("Output format:     %r", sync_map_format)
        logger.debug("Output path:       %r", output_file_path)
        logger.debug("Output parameters: %r", parameters)

        # select levels and head/tail format
        pruned_syncmap = self.clone()
        try:
            select_levels(pruned_syncmap, parameters[gc.PPN_TASK_OS_FILE_LEVELS])
        except Exception:
            logger.warning("No %s parameter specified", gc.PPN_TASK_OS_FILE_LEVELS)
        try:
            set_head_tail_format(
                pruned_syncmap, parameters[gc.PPN_TASK_OS_FILE_HEAD_TAIL_FORMAT]
            )
        except Exception:
            logger.warning(
                "No %s parameter specified", gc.PPN_TASK_OS_FILE_HEAD_TAIL_FORMAT
            )

        # create writer
        # the constructor will check for required parameters, if any
        # if some are missing, it will raise a SyncMapMissingParameterError
        writer = (SyncMapFormat.CODE_TO_CLASS[sync_map_format])(
            variant=sync_map_format,
            parameters=parameters,
        )

        # create dir hierarchy, if needed
        gf.ensure_parent_directory(output_file_path)

        # open file for writing
        logger.debug("Writing output file...")
        with open(output_file_path, "w", encoding="utf-8") as output_file:
            output_file.write(writer.format(syncmap=pruned_syncmap))
        logger.debug("Writing output file... done")
