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

* :class:`~aeneas.adjustboundaryalgorithm.AdjustBoundaryAlgorithm`
  implementing functions to adjust
  the boundary point between two consecutive fragments.

.. warning:: This module is likely to be refactored in a future version
"""

import decimal
import logging

from aeneas.audiofilemfcc import AudioFileMFCC
from aeneas.exacttiming import TimeValue
from aeneas.logger import Configurable
from aeneas.runtimeconfiguration import RuntimeConfiguration
from aeneas.syncmap.fragment import SyncMapFragment, FragmentType
from aeneas.syncmap.fragmentlist import SyncMapFragmentList
from aeneas.textfile import TextFile, TextFragment
from aeneas.tree import Tree
import aeneas.globalconstants as gc

logger = logging.getLogger(__name__)


class AdjustBoundaryAlgorithm(Configurable):
    """
    Enumeration and implementation of the available algorithms
    to adjust the boundary point between two consecutive fragments.

    :param rconf: a runtime configuration
    :type  rconf: :class:`~aeneas.runtimeconfiguration.RuntimeConfiguration`
    :raises: TypeError: if one of ``boundary_indices``, ``real_wave_mfcc``,
                        or ``text_file`` is ``None`` or it has a wrong type
    """

    AFTERCURRENT = "aftercurrent"
    """
    Set the boundary at ``value`` seconds
    after the end of the current fragment,
    if the current boundary falls inside
    a nonspeech interval.
    If not, no adjustment is made.

    Example (value ``0.200`` seconds):

    .. image:: _static/aftercurrent.200.png
       :scale: 100%
       :align: center
       :alt: Comparison between AUTO labels and AFTERCURRENT labels with 0.200 seconds offset
    """

    AUTO = "auto"
    """
    Auto (no adjustment).

    Example:

    .. image:: _static/auto.png
       :scale: 100%
       :align: center
       :alt: The AUTO method does not change the time intervals
    """

    BEFORENEXT = "beforenext"
    """
    Set the boundary at ``value`` seconds
    before the beginning of the next fragment,
    if the current boundary falls inside
    a nonspeech interval.
    If not, no adjustment is made.

    Example (value ``0.200`` seconds):

    .. image:: _static/beforenext.200.png
       :scale: 100%
       :align: center
       :alt: Comparison between AUTO labels and BEFORENEXT labels with 0.200 seconds offset
    """

    OFFSET = "offset"
    """
    Offset the current boundaries by ``value`` seconds.
    The ``value`` can be negative or positive.

    Example (value ``-0.200`` seconds):

    .. image:: _static/offset.m200.png
       :scale: 100%
       :align: center
       :alt: Comparison between AUTO labels and OFFSET labels with value -0.200

    Example (value ``0.200`` seconds):

    .. image:: _static/offset.200.png
       :scale: 100%
       :align: center
       :alt: Comparison between AUTO labels and OFFSET labels with value 0.200

    .. versionadded:: 1.1.0
    """

    PERCENT = "percent"
    """
    Set the boundary at ``value`` percent of
    the nonspeech interval between the current and the next fragment,
    if the current boundary falls inside
    a nonspeech interval.
    The ``value`` must be an integer in ``[0, 100]``.
    If not, no adjustment is made.

    Example (value ``25`` %):

    .. image:: _static/percent.25.png
       :scale: 100%
       :align: center
       :alt: Comparison between AUTO labels and PERCENT labels with value 25 %

    Example (value ``50`` %):

    .. image:: _static/percent.50.png
       :scale: 100%
       :align: center
       :alt: Comparison between AUTO labels and PERCENT labels with value 50 %

    Example (value ``75`` %):

    .. image:: _static/percent.75.png
       :scale: 100%
       :align: center
       :alt: Comparison between AUTO labels and PERCENT labels with value 75 %

    """

    RATE = "rate"
    """
    Adjust boundaries trying to respect the
    ``value`` characters/second constraint.
    The ``value`` must be positive.
    First, the rates of all fragments are computed,
    using the current boundaries.
    For those fragments exceeding ``value`` characters/second,
    the algorithm will try to move the end boundary forward,
    so that its time interval increases (and hence its rate decreases).
    Clearly, it is possible that not all fragments
    can be adjusted this way: for example,
    if you have three consecutive fragments exceeding ``value``,
    the middle one cannot be stretched.

    Example (value ``13.0``, note how ``f000003`` is modified):

    .. image:: _static/rate.13.png
       :scale: 100%
       :align: center
       :alt: Comparison between AUTO labels and RATE labels with value 13.0

    """

    RATEAGGRESSIVE = "rateaggressive"
    """
    Adjust boundaries trying to respect the
    ``value`` characters/second constraint, in aggressive mode.
    The ``value`` must be positive.
    First, the rates of all fragments are computed,
    using the current boundaries.
    For those fragments exceeding ``value`` characters/second,
    the algorithm will try to move the end boundary forward,
    so that its time interval increases (and hence its rate decreases).
    If moving the end boundary is not possible,
    or it is not enough to keep the rate below ``value``,
    the algorithm will try to move the begin boundary back;
    this is the difference with the less aggressive
    :data:`~aeneas.adjustboundaryalgorithm.AdjustBoundaryAlgorithm.RATE`
    algorithm.
    Clearly, it is possible that not all fragments
    can be adjusted this way: for example,
    if you have three consecutive fragments exceeding ``value``,
    the middle one cannot be stretched.

    Example (value ``13.0``, note how ``f000003`` is modified):

    .. image:: _static/rateaggressive.13.png
       :scale: 100%
       :align: center
       :alt: Comparison between AUTO labels and RATEAGGRESSIVE labels with value 13.0

    .. versionadded:: 1.1.0
    """

    ALLOWED_VALUES = (
        AFTERCURRENT,
        AUTO,
        BEFORENEXT,
        OFFSET,
        PERCENT,
        RATE,
        RATEAGGRESSIVE,
    )
    """ List of all the allowed values """

    def __init__(self, rconf=None):
        super().__init__(rconf=rconf)
        self.smflist = None
        self.mws = self.rconf.mws

    def adjust(
        self,
        aba_parameters,
        boundary_indices,
        real_wave_mfcc: AudioFileMFCC,
        text_file: TextFile,
        allow_arbitrary_shift: bool = False,
    ) -> list[SyncMapFragmentList]:
        """
        Adjust the boundaries of the text map
        using the algorithm and parameters
        specified in the constructor,
        storing the sync map fragment list internally.

        :param dict aba_parameters: a dictionary containing the algorithm and its parameters,
                                    as produced by ``aba_parameters()`` in ``TaskConfiguration``
        :param boundary_indices: the current boundary indices,
                                 with respect to the audio file full MFCCs
        :type  boundary_indices: :class:`numpy.ndarray` (1D)
        :param real_wave_mfcc: the audio file MFCCs
        :type  real_wave_mfcc: :class:`~aeneas.audiofilemfcc.AudioFileMFCC`
        :param text_file: the text file containing the text fragments associated
        :type  text_file: :class:`~aeneas.textfile.TextFile`
        :param bool allow_arbitrary_shift: if ``True``, allow arbitrary shifts when adjusting zero length

        :rtype: list of :class:`~aeneas.syncmap.SyncMapFragmentList`
        """
        if boundary_indices is None:
            raise TypeError("`boundary_indices` is None")

        nozero = aba_parameters["nozero"]
        ns_min, ns_string = aba_parameters["nonspeech"]
        algorithm, algo_parameters = aba_parameters["algorithm"]

        logger.debug("  Converting boundary indices to fragment list...")
        begin = real_wave_mfcc.middle_begin * real_wave_mfcc.rconf.mws
        end = real_wave_mfcc.middle_end * real_wave_mfcc.rconf.mws
        time_values = [begin] + list(boundary_indices * self.mws) + [end]
        self.intervals_to_fragment_list(text_file=text_file, time_values=time_values)
        logger.debug("  Converting boundary indices to fragment list... done")

        logger.debug("  Processing fragments with zero length...")
        self._process_zero_length(nozero, allow_arbitrary_shift)
        logger.debug("  Processing fragments with zero length... done")

        logger.debug("  Processing nonspeech fragments...")
        self._process_long_nonspeech(ns_min, ns_string, real_wave_mfcc)
        logger.debug("  Processing nonspeech fragments... done")

        logger.debug("  Adjusting...")
        ALGORITHM_MAP = {
            self.AFTERCURRENT: self._adjust_aftercurrent,
            self.AUTO: self._adjust_auto,
            self.BEFORENEXT: self._adjust_beforenext,
            self.OFFSET: self._adjust_offset,
            self.PERCENT: self._adjust_percent,
            self.RATE: self._adjust_rate,
            self.RATEAGGRESSIVE: self._adjust_rate_aggressive,
        }
        ALGORITHM_MAP[algorithm](real_wave_mfcc, algo_parameters)
        logger.debug("  Adjusting... done")

        logger.debug("  Smoothing...")
        self._smooth_fragment_list(real_wave_mfcc.audio_length, ns_string)
        logger.debug("  Smoothing... done")

        return self.smflist

    def intervals_to_fragment_list(self, text_file: TextFile, time_values: list):
        """
        Transform a list of at least 4 time values
        (corresponding to at least 3 intervals)
        into a sync map fragment list and store it internally.
        The first interval is a HEAD, the last is a TAIL.

        For example:

            time_values=[0.000, 1.000, 2.000, 3.456] => [(0.000, 1.000), (1.000, 2.000), (2.000, 3.456)]

        :param text_file: the text file containing the text fragments associated
        :type  text_file: :class:`~aeneas.textfile.TextFile`
        :param time_values: the time values
        :type  time_values: list of :class:`~aeneas.exacttiming.TimeValue`
        :raises: TypeError: if ``text_file`` is not an instance of :class:`~aeneas.textfile.TextFile`
                            or ``time_values`` is not a list
        :raises: ValueError: if ``time_values`` has length less than four
        """
        if not isinstance(time_values, list):
            raise TypeError("time_values is not a list")
        if len(time_values) < 4:
            raise ValueError("time_values has length < 4")
        logger.debug("Converting time values to fragment list...")
        begin = time_values[0]
        end = time_values[-1]
        logger.debug(
            "  Creating SyncMapFragmentList with begin %.3f and end %.3f", begin, end
        )
        self.smflist = SyncMapFragmentList(begin=begin, end=end)
        logger.debug("  Creating HEAD fragment")
        self.smflist.add(
            SyncMapFragment.from_begin_end(
                begin=time_values[0],
                end=time_values[1],
                # NOTE lines and filtered lines MUST be set,
                #      otherwise some output format might break
                #      when adding HEAD/TAIL to output
                text_fragment=TextFragment(
                    identifier="HEAD", lines=[], filtered_lines=[]
                ),
                fragment_type=FragmentType.HEAD,
            ),
            sort=False,
        )
        logger.debug("  Creating REGULAR fragments")
        # NOTE text_file.fragments() returns a list,
        #      so we cache a copy here instead of
        #      calling it once per loop
        fragments = text_file.fragments
        for i in range(1, len(time_values) - 2):
            logger.debug("    Adding fragment %d ...", i)
            self.smflist.add(
                SyncMapFragment.from_begin_end(
                    begin=time_values[i],
                    end=time_values[i + 1],
                    text_fragment=fragments[i - 1],
                    fragment_type=FragmentType.REGULAR,
                ),
                sort=False,
            )
            logger.debug("    Adding fragment %d ... done", i)
        logger.debug("  Creating TAIL fragment")
        self.smflist.add(
            SyncMapFragment.from_begin_end(
                begin=time_values[len(time_values) - 2],
                end=end,
                # NOTE lines and filtered lines MUST be set,
                #      otherwise some output format might break
                #      when adding HEAD/TAIL to output
                text_fragment=TextFragment(
                    identifier="TAIL", lines=[], filtered_lines=[]
                ),
                fragment_type=FragmentType.TAIL,
            ),
            sort=False,
        )
        logger.debug("Converting time values to fragment list... done")
        logger.debug("Sorting fragment list...")
        self.smflist.sort()
        logger.debug("Sorting fragment list... done")
        return self.smflist

    def append_fragment_list_to_sync_root(self, sync_root: Tree):
        """
        Append the sync map fragment list
        to the given node from a sync map tree.

        :param sync_root: the root of the sync map tree to which the new nodes should be appended
        :type  sync_root: :class:`~aeneas.tree.Tree`
        """
        if not isinstance(sync_root, Tree):
            raise TypeError("sync_root is not a Tree object")

        logger.debug("Appending fragment list to sync root...")
        for fragment in self.smflist:
            sync_root.add_child(Tree(value=fragment))
        logger.debug("Appending fragment list to sync root... done")

    # #####################################################
    # NO ZERO AND LONG NONSPEECH FUNCTIONS
    # #####################################################

    def _process_zero_length(self, nozero, allow_arbitrary_shift):
        """
        If ``nozero`` is ``True``, modify the sync map fragment list
        so that no fragment will have zero length.
        """
        logger.debug("Called _process_zero_length")
        if not nozero:
            logger.debug("Processing zero length intervals not requested: returning")
            return
        logger.debug("Processing zero length intervals requested")
        logger.debug("  Checking and fixing...")
        duration = self.rconf[RuntimeConfiguration.ABA_NO_ZERO_DURATION]
        logger.debug("  Requested no zero duration: %.3f", duration)
        if not allow_arbitrary_shift:
            logger.debug("  No arbitrary shift => taking max with mws")
            duration = self.rconf.mws.geq_multiple(duration)
        logger.debug("  Actual no zero duration: %.3f", duration)
        # ignore HEAD and TAIL
        max_index = len(self.smflist) - 1
        self.smflist.fix_zero_length_fragments(
            duration=duration, min_index=1, max_index=max_index
        )
        logger.debug("  Checking and fixing... done")
        if self.smflist.has_zero_length_fragments(1, max_index):
            logger.warning("  The fragment list still has fragments with zero length")
        else:
            logger.debug("  The fragment list does not have fragments with zero length")

    def _process_long_nonspeech(self, ns_min, ns_string, real_wave_mfcc):
        logger.debug("Called _process_long_nonspeech")
        if ns_min is not None:
            logger.debug("Processing long nonspeech intervals requested")
            logger.debug("  Checking and fixing...")
            tolerance = self.rconf[RuntimeConfiguration.ABA_NONSPEECH_TOLERANCE]
            logger.debug("    Tolerance: %.3f", tolerance)
            long_nonspeech_intervals = [
                i
                for i in real_wave_mfcc.intervals(speech=False, time=True)
                if i.length >= ns_min
            ]
            pairs = self.smflist.fragments_ending_inside_nonspeech_intervals(
                long_nonspeech_intervals, tolerance
            )
            # ignore HEAD and TAIL
            min_index = 1
            max_index = len(self.smflist) - 1
            pairs = [(n, i) for (n, i) in pairs if (i >= min_index) and (i < max_index)]
            self.smflist.inject_long_nonspeech_fragments(pairs, ns_string)
            logger.debug("  Checking and fixing... done")
        else:
            logger.debug("Processing long nonspeech intervals not requested: returning")

    def _smooth_fragment_list(self, real_wave_mfcc_audio_length, ns_string):
        """
        Remove NONSPEECH fragments from list if needed,
        and set HEAD/TAIL begin/end.
        """
        logger.debug("Called _smooth_fragment_list")
        self.smflist[0].begin = TimeValue("0.000")
        self.smflist[-1].end = real_wave_mfcc_audio_length
        if ns_string in [None, gc.PPV_TASK_ADJUST_BOUNDARY_NONSPEECH_REMOVE]:
            logger.debug("Remove all NONSPEECH fragments")
            self.smflist.remove_nonspeech_fragments(zero_length_only=False)
        else:
            logger.debug("Remove NONSPEECH fragments with zero length only")
            self.smflist.remove_nonspeech_fragments(zero_length_only=True)

    # #####################################################
    # ADJUST FUNCTIONS
    # #####################################################

    def _adjust_auto(self, real_wave_mfcc, algo_parameters):
        """
        AUTO (do not modify)
        """
        logger.debug("Called _adjust_auto")
        logger.debug("Nothing to do, return unchanged")

    def _adjust_offset(self, real_wave_mfcc, algo_parameters):
        """
        OFFSET
        """
        logger.debug("Called _adjust_offset")
        self._apply_offset(offset=algo_parameters[0])

    def _adjust_percent(self, real_wave_mfcc, algo_parameters):
        """
        PERCENT
        """

        def new_time(nsi):
            """
            The new boundary time value is ``percent``
            of the nonspeech interval ``nsi``.
            """
            percent = decimal.Decimal(algo_parameters[0])
            return nsi.percent_value(percent)

        logger.debug("Called _adjust_percent")
        self._adjust_on_nonspeech(real_wave_mfcc, new_time)

    def _adjust_aftercurrent(self, real_wave_mfcc, algo_parameters):
        """
        AFTERCURRENT
        """

        def new_time(nsi):
            """
            The new boundary time value is ``delay`` after
            the begin of the nonspeech interval ``nsi``.
            If ``nsi`` has length less than ``delay``,
            set the new boundary time to the end of ``nsi``.
            """
            delay = max(algo_parameters[0], TimeValue("0.000"))
            return min(nsi.begin + delay, nsi.end)

        logger.debug("Called _adjust_aftercurrent")
        self._adjust_on_nonspeech(real_wave_mfcc, new_time)

    def _adjust_beforenext(self, real_wave_mfcc, algo_parameters):
        """
        BEFORENEXT
        """

        def new_time(nsi):
            """
            The new boundary time value is ``delay`` before
            the end of the nonspeech interval ``nsi``.
            If ``nsi`` has length less than ``delay``,
            set the new boundary time to the begin of ``nsi``.
            """
            delay = max(algo_parameters[0], TimeValue("0.000"))
            return max(nsi.end - delay, nsi.begin)

        logger.debug("Called _adjust_beforenext")
        self._adjust_on_nonspeech(real_wave_mfcc, new_time)

    def _adjust_rate(self, real_wave_mfcc, algo_parameters):
        """
        RATE
        """
        logger.debug("Called _adjust_rate")
        self._apply_rate(max_rate=algo_parameters[0], aggressive=False)

    def _adjust_rate_aggressive(self, real_wave_mfcc, algo_parameters):
        """
        RATEAGGRESSIVE
        """
        logger.debug("Called _adjust_rate_aggressive")
        self._apply_rate(max_rate=algo_parameters[0], aggressive=True)

    # #####################################################
    # HELPER FUNCTIONS
    # #####################################################

    def _apply_offset(self, offset: TimeValue):
        """
        Apply the given offset (negative, zero, or positive)
        to all time intervals.

        :param offset: the offset, in seconds
        :type  offset: :class:`~aeneas.exacttiming.TimeValue`
        """
        if not isinstance(offset, TimeValue):
            raise TypeError("offset is not an instance of TimeValue")
        logger.debug("Applying offset %s", offset)
        self.smflist.offset(offset)

    def _adjust_on_nonspeech(self, real_wave_mfcc, adjust_function):
        """
        Apply the adjust function to each boundary point
        falling inside (extrema included) of a nonspeech interval.

        The adjust function is not applied to a boundary index
        if there are two or more boundary indices falling
        inside the same nonspeech interval.

        The adjust function is not applied to the last boundary index
        to avoid anticipating the end of the audio file.

        The ``adjust function`` takes
        the nonspeech interval as its only argument.
        """
        logger.debug("Called _adjust_on_nonspeech")
        logger.debug("  Getting nonspeech intervals...")
        nonspeech_intervals = real_wave_mfcc.intervals(speech=False, time=True)
        logger.debug("  Getting nonspeech intervals... done")

        logger.debug(
            "  First pass: find pairs of adjacent fragments transitioning inside nonspeech"
        )
        tolerance = self.rconf[RuntimeConfiguration.ABA_NONSPEECH_TOLERANCE]
        logger.debug("    Tolerance: %.3f", tolerance)
        pairs = self.smflist.fragments_ending_inside_nonspeech_intervals(
            nonspeech_intervals, tolerance
        )
        logger.debug("  First pass: done")

        logger.debug("  Second pass: move end point of good pairs")
        for nsi, frag_index in pairs:
            new_value = adjust_function(nsi)
            logger.debug("    Current interval: %s", self.smflist[frag_index].interval)
            logger.debug("    New value:        %.3f", new_value)
            self.smflist.move_transition_point(frag_index, new_value)
            logger.debug("    New interval:     %s", self.smflist[frag_index].interval)
        logger.debug("  Second pass: done")

    def _apply_rate(self, max_rate, aggressive: bool = False):
        """
        Try to adjust the rate (characters/second)
        of the fragments of the list,
        so that it does not exceed the given ``max_rate``.

        This is done by testing whether some slack
        can be borrowed from the fragment before
        the faster current one.

        If ``aggressive`` is ``True``,
        the slack might be retrieved from the fragment after
        the faster current one,
        if the previous fragment could not contribute enough slack.
        """
        logger.debug(
            "Called _apply_rate(max_rate=%.3f, agressive=%s)", max_rate, aggressive
        )
        regular_fragments = list(self.smflist.regular_fragments)
        if len(regular_fragments) <= 1:
            logger.debug("  The list contains at most one regular fragment, returning")
            return

        faster_fragments = [
            (i, f)
            for i, f in regular_fragments
            if f.rate is not None and f.rate >= max_rate + decimal.Decimal("0.001")
        ]

        if not faster_fragments:
            logger.debug("  No regular fragment faster than max rate, returning")
            return

        logger.warning(
            "  Some fragments have rate faster than max rate: %s",
            [i for i, f in faster_fragments],
        )
        logger.debug("Fixing rate for faster fragments...")
        for frag_index, fragment in faster_fragments:
            self.smflist.fix_fragment_rate(frag_index, max_rate, aggressive=aggressive)
        logger.debug("Fixing rate for faster fragments... done")
        faster_fragments = [
            (i, f)
            for i, f in regular_fragments
            if (f.rate is not None) and (f.rate >= max_rate + decimal.Decimal("0.001"))
        ]
        if faster_fragments:
            logger.warning(
                "  Some fragments still have rate faster than max rate: %s",
                [i for i, f in faster_fragments],
            )
