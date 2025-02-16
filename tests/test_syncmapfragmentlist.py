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

import copy
import typing

from aeneas.exacttiming import TimeInterval, TimeValue
from aeneas.syncmap.fragment import FragmentType, SyncMapFragment
from aeneas.syncmap.fragmentlist import SyncMapFragmentList

from .common import BaseCase


class TestSyncMapFragmentList(BaseCase):
    def build_fragment_list_from_intervals(
        self,
        intervals: typing.Sequence[tuple[str, str]],
        *,
        begin: TimeValue = TimeValue("0.000"),
        end: TimeValue = TimeValue("10.000"),
        sort: bool = True,
    ) -> SyncMapFragmentList:
        fragment_list = SyncMapFragmentList(
            begin=begin,
            end=end,
        )
        for interval_begin, interval_end in intervals:
            interval = TimeInterval(
                begin=TimeValue(interval_begin), end=TimeValue(interval_end)
            )
            fragment = SyncMapFragment(interval=interval)
            fragment_list.add(fragment, sort=sort)
        return fragment_list

    def test_time_interval_list_bad(self):
        cases = (
            (None, None, TypeError),
            ("0.000", None, TypeError),
            (0.000, None, TypeError),
            (0.000, 5.000, TypeError),
            ("0.000", None, TypeError),
            ("0.000", "5.000", TypeError),
            (TimeValue("0.000"), None, TypeError),
            (TimeValue("-5.000"), TimeValue("5.000"), ValueError),
            (TimeValue("5.000"), TimeValue("0.000"), ValueError),
        )
        for begin, end, exc in cases:
            with self.subTest(being=begin, end=end, exc=exc), self.assertRaises(exc):
                SyncMapFragmentList(begin=begin, end=end)

    def test_time_interval_list_good(self):
        cases = (
            ("0.000", "0.000"),
            ("0.000", "5.000"),
            ("1.000", "5.000"),
            ("5.000", "5.000"),
        )
        for begin, end in cases:
            with self.subTest(begin=begin, end=end):
                SyncMapFragmentList(begin=TimeValue(begin), end=TimeValue(end))

    def test_time_interval_list_add_bad_type(self):
        cases = (
            None,
            (0.000, 5.000),
            (TimeValue("0.000"), TimeValue("5.000")),
            TimeInterval(begin=TimeValue("0.000"), end=TimeValue("5.000")),
        )
        fragment_list = SyncMapFragmentList(
            begin=TimeValue("0.000"), end=TimeValue("10.000")
        )
        for p in cases:
            with self.subTest(p=p), self.assertRaises(TypeError):
                fragment_list.add(p)

    def test_time_interval_list_add_bad_value(self):
        cases = (
            ("5.000", "6.000", "1.000", "2.000"),
            ("5.000", "6.000", "1.000", "5.000"),
            ("5.000", "6.000", "5.000", "7.000"),
            ("5.000", "6.000", "5.500", "7.000"),
            ("5.000", "6.000", "6.000", "7.000"),
            ("5.000", "6.000", "7.000", "8.000"),
        )
        for list_begin, list_end, begin, end in cases:
            with self.subTest(
                list_begin=list_begin, list_end=list_end, begin=begin, end=end
            ):
                interval = TimeInterval(begin=TimeValue(begin), end=TimeValue(end))
                fragment = SyncMapFragment(interval=interval)
                fragment_list = SyncMapFragmentList(
                    begin=TimeValue(list_begin), end=TimeValue(list_end)
                )
                with self.assertRaises(ValueError):
                    fragment_list.add(fragment)

    def test_time_interval_list_add_good(self):
        cases = (
            ("5.000", "6.000", "5.000", "5.000"),
            ("5.000", "6.000", "5.000", "5.500"),
            ("5.000", "6.000", "5.000", "6.000"),
            ("5.000", "6.000", "5.500", "5.600"),
            ("5.000", "6.000", "6.000", "6.000"),
        )
        for list_begin, list_end, begin, end in cases:
            with self.subTest(
                list_begin=list_begin, list_end=list_end, begin=begin, end=end
            ):
                self.build_fragment_list_from_intervals(
                    [(begin, end)], begin=TimeValue(list_begin), end=TimeValue(list_end)
                )

    def test_time_interval_list_add_bad_sequence(self):
        cases = (
            (
                ("1.000", "1.000"),
                ("0.500", "1.500"),
            ),
            (
                ("1.000", "2.000"),
                ("1.500", "1.750"),
            ),
            (
                ("1.000", "2.000"),
                ("1.500", "1.500"),
            ),
            (
                ("1.000", "2.000"),
                ("0.500", "1.500"),
            ),
            (
                ("1.000", "2.000"),
                ("1.500", "2.500"),
            ),
            (
                ("1.000", "2.000"),
                ("0.500", "2.500"),
            ),
        )
        for intervals in cases:
            with self.subTest(intervals=intervals):
                fragments = []
                for begin, end in intervals:
                    interval = TimeInterval(begin=TimeValue(begin), end=TimeValue(end))
                    fragments.append(SyncMapFragment(interval=interval))

                fragment_list = SyncMapFragmentList(
                    begin=TimeValue("0.000"), end=TimeValue("10.000")
                )
                with self.assertRaises(ValueError):
                    for fragment in fragments:
                        fragment_list.add(fragment)

    def test_time_interval_list_add_not_sorted_bad_sequence(self):
        cases = (
            (
                ("1.000", "1.000"),
                ("0.500", "1.500"),
            ),
            (
                ("1.000", "2.000"),
                ("1.500", "1.750"),
            ),
            (
                ("1.000", "2.000"),
                ("1.500", "1.500"),
            ),
            (
                ("1.000", "2.000"),
                ("0.500", "1.500"),
            ),
            (
                ("1.000", "2.000"),
                ("1.500", "2.500"),
            ),
            (
                ("1.000", "2.000"),
                ("0.500", "2.500"),
            ),
        )
        for intervals in cases:
            with self.subTest(intervals=intervals):
                fragment_list = self.build_fragment_list_from_intervals(
                    intervals, sort=False
                )

                with self.assertRaises(ValueError):
                    fragment_list.sort()

    def test_time_interval_list_add_sorted_bad(self):
        fragment_list = self.build_fragment_list_from_intervals(
            [("0.000", "0.000"), ("1.000", "1.000")], sort=False
        )

        interval = TimeInterval(begin=TimeValue("2.000"), end=TimeValue("2.000"))
        fragment = SyncMapFragment(interval=interval)
        with self.assertRaises(ValueError):
            fragment_list.add(fragment, sort=True)

    def test_time_interval_list_add_sorted(self):
        cases = (
            (
                [
                    ("1.000", "1.000"),
                    ("0.500", "0.500"),
                    ("1.000", "1.000"),
                ],
                [
                    ("0.500", "0.500"),
                    ("1.000", "1.000"),
                    ("1.000", "1.000"),
                ],
            ),
            (
                [
                    ("1.000", "1.000"),
                    ("0.500", "0.500"),
                ],
                [
                    ("0.500", "0.500"),
                    ("1.000", "1.000"),
                ],
            ),
            (
                [
                    ("2.000", "2.000"),
                    ("1.000", "2.000"),
                    ("0.500", "0.500"),
                ],
                [
                    ("0.500", "0.500"),
                    ("1.000", "2.000"),
                    ("2.000", "2.000"),
                ],
            ),
            (
                [
                    ("2.000", "2.000"),
                    ("0.500", "0.500"),
                    ("2.000", "3.000"),
                    ("1.000", "2.000"),
                    ("0.500", "0.500"),
                ],
                [
                    ("0.500", "0.500"),
                    ("0.500", "0.500"),
                    ("1.000", "2.000"),
                    ("2.000", "2.000"),
                    ("2.000", "3.000"),
                ],
            ),
        )
        for intervals, expected in cases:
            with self.subTest(intervals=intervals, expected=expected):
                fragment_list = self.build_fragment_list_from_intervals(intervals)

                for idx, fragment in enumerate(fragment_list.fragments):
                    begin, end = expected[idx]
                    expected_interval = TimeInterval(
                        begin=TimeValue(begin), end=TimeValue(end)
                    )
                    expected_fragment = SyncMapFragment(interval=expected_interval)
                    self.assertEqual(fragment, expected_fragment)

    def test_time_interval_list_add_not_sorted(self):
        cases = (
            (
                [
                    ("1.000", "1.000"),
                    ("0.500", "0.500"),
                    ("1.000", "1.000"),
                ],
                [
                    ("0.500", "0.500"),
                    ("1.000", "1.000"),
                    ("1.000", "1.000"),
                ],
            ),
            (
                [
                    ("1.000", "1.000"),
                    ("0.500", "0.500"),
                ],
                [
                    ("0.500", "0.500"),
                    ("1.000", "1.000"),
                ],
            ),
            (
                [
                    ("2.000", "2.000"),
                    ("1.000", "2.000"),
                    ("0.500", "0.500"),
                ],
                [
                    ("0.500", "0.500"),
                    ("1.000", "2.000"),
                    ("2.000", "2.000"),
                ],
            ),
            (
                [
                    ("2.000", "2.000"),
                    ("0.500", "0.500"),
                    ("2.000", "3.000"),
                    ("1.000", "2.000"),
                    ("0.500", "0.500"),
                ],
                [
                    ("0.500", "0.500"),
                    ("0.500", "0.500"),
                    ("1.000", "2.000"),
                    ("2.000", "2.000"),
                    ("2.000", "3.000"),
                ],
            ),
        )
        for intervals, expected in cases:
            with self.subTest(intervals=intervals, expected=expected):
                fragment_list = self.build_fragment_list_from_intervals(
                    intervals, sort=False
                )

                fragment_list.sort()

                for idx, fragment in enumerate(fragment_list.fragments):
                    begin, end = expected[idx]
                    expected_interval = TimeInterval(
                        begin=TimeValue(begin), end=TimeValue(end)
                    )
                    expected_fragment = SyncMapFragment(interval=expected_interval)
                    self.assertEqual(fragment, expected_fragment)

    def test_time_interval_list_clone(self):
        cases = (
            [
                ("1.000", "1.000"),
                ("0.500", "0.500"),
                ("1.000", "1.000"),
            ],
            [
                ("1.000", "1.000"),
                ("0.500", "0.500"),
            ],
            [
                ("2.000", "2.000"),
                ("1.000", "2.000"),
                ("0.500", "0.500"),
            ],
            [
                ("2.000", "2.000"),
                ("0.500", "0.500"),
                ("2.000", "3.000"),
                ("1.000", "2.000"),
                ("0.500", "0.500"),
            ],
        )
        for intervals in cases:
            with self.subTest(intervals=intervals):
                fragment_list = self.build_fragment_list_from_intervals(intervals)

                c = copy.deepcopy(fragment_list)

                self.assertNotEqual(id(fragment_list), id(c))
                self.assertEqual(len(fragment_list), len(c))
                for idx, fragment in enumerate(fragment_list.fragments):
                    self.assertNotEqual(id(fragment_list[idx]), id(c[idx]))
                    self.assertEqual(fragment_list[idx], c[idx])
                    fragment.fragment_type = FragmentType.NONSPEECH
                    self.assertNotEqual(
                        fragment_list[idx].fragment_type, c[idx].fragment_type
                    )
                    self.assertEqual(
                        fragment_list[idx].fragment_type, FragmentType.NONSPEECH
                    )
                    self.assertEqual(c[idx].fragment_type, FragmentType.REGULAR)

    def test_time_interval_list_has_zero_length_fragments(self):
        cases = (
            (
                [
                    ("0.000", "0.000"),
                    ("0.000", "0.000"),
                    ("0.000", "0.000"),
                ],
                True,
                True,
            ),
            (
                [
                    ("0.000", "1.000"),
                    ("1.000", "1.000"),
                    ("1.000", "1.000"),
                ],
                True,
                True,
            ),
            (
                [
                    ("0.000", "0.000"),
                    ("0.000", "0.000"),
                    ("0.000", "1.000"),
                ],
                True,
                True,
            ),
            (
                [
                    ("0.000", "0.000"),
                    ("0.000", "1.000"),
                    ("1.000", "1.000"),
                ],
                True,
                False,
            ),
            (
                [
                    ("0.000", "1.000"),
                    ("1.000", "2.000"),
                    ("2.000", "3.000"),
                ],
                False,
                False,
            ),
            (
                [
                    ("0.000", "0.000"),
                    ("0.000", "1.000"),
                    ("1.000", "1.000"),
                    ("1.000", "2.000"),
                    ("2.000", "2.000"),
                ],
                True,
                True,
            ),
            (
                [
                    ("0.000", "0.000"),
                    ("0.000", "1.000"),
                    ("1.000", "1.500"),
                    ("1.500", "2.000"),
                    ("2.000", "2.000"),
                ],
                True,
                False,
            ),
        )
        for intervals, expected, expected_inside in cases:
            with self.subTest(
                intervals=intervals, expected=expected, expected_inside=expected_inside
            ):
                fragment_list = self.build_fragment_list_from_intervals(intervals)

                self.assertEqual(fragment_list.has_zero_length_fragments(), expected)
                self.assertEqual(
                    fragment_list.has_zero_length_fragments(
                        min_index=1, max_index=len(fragment_list) - 1
                    ),
                    expected_inside,
                )

    def test_time_interval_list_has_adjacent_fragments_only(self):
        cases = (
            (
                [
                    ("0.000", "0.000"),
                    ("0.000", "0.000"),
                    ("0.000", "0.000"),
                ],
                True,
                True,
            ),
            (
                [
                    ("0.000", "1.000"),
                    ("1.000", "1.000"),
                    ("1.000", "1.000"),
                ],
                True,
                True,
            ),
            (
                [
                    ("0.000", "0.000"),
                    ("0.000", "0.000"),
                    ("0.000", "1.000"),
                ],
                True,
                True,
            ),
            (
                [
                    ("0.000", "0.000"),
                    ("0.000", "1.000"),
                    ("1.000", "1.000"),
                ],
                True,
                True,
            ),
            (
                [
                    ("0.000", "1.000"),
                    ("1.000", "2.000"),
                    ("2.000", "3.000"),
                ],
                True,
                True,
            ),
            (
                [
                    ("0.000", "0.000"),
                    ("0.000", "1.000"),
                    ("1.000", "1.000"),
                    ("1.000", "2.000"),
                    ("2.000", "2.000"),
                ],
                True,
                True,
            ),
            (
                [
                    ("0.000", "0.000"),
                    ("0.000", "1.000"),
                    ("1.000", "1.500"),
                    ("1.500", "2.000"),
                    ("2.000", "2.000"),
                ],
                True,
                True,
            ),
        )
        for intervals, expected, expected_inside in cases:
            with self.subTest(
                intervals=intervals, expected=expected, expected_inside=expected_inside
            ):
                fragment_list = self.build_fragment_list_from_intervals(intervals)

                self.assertEqual(fragment_list.has_adjacent_fragments_only(), expected)
                self.assertEqual(
                    fragment_list.has_adjacent_fragments_only(
                        min_index=1, max_index=len(fragment_list) - 1
                    ),
                    expected_inside,
                )

    def test_time_interval_list_offset(self):
        cases = (
            (
                [
                    ("0.500", "0.500"),
                    ("1.000", "1.000"),
                    ("1.000", "2.000"),
                ],
                "0.500",
                [
                    ("1.000", "1.000"),
                    ("1.500", "1.500"),
                    ("1.500", "2.500"),
                ],
            ),
            (
                [
                    ("0.500", "0.500"),
                    ("1.000", "1.000"),
                    ("1.000", "2.000"),
                ],
                "8.000",
                [
                    ("8.500", "8.500"),
                    ("9.000", "9.000"),
                    ("9.000", "10.000"),
                ],
            ),
            (
                [
                    ("0.500", "0.500"),
                    ("1.000", "1.000"),
                    ("1.000", "2.000"),
                ],
                "8.500",
                [
                    ("9.000", "9.000"),
                    ("9.500", "9.500"),
                    ("9.500", "10.000"),
                ],
            ),
            (
                [
                    ("0.500", "0.500"),
                    ("1.000", "1.000"),
                    ("1.000", "2.000"),
                ],
                "9.000",
                [
                    ("9.500", "9.500"),
                    ("10.000", "10.000"),
                    ("10.000", "10.000"),
                ],
            ),
            (
                [
                    ("0.500", "0.500"),
                    ("1.000", "1.000"),
                    ("1.000", "2.000"),
                ],
                "10.000",
                [
                    ("10.000", "10.000"),
                    ("10.000", "10.000"),
                    ("10.000", "10.000"),
                ],
            ),
            (
                [
                    ("0.500", "0.500"),
                    ("1.000", "1.000"),
                    ("1.000", "2.000"),
                ],
                "-0.500",
                [
                    ("0.000", "0.000"),
                    ("0.500", "0.500"),
                    ("0.500", "1.500"),
                ],
            ),
            (
                [
                    ("0.500", "0.500"),
                    ("1.000", "1.000"),
                    ("1.000", "2.000"),
                ],
                "-1.000",
                [
                    ("0.000", "0.000"),
                    ("0.000", "0.000"),
                    ("0.000", "1.000"),
                ],
            ),
            (
                [
                    ("0.500", "0.500"),
                    ("1.000", "1.000"),
                    ("1.000", "2.000"),
                ],
                "-1.500",
                [
                    ("0.000", "0.000"),
                    ("0.000", "0.000"),
                    ("0.000", "0.500"),
                ],
            ),
            (
                [
                    ("0.500", "0.500"),
                    ("1.000", "1.000"),
                    ("1.000", "2.000"),
                ],
                "-3.000",
                [
                    ("0.000", "0.000"),
                    ("0.000", "0.000"),
                    ("0.000", "0.000"),
                ],
            ),
        )
        for intervals, offset, expected in cases:
            with self.subTest(intervals=intervals, offset=offset, expected=expected):
                fragment_list = self.build_fragment_list_from_intervals(intervals)

                fragment_list.offset(TimeValue(offset))

                for idx, fragment in enumerate(fragment_list.fragments):
                    begin, end = expected[idx]
                    expected_interval = TimeInterval(
                        begin=TimeValue(begin), end=TimeValue(end)
                    )
                    expected_fragment = SyncMapFragment(interval=expected_interval)
                    self.assertEqual(fragment, expected_fragment)

    def test_time_interval_list_fix_zero_length_fragments(self):
        cases = (
            (
                [
                    ("0.000", "1.000"),
                    ("1.000", "1.000"),
                    ("1.000", "2.000"),
                ],
                [
                    ("0.000", "1.000"),
                    ("1.000", "1.001"),
                    ("1.001", "2.000"),
                ],
            ),
            (
                [
                    ("0.000", "1.000"),
                    ("1.000", "1.000"),
                    ("1.000", "1.000"),
                    ("1.000", "2.000"),
                ],
                [
                    ("0.000", "1.000"),
                    ("1.000", "1.001"),
                    ("1.001", "1.002"),
                    ("1.002", "2.000"),
                ],
            ),
            (
                [
                    ("0.000", "1.000"),
                    ("1.000", "1.000"),
                    ("1.000", "1.000"),
                    ("1.000", "1.000"),
                    ("1.000", "2.000"),
                ],
                [
                    ("0.000", "1.000"),
                    ("1.000", "1.001"),
                    ("1.001", "1.002"),
                    ("1.002", "1.003"),
                    ("1.003", "2.000"),
                ],
            ),
            (
                [
                    ("0.000", "1.000"),
                    ("1.000", "1.000"),
                    ("1.000", "1.000"),
                    ("1.000", "1.000"),
                    ("1.000", "2.000"),
                    ("2.000", "3.000"),
                    ("3.000", "4.000"),
                    ("4.000", "4.000"),
                    ("4.000", "5.000"),
                ],
                [
                    ("0.000", "1.000"),
                    ("1.000", "1.001"),
                    ("1.001", "1.002"),
                    ("1.002", "1.003"),
                    ("1.003", "2.000"),
                    ("2.000", "3.000"),
                    ("3.000", "4.000"),
                    ("4.000", "4.001"),
                    ("4.001", "5.000"),
                ],
            ),
            (
                [
                    ("0.000", "0.000"),
                    ("0.000", "1.000"),
                    ("1.000", "1.000"),
                    ("1.000", "1.000"),
                    ("1.000", "1.000"),
                    ("1.000", "2.000"),
                    ("2.000", "3.000"),
                    ("3.000", "4.000"),
                    ("4.000", "4.000"),
                    ("4.000", "5.000"),
                ],
                [
                    ("0.000", "0.001"),
                    ("0.001", "1.000"),
                    ("1.000", "1.001"),
                    ("1.001", "1.002"),
                    ("1.002", "1.003"),
                    ("1.003", "2.000"),
                    ("2.000", "3.000"),
                    ("3.000", "4.000"),
                    ("4.000", "4.001"),
                    ("4.001", "5.000"),
                ],
            ),
            (
                [
                    ("0.000", "1.000"),
                    ("1.000", "1.000"),
                    ("1.000", "1.000"),
                    ("1.000", "1.000"),
                    ("1.000", "1.002"),
                ],
                [
                    ("0.000", "1.000"),
                    ("1.000", "1.001"),
                    ("1.001", "1.002"),
                    ("1.002", "1.003"),
                    ("1.003", "1.005"),
                ],
            ),
            (
                [
                    ("0.000", "1.000"),
                    ("1.000", "1.000"),
                    ("1.000", "1.000"),
                    ("1.000", "1.000"),
                    ("1.000", "1.002"),
                    ("1.002", "2.000"),
                ],
                [
                    ("0.000", "1.000"),
                    ("1.000", "1.001"),
                    ("1.001", "1.002"),
                    ("1.002", "1.003"),
                    ("1.003", "1.005"),
                    ("1.005", "2.000"),
                ],
            ),
            (
                [
                    ("0.000", "1.000"),
                    ("1.000", "1.000"),
                    ("1.000", "1.000"),
                    ("1.000", "1.000"),
                    ("1.000", "1.002"),
                    ("1.002", "1.002"),
                    ("1.002", "2.000"),
                ],
                [
                    ("0.000", "1.000"),
                    ("1.000", "1.001"),
                    ("1.001", "1.002"),
                    ("1.002", "1.003"),
                    ("1.003", "1.005"),
                    ("1.005", "1.006"),
                    ("1.006", "2.000"),
                ],
            ),
        )
        for intervals, expected in cases:
            with self.subTest(intervals=intervals, expected=expected):
                fragment_list = self.build_fragment_list_from_intervals(intervals)

                fragment_list.fix_zero_length_fragments()

                for idx, fragment in enumerate(fragment_list.fragments):
                    begin, end = expected[idx]
                    expected_interval = TimeInterval(
                        begin=TimeValue(begin), end=TimeValue(end)
                    )
                    expected_fragment = SyncMapFragment(interval=expected_interval)
                    self.assertEqual(fragment, expected_fragment)

    def test_time_interval_list_fix_zero_length_fragments_middle(self):
        cases = (
            (
                [
                    ("0.000", "0.000"),
                    ("0.000", "1.000"),
                    ("1.000", "1.000"),
                    ("1.000", "2.000"),
                    ("2.000", "9.999"),
                ],
                [
                    ("0.000", "0.000"),
                    ("0.000", "1.000"),
                    ("1.000", "1.001"),
                    ("1.001", "2.000"),
                    ("2.000", "9.999"),
                ],
            ),
            (
                [
                    ("0.000", "0.000"),
                    ("0.000", "1.000"),
                    ("1.000", "1.000"),
                    ("1.000", "1.000"),
                    ("1.000", "2.000"),
                    ("2.000", "9.999"),
                ],
                [
                    ("0.000", "0.000"),
                    ("0.000", "1.000"),
                    ("1.000", "1.001"),
                    ("1.001", "1.002"),
                    ("1.002", "2.000"),
                    ("2.000", "9.999"),
                ],
            ),
            (
                [
                    ("0.000", "0.000"),
                    ("0.000", "1.000"),
                    ("1.000", "1.000"),
                    ("1.000", "1.000"),
                    ("1.000", "1.000"),
                    ("1.000", "2.000"),
                    ("2.000", "9.999"),
                ],
                [
                    ("0.000", "0.000"),
                    ("0.000", "1.000"),
                    ("1.000", "1.001"),
                    ("1.001", "1.002"),
                    ("1.002", "1.003"),
                    ("1.003", "2.000"),
                    ("2.000", "9.999"),
                ],
            ),
            (
                [
                    ("0.000", "0.000"),
                    ("0.000", "1.000"),
                    ("1.000", "1.000"),
                    ("1.000", "1.000"),
                    ("1.000", "1.000"),
                    ("1.000", "2.000"),
                    ("2.000", "3.000"),
                    ("3.000", "4.000"),
                    ("4.000", "4.000"),
                    ("4.000", "5.000"),
                    ("5.000", "9.999"),
                ],
                [
                    ("0.000", "0.000"),
                    ("0.000", "1.000"),
                    ("1.000", "1.001"),
                    ("1.001", "1.002"),
                    ("1.002", "1.003"),
                    ("1.003", "2.000"),
                    ("2.000", "3.000"),
                    ("3.000", "4.000"),
                    ("4.000", "4.001"),
                    ("4.001", "5.000"),
                    ("5.000", "9.999"),
                ],
            ),
            (
                [
                    ("0.000", "0.000"),
                    ("0.000", "0.000"),
                    ("0.000", "1.000"),
                    ("1.000", "1.000"),
                    ("1.000", "1.000"),
                    ("1.000", "1.000"),
                    ("1.000", "2.000"),
                    ("2.000", "3.000"),
                    ("3.000", "4.000"),
                    ("4.000", "4.000"),
                    ("4.000", "5.000"),
                    ("5.000", "9.999"),
                ],
                [
                    ("0.000", "0.000"),
                    ("0.000", "0.001"),
                    ("0.001", "1.000"),
                    ("1.000", "1.001"),
                    ("1.001", "1.002"),
                    ("1.002", "1.003"),
                    ("1.003", "2.000"),
                    ("2.000", "3.000"),
                    ("3.000", "4.000"),
                    ("4.000", "4.001"),
                    ("4.001", "5.000"),
                    ("5.000", "9.999"),
                ],
            ),
            (
                [
                    ("0.000", "0.000"),
                    ("0.000", "1.000"),
                    ("1.000", "1.000"),
                    ("1.000", "1.000"),
                    ("1.000", "1.000"),
                    ("1.000", "1.002"),
                    ("1.002", "9.999"),
                ],
                [
                    ("0.000", "0.000"),
                    ("0.000", "1.000"),
                    ("1.000", "1.001"),
                    ("1.001", "1.002"),
                    ("1.002", "1.003"),
                    ("1.003", "1.005"),
                    ("1.005", "9.999"),
                ],
            ),
            (
                [
                    ("0.000", "0.000"),
                    ("0.000", "1.000"),
                    ("1.000", "1.000"),
                    ("1.000", "1.000"),
                    ("1.000", "1.000"),
                    ("1.000", "1.002"),
                    ("1.002", "2.000"),
                    ("2.000", "9.999"),
                ],
                [
                    ("0.000", "0.000"),
                    ("0.000", "1.000"),
                    ("1.000", "1.001"),
                    ("1.001", "1.002"),
                    ("1.002", "1.003"),
                    ("1.003", "1.005"),
                    ("1.005", "2.000"),
                    ("2.000", "9.999"),
                ],
            ),
            (
                [
                    ("0.000", "0.000"),
                    ("0.000", "1.000"),
                    ("1.000", "1.000"),
                    ("1.000", "1.000"),
                    ("1.000", "1.000"),
                    ("1.000", "1.002"),
                    ("1.002", "1.002"),
                    ("1.002", "2.000"),
                    ("2.000", "9.999"),
                ],
                [
                    ("0.000", "0.000"),
                    ("0.000", "1.000"),
                    ("1.000", "1.001"),
                    ("1.001", "1.002"),
                    ("1.002", "1.003"),
                    ("1.003", "1.005"),
                    ("1.005", "1.006"),
                    ("1.006", "2.000"),
                    ("2.000", "9.999"),
                ],
            ),
        )
        for intervals, expected in cases:
            with self.subTest(intervals=intervals, expected=expected):
                fragment_list = self.build_fragment_list_from_intervals(intervals)

                fragment_list.fix_zero_length_fragments(
                    duration=TimeValue("0.001"),
                    min_index=1,
                    max_index=(len(fragment_list) - 1),
                )

                for idx, fragment in enumerate(fragment_list.fragments):
                    begin, end = expected[idx]
                    expected_interval = TimeInterval(
                        begin=TimeValue(begin), end=TimeValue(end)
                    )
                    expected_fragment = SyncMapFragment(interval=expected_interval)
                    self.assertEqual(fragment, expected_fragment)
