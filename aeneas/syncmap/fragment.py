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

import decimal
import enum

from aeneas.exacttiming import TimeInterval, TimeValue
from aeneas.textfile import TextFragment


@enum.unique
class FragmentType(enum.IntEnum):
    REGULAR = 0
    """ Regular fragment """

    HEAD = 1
    """ Head fragment """

    TAIL = 2
    """ Tail fragment """

    NONSPEECH = 3
    """ Nonspeech fragment (not head nor tail) """


class SyncMapFragment:
    """
    A sync map fragment, that is,
    a text fragment and an associated time interval.

    :param text_fragment: the text fragment
    :type  text_fragment: :class:`~aeneas.textfile.TextFragment`
    :param begin: the begin time of the audio interval
    :type  begin: :class:`~aeneas.exacttiming.TimeValue`
    :param end: the end time of the audio interval
    :type  end: :class:`~aeneas.exacttiming.TimeValue`
    :param float confidence: the confidence of the audio timing
    """

    NOT_REGULAR_TYPES = [FragmentType.HEAD, FragmentType.TAIL, FragmentType.NONSPEECH]
    """ Types of fragment different than ``REGULAR`` """

    def __init__(
        self,
        interval: TimeInterval,
        *,
        text_fragment: TextFragment | None = None,
        fragment_type: FragmentType = FragmentType.REGULAR,
        confidence: float = 1.0,
    ):
        self.text_fragment = text_fragment
        self.interval = interval
        self.fragment_type = fragment_type
        self.confidence = confidence

    @classmethod
    def from_begin_end(
        cls,
        begin: TimeValue,
        end: TimeValue,
        *,
        text_fragment: TextFragment | None = None,
        fragment_type: FragmentType = FragmentType.REGULAR,
        confidence: float = 1.0,
    ) -> "SyncMapFragment":
        return cls(
            interval=TimeInterval(begin, end),
            text_fragment=text_fragment,
            fragment_type=fragment_type,
            confidence=confidence,
        )

    def __str__(self):
        return "%s %d %.3f %.3f" % (
            self.text_fragment.identifier,
            self.fragment_type,
            self.begin,
            self.end,
        )

    def __eq__(self, other):
        if not isinstance(other, SyncMapFragment):
            return False
        return self.interval == other.interval

    def __ne__(self, other):
        return not (self == other)

    def __gt__(self, other):
        if not isinstance(other, SyncMapFragment):
            return False
        return self.interval > other.interval

    def __lt__(self, other):
        if not isinstance(other, SyncMapFragment):
            return False
        return self.interval < other.interval

    def __ge__(self, other):
        return (self > other) or (self == other)

    def __le__(self, other):
        return (self < other) or (self == other)

    @property
    def text_fragment(self) -> TextFragment | None:
        """
        The text fragment associated with this sync map fragment.
        """
        return self.__text_fragment

    @text_fragment.setter
    def text_fragment(self, text_fragment: TextFragment | None):
        self.__text_fragment = text_fragment

    @property
    def interval(self) -> TimeInterval:
        """
        The time interval corresponding to this fragment.
        """
        return self.__interval

    @interval.setter
    def interval(self, interval: TimeInterval):
        self.__interval = interval

    @property
    def fragment_type(self) -> FragmentType:
        """
        The type of fragment.
        """
        return self.__fragment_type

    @fragment_type.setter
    def fragment_type(self, fragment_type: FragmentType):
        self.__fragment_type = fragment_type

    @property
    def is_head_or_tail(self) -> bool:
        """
        Return ``True`` if the fragment is HEAD or TAIL.

        .. versionadded:: 1.7.0
        """
        return self.fragment_type in (FragmentType.HEAD, FragmentType.TAIL)

    @property
    def is_regular(self) -> bool:
        """
        Return ``True`` if the fragment is REGULAR.

        .. versionadded:: 1.7.0
        """
        return self.fragment_type == FragmentType.REGULAR

    @property
    def confidence(self) -> float:
        """
        The confidence of the audio timing, from ``0.0`` to ``1.0``.

        Currently this value is not used, and it is always ``1.0``.
        """
        return self.__confidence

    @confidence.setter
    def confidence(self, confidence: float):
        self.__confidence = confidence

    @property
    def pretty_print(self) -> str:
        """
        Pretty print representation of this fragment,
        as ``(identifier, begin, end, text)``.

        .. versionadded:: 1.7.0
        """
        return "{}\t{:.3f}\t{:.3f}\t{}".format(
            self.identifier or "",
            self.interval.begin,
            self.interval.end,
            self.text or "",
        )

    @property
    def identifier(self) -> str | None:
        """
        The identifier of this sync map fragment.

        .. versionadded:: 1.7.0
        """
        if self.text_fragment is None:
            return None
        return self.text_fragment.identifier

    @property
    def text(self) -> str | None:
        """
        The text of this sync map fragment.

        .. versionadded:: 1.7.0
        """
        if self.text_fragment is None:
            return None
        return self.text_fragment.text

    @property
    def begin(self) -> TimeValue:
        """
        The begin time of this sync map fragment.
        """
        return self.interval.begin

    @begin.setter
    def begin(self, begin: TimeValue):
        if not isinstance(begin, TimeValue):
            raise TypeError("The given begin value is not an instance of TimeValue")
        self.interval.begin = begin

    @property
    def end(self) -> TimeValue:
        """
        The end time of this sync map fragment.
        """
        return self.interval.end

    @end.setter
    def end(self, end: TimeValue):
        if not isinstance(end, TimeValue):
            raise TypeError("The given end value is not an instance of TimeValue")
        self.interval.end = end

    @property
    def length(self) -> TimeValue:
        """
        The audio duration of this sync map fragment,
        as end time minus begin time.
        """
        return self.interval.length

    @property
    def has_zero_length(self) -> bool:
        """
        Returns ``True`` if this sync map fragment has zero length,
        that is, if its begin and end values coincide.

        :rtype: bool

        .. versionadded:: 1.7.0
        """
        return self.length == TimeValue("0.000")

    @property
    def chars(self) -> int:
        """
        Return the number of characters of the text fragment,
        not including the line separators.

        .. versionadded:: 1.2.0
        """
        if self.text_fragment is None:
            return 0
        return self.text_fragment.chars

    @property
    def rate(self) -> decimal.Decimal | None:
        """
        The rate, in characters/second, of this fragment.

        If the fragment is not ``REGULAR`` or its duration is zero,
        return ``None``.

        .. versionadded:: 1.2.0
        """
        if self.fragment_type != FragmentType.REGULAR or self.has_zero_length:
            return None
        return decimal.Decimal(self.chars / self.length)

    def rate_lack(self, max_rate: decimal.Decimal) -> TimeValue:
        """
        The time interval that this fragment lacks
        to respect the given max rate.

        A positive value means that the current fragment
        is faster than the max rate (bad).
        A negative or zero value means that the current fragment
        has rate slower or equal to the max rate (good).

        Always return ``0.000`` for fragments that are not ``REGULAR``.

        :param max_rate: the maximum rate (characters/second)
        :type  max_rate: :class:`~decimal.Decimal`

        .. versionadded:: 1.7.0
        """
        if self.fragment_type == FragmentType.REGULAR:
            return self.chars / max_rate - self.length
        return TimeValue("0.000")

    def rate_slack(self, max_rate: decimal.Decimal) -> TimeValue:
        """
        The maximum time interval that can be stolen to this fragment
        while keeping it respecting the given max rate.

        For ``REGULAR`` fragments this value is
        the opposite of the ``rate_lack``.
        For ``NONSPEECH`` fragments this value is equal to
        the length of the fragment.
        For ``HEAD`` and ``TAIL`` fragments this value is ``0.000``,
        meaning that they cannot be stolen.

        :param max_rate: the maximum rate (characters/second)
        :type  max_rate: :class:`~decimal.Decimal`
        :rtype: :class:`~aeneas.exacttiming.TimeValue`

        .. versionadded:: 1.7.0
        """
        if self.fragment_type == FragmentType.REGULAR:
            return -self.rate_lack(max_rate)
        elif self.fragment_type == FragmentType.NONSPEECH:
            return self.length
        else:
            return TimeValue("0.000")
