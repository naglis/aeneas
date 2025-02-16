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

* :class:`~aeneas.sd.SD`, for detecting the audio head and tail of a given audio file.

.. warning:: This module is likely to be refactored in a future version

.. versionadded:: 1.2.0
"""

import decimal
import logging
import tempfile

import numpy

from aeneas.audiofilemfcc import AudioFileMFCC
from aeneas.dtw import DTWAligner
from aeneas.exacttiming import TimeValue
from aeneas.logger import Configurable
from aeneas.runtimeconfiguration import RuntimeConfiguration
from aeneas.synthesizer import Synthesizer
from aeneas.textfile import TextFile

logger = logging.getLogger(__name__)


class SD(Configurable):
    """
    The SD ("start detector").

    Given an audio file and a text, detects the audio head and/or tail,
    using a voice activity detector (via :class:`~aeneas.vad.VAD`) and
    performing an alignment with a partial portion of the text
    (via :class:`~aeneas.dtw.DTWAligner`).

    This implementation relies on the following heuristic:

    1. synthesize text until
       ``max_head_length`` times :data:`aeneas.sd.SD.QUERY_FACTOR`
       seconds are reached;
    2. consider only the first
       ``max_head_length`` times :data:`aeneas.sd.SD.AUDIO_FACTOR`
       seconds of the audio file;
    3. compute the best partial alignment of 1. with 2., and return
       the corresponding time value.

    (Similarly for the audio tail.)

    :param real_wave_mfcc: the audio file
    :type  real_wave_mfcc: :class:`~aeneas.audiofile.AudioFileMFCC`
    :param text_file: the text file
    :type  text_file: :class:`~aeneas.textfile.TextFile`
    :param rconf: a runtime configuration
    :type  rconf: :class:`~aeneas.runtimeconfiguration.RuntimeConfiguration`
    """

    QUERY_FACTOR = decimal.Decimal("1.0")
    """
    Multiply the max head/tail length by this factor
    to get the minimum query length to be synthesized.
    Default: ``1.0``.

    .. versionadded:: 1.5.0
    """

    AUDIO_FACTOR = decimal.Decimal("2.5")
    """
    Multiply the max head/tail length by this factor
    to get the minimum length in the audio that will be searched
    for.
    Set it to be at least ``1.0 + QUERY_FACTOR * 1.5``.
    Default: ``2.5``.

    .. versionadded:: 1.5.0
    """

    MAX_LENGTH = TimeValue("10.000")
    """
    Try detecting audio head or tail up to this many seconds.
    Default: ``10.000``.

    .. versionadded:: 1.2.0
    """

    MIN_LENGTH = TimeValue("0.000")
    """
    Try detecting audio head or tail of at least this many seconds.
    Default: ``0.000``.

    .. versionadded:: 1.2.0
    """

    def __init__(
        self,
        real_wave_mfcc: AudioFileMFCC,
        text_file: TextFile,
        rconf=None,
    ):
        super().__init__(rconf=rconf)
        self.real_wave_mfcc = real_wave_mfcc
        self.text_file = text_file

    def detect_interval(
        self,
        min_head_length: TimeValue | None = None,
        max_head_length: TimeValue | None = None,
        min_tail_length: TimeValue | None = None,
        max_tail_length: TimeValue | None = None,
    ) -> tuple[TimeValue, TimeValue]:
        """
        Detect the interval of the audio file
        containing the fragments in the text file.

        Return the audio interval as a tuple of two
        :class:`~aeneas.exacttiming.TimeValue` objects,
        representing the begin and end time, in seconds,
        with respect to the full wave duration.

        If one of the parameters is ``None``, the default value
        (``0.0`` for min, ``10.0`` for max) will be used.

        :param min_head_length: estimated minimum head length
        :type  min_head_length: :class:`~aeneas.exacttiming.TimeValue`
        :param max_head_length: estimated maximum head length
        :type  max_head_length: :class:`~aeneas.exacttiming.TimeValue`
        :param min_tail_length: estimated minimum tail length
        :type  min_tail_length: :class:`~aeneas.exacttiming.TimeValue`
        :param max_tail_length: estimated maximum tail length
        :type  max_tail_length: :class:`~aeneas.exacttiming.TimeValue`
        :rtype: (:class:`~aeneas.exacttiming.TimeValue`, :class:`~aeneas.exacttiming.TimeValue`)
        :raises: TypeError: if one of the parameters is not ``None`` or a number
        :raises: ValueError: if one of the parameters is negative
        """
        head = self.detect_head(min_head_length, max_head_length)
        tail = self.detect_tail(min_tail_length, max_tail_length)
        begin = head
        end = self.real_wave_mfcc.audio_length - tail
        logger.debug("Audio length: %.3f", self.real_wave_mfcc.audio_length)
        logger.debug("Head length: %.3f", head)
        logger.debug("Tail length: %.3f", tail)
        logger.debug("Begin: %.3f", begin)
        logger.debug("End: %.3f", end)
        if (begin >= TimeValue("0.000")) and (end > begin):
            logger.debug("Returning %.3f %.3f", begin, end)
            return (begin, end)
        logger.debug("Returning (0.000, 0.000)")
        return (TimeValue("0.000"), TimeValue("0.000"))

    def detect_head(
        self,
        min_head_length: TimeValue | None = None,
        max_head_length: TimeValue | None = None,
    ) -> TimeValue:
        """
        Detect the audio head, returning its duration, in seconds.

        :param min_head_length: estimated minimum head length
        :type  min_head_length: :class:`~aeneas.exacttiming.TimeValue`
        :param max_head_length: estimated maximum head length
        :type  max_head_length: :class:`~aeneas.exacttiming.TimeValue`
        :rtype: :class:`~aeneas.exacttiming.TimeValue`
        :raises: TypeError: if one of the parameters is not ``None`` or a number
        :raises: ValueError: if one of the parameters is negative
        """
        return self._detect(min_head_length, max_head_length, tail=False)

    def detect_tail(
        self,
        min_tail_length: TimeValue | None = None,
        max_tail_length: TimeValue | None = None,
    ) -> TimeValue:
        """
        Detect the audio tail, returning its duration, in seconds.

        :param min_tail_length: estimated minimum tail length
        :type  min_tail_length: :class:`~aeneas.exacttiming.TimeValue`
        :param max_tail_length: estimated maximum tail length
        :type  max_tail_length: :class:`~aeneas.exacttiming.TimeValue`
        :rtype: :class:`~aeneas.exacttiming.TimeValue`
        :raises: TypeError: if one of the parameters is not ``None`` or a number
        :raises: ValueError: if one of the parameters is negative
        """
        return self._detect(min_tail_length, max_tail_length, tail=True)

    def _detect(
        self,
        min_length: TimeValue | None,
        max_length: TimeValue | None,
        tail: bool = False,
    ) -> TimeValue:
        """
        Detect the head or tail within ``min_length`` and ``max_length`` duration.

        If detecting the tail, the real wave MFCC and the query are reversed
        so that the tail detection problem reduces to a head detection problem.

        Return the duration of the head or tail, in seconds.

        :param min_length: estimated minimum length
        :type  min_length: :class:`~aeneas.exacttiming.TimeValue`
        :param max_length: estimated maximum length
        :type  max_length: :class:`~aeneas.exacttiming.TimeValue`
        :rtype: :class:`~aeneas.exacttiming.TimeValue`
        :raises: TypeError: if one of the parameters is not ``None`` or a number
        :raises: ValueError: if one of the parameters is negative
        """

        def _sanitize(
            value: TimeValue | None, default: TimeValue, name: str
        ) -> TimeValue:
            if value is None:
                value = default
            try:
                value = TimeValue(value)
            except (TypeError, ValueError, decimal.InvalidOperation) as exc:
                raise TypeError(f"The value of {name} is not a number") from exc
            if value < 0:
                raise ValueError(f"The value of {name} is negative")
            return value

        min_length = _sanitize(min_length, self.MIN_LENGTH, "min_length")
        max_length = _sanitize(max_length, self.MAX_LENGTH, "max_length")
        mws = self.rconf.mws
        min_length_frames = int(min_length / mws)
        max_length_frames = int(max_length / mws)
        logger.debug("MFCC window shift s: %.3f", mws)
        logger.debug("Min start length s: %.3f", min_length)
        logger.debug("Min start length frames: %d", min_length_frames)
        logger.debug("Max start length s: %.3f", max_length)
        logger.debug("Max start length frames: %d", max_length_frames)
        logger.debug("Tail?: %s", tail)

        logger.debug("Synthesizing query...")
        synt_duration = max_length * self.QUERY_FACTOR
        logger.debug("Synthesizing at least %.3f seconds", synt_duration)
        with tempfile.NamedTemporaryFile(
            suffix=".wav", dir=self.rconf[RuntimeConfiguration.TMP_PATH]
        ) as tmp_file:
            synt = Synthesizer.from_rconf(self.rconf)
            anchors, total_time, synthesized_chars = synt.synthesize(
                self.text_file, tmp_file.name, quit_after=synt_duration, backwards=tail
            )
            logger.debug("Synthesizing query... done")

            logger.debug("Extracting MFCCs for query...")
            query_mfcc = AudioFileMFCC(
                tmp_file.name,
                rconf=self.rconf,
            )
            logger.debug("Extracting MFCCs for query... done")

        search_window = max_length * self.AUDIO_FACTOR
        search_window_end = min(
            int(search_window / mws), self.real_wave_mfcc.all_length
        )
        logger.debug("Query MFCC length (frames): %d", query_mfcc.all_length)
        logger.debug("Real MFCC length (frames): %d", self.real_wave_mfcc.all_length)
        logger.debug("Search window end (s): %.3f", search_window)
        logger.debug("Search window end (frames): %d", search_window_end)

        if tail:
            logger.debug("Tail => reversing real_wave_mfcc and query_mfcc")
            self.real_wave_mfcc.reverse()
            query_mfcc.reverse()

        # NOTE: VAD will be run here, if not done before
        speech_intervals = self.real_wave_mfcc.intervals(speech=True)
        if len(speech_intervals) < 1:
            logger.debug("No speech intervals, hence no start found")
            if tail:
                self.real_wave_mfcc.reverse()
            return TimeValue("0.000")

        # generate a list of begin indices
        search_end = None
        candidates_begin = []
        for interval in speech_intervals:
            if interval[0] >= min_length_frames and interval[0] <= max_length_frames:
                candidates_begin.append(interval[0])
            search_end = interval[1]
            if search_end >= search_window_end:
                break

        # for each begin index, compute the acm cost
        # to match the query
        # note that we take the min over the last column of the acm
        # meaning that we allow to match the entire query wave
        # against a portion of the real wave
        candidates = []
        for candidate_begin in candidates_begin:
            logger.debug(
                "Candidate interval starting at %d == %.3f",
                candidate_begin,
                candidate_begin * mws,
            )
            try:
                rwm = AudioFileMFCC(
                    mfcc_matrix=self.real_wave_mfcc.all_mfcc[
                        :, candidate_begin:search_end
                    ],
                    rconf=self.rconf,
                )
                dtw = DTWAligner(
                    real_wave_mfcc=rwm,
                    synt_wave_mfcc=query_mfcc,
                    rconf=self.rconf,
                )
                acm = dtw.compute_accumulated_cost_matrix()
                last_column = acm[:, -1]
                min_value = numpy.min(last_column)
                min_index = numpy.argmin(last_column)
                logger.debug(
                    "Candidate interval: %d %d == %.3f %.3f",
                    candidate_begin,
                    search_end,
                    candidate_begin * mws,
                    search_end * mws,
                )
                logger.debug("Min value: %.6f", min_value)
                logger.debug("Min index: %d == %.3f", min_index, min_index * mws)
                candidates.append((min_value, candidate_begin, min_index))
            except Exception:
                logger.exception(
                    "An unexpected error occurred while running _detect",
                )

        # reverse again the real wave
        if tail:
            logger.debug("Tail => reversing real_wave_mfcc again")
            self.real_wave_mfcc.reverse()

        # return
        if len(candidates) < 1:
            logger.debug("No candidates found")
            return TimeValue("0.000")
        logger.debug("Candidates:")
        for candidate in candidates:
            logger.debug(
                "Value: %.6f Begin Time: %.3f Min Index: %d",
                candidate[0],
                candidate[1] * mws,
                candidate[2],
            )
        best = sorted(candidates)[0][1]
        logger.debug("Best candidate: %d == %.3f", best, best * mws)
        return best * mws
