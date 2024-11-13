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

import unittest

from aeneas.exacttiming import TimeInterval
from aeneas.exacttiming import TimeValue
from aeneas.syncmap.fragment import SyncMapFragment
from aeneas.syncmap.fragmentlist import SyncMapFragmentList


class TestSyncMapFragmentList(unittest.TestCase):
    def test_time_interval_list_bad(self):
        params = [
            (None, None, TypeError),
            ("0.000", None, TypeError),
            (0.000, None, TypeError),
            (0.000, 5.000, TypeError),
            ("0.000", None, TypeError),
            ("0.000", "5.000", TypeError),
            (TimeValue("0.000"), None, TypeError),
            (TimeValue("-5.000"), TimeValue("5.000"), ValueError),
            (TimeValue("5.000"), TimeValue("0.000"), ValueError),
        ]
        for b, e, exc in params:
            with self.assertRaises(exc):
                SyncMapFragmentList(begin=b, end=e)

    def test_time_interval_list_good(self):
        params = [
            ("0.000", "0.000"),
            ("0.000", "5.000"),
            ("1.000", "5.000"),
            ("5.000", "5.000"),
        ]
        for b, e in params:
            if b is not None:
                b = TimeValue(b)
            if e is not None:
                e = TimeValue(e)
            SyncMapFragmentList(begin=b, end=e)

    def test_time_interval_list_add_bad_type(self):
        params = [
            None,
            (0.000, 5.000),
            (TimeValue("0.000"), TimeValue("5.000")),
            TimeInterval(begin=TimeValue("0.000"), end=TimeValue("5.000")),
        ]
        fragment_list = SyncMapFragmentList(
            begin=TimeValue("0.000"), end=TimeValue("10.000")
        )
        for p in params:
            with self.assertRaises(TypeError):
                fragment_list.add(p)

    def test_time_interval_list_add_bad_value(self):
        params = [
            ("5.000", "6.000", "1.000", "2.000"),
            ("5.000", "6.000", "1.000", "5.000"),
            ("5.000", "6.000", "5.000", "7.000"),
            ("5.000", "6.000", "5.500", "7.000"),
            ("5.000", "6.000", "6.000", "7.000"),
            ("5.000", "6.000", "7.000", "8.000"),
        ]
        for lb, le, b, e in params:
            i = TimeInterval(begin=TimeValue(b), end=TimeValue(e))
            s = SyncMapFragment(interval=i)
            fragment_list = SyncMapFragmentList(begin=TimeValue(lb), end=TimeValue(le))
            with self.assertRaises(ValueError):
                fragment_list.add(s)

    def test_time_interval_list_add_good(self):
        params = [
            ("5.000", "6.000", "5.000", "5.000"),
            ("5.000", "6.000", "5.000", "5.500"),
            ("5.000", "6.000", "5.000", "6.000"),
            ("5.000", "6.000", "5.500", "5.600"),
            ("5.000", "6.000", "6.000", "6.000"),
        ]
        for lb, le, b, e in params:
            i = TimeInterval(begin=TimeValue(b), end=TimeValue(e))
            s = SyncMapFragment(interval=i)
            fragment_list = SyncMapFragmentList(begin=TimeValue(lb), end=TimeValue(le))
            fragment_list.add(s)

    def test_time_interval_list_add_bad_sequence(self):
        params = [
            [
                ("1.000", "1.000"),
                ("0.500", "1.500"),
            ],
            [
                ("1.000", "2.000"),
                ("1.500", "1.750"),
            ],
            [
                ("1.000", "2.000"),
                ("1.500", "1.500"),
            ],
            [
                ("1.000", "2.000"),
                ("0.500", "1.500"),
            ],
            [
                ("1.000", "2.000"),
                ("1.500", "2.500"),
            ],
            [
                ("1.000", "2.000"),
                ("0.500", "2.500"),
            ],
        ]
        for seq in params:
            fragment_list = SyncMapFragmentList(
                begin=TimeValue("0.000"), end=TimeValue("10.000")
            )
            with self.assertRaises(ValueError):
                for b, e in seq:
                    i = TimeInterval(begin=TimeValue(b), end=TimeValue(e))
                    s = SyncMapFragment(interval=i)
                    fragment_list.add(s)

    def test_time_interval_list_add_not_sorted_bad_sequence(self):
        params = [
            [
                ("1.000", "1.000"),
                ("0.500", "1.500"),
            ],
            [
                ("1.000", "2.000"),
                ("1.500", "1.750"),
            ],
            [
                ("1.000", "2.000"),
                ("1.500", "1.500"),
            ],
            [
                ("1.000", "2.000"),
                ("0.500", "1.500"),
            ],
            [
                ("1.000", "2.000"),
                ("1.500", "2.500"),
            ],
            [
                ("1.000", "2.000"),
                ("0.500", "2.500"),
            ],
        ]
        for seq in params:
            fragment_list = SyncMapFragmentList(
                begin=TimeValue("0.000"), end=TimeValue("10.000")
            )
            for b, e in seq:
                i = TimeInterval(begin=TimeValue(b), end=TimeValue(e))
                s = SyncMapFragment(interval=i)
                fragment_list.add(s, sort=False)
            with self.assertRaises(ValueError):
                fragment_list.sort()

    def test_time_interval_list_add_sorted_bad(self):
        fragment_list = SyncMapFragmentList(
            begin=TimeValue("0.000"), end=TimeValue("10.000")
        )
        i = TimeInterval(begin=TimeValue("0.000"), end=TimeValue("0.000"))
        s = SyncMapFragment(interval=i)
        fragment_list.add(s, sort=False)
        i = TimeInterval(begin=TimeValue("1.000"), end=TimeValue("1.000"))
        s = SyncMapFragment(interval=i)
        fragment_list.add(s, sort=False)
        i = TimeInterval(begin=TimeValue("2.000"), end=TimeValue("2.000"))
        s = SyncMapFragment(interval=i)
        with self.assertRaises(ValueError):
            fragment_list.add(s, sort=True)

    def test_time_interval_list_add_sorted(self):
        params = [
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
        ]
        for ins, exp in params:
            fragment_list = SyncMapFragmentList(
                begin=TimeValue("0.000"), end=TimeValue("10.000")
            )
            for b, e in ins:
                i = TimeInterval(begin=TimeValue(b), end=TimeValue(e))
                s = SyncMapFragment(interval=i)
                fragment_list.add(s)
            for j, fragment in enumerate(fragment_list.fragments):
                b, e = exp[j]
                exp_i = TimeInterval(begin=TimeValue(b), end=TimeValue(e))
                exp_s = SyncMapFragment(interval=exp_i)
                self.assertTrue(fragment == exp_s)

    def test_time_interval_list_add_not_sorted(self):
        params = [
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
        ]
        for ins, exp in params:
            fragment_list = SyncMapFragmentList(
                begin=TimeValue("0.000"), end=TimeValue("10.000")
            )
            for b, e in ins:
                i = TimeInterval(begin=TimeValue(b), end=TimeValue(e))
                s = SyncMapFragment(interval=i)
                fragment_list.add(s, sort=False)
            fragment_list.sort()
            for j, fragment in enumerate(fragment_list.fragments):
                b, e = exp[j]
                exp_i = TimeInterval(begin=TimeValue(b), end=TimeValue(e))
                exp_s = SyncMapFragment(interval=exp_i)
                self.assertTrue(fragment == exp_s)

    def test_time_interval_list_clone(self):
        params = [
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
        ]
        for ins in params:
            fragment_list = SyncMapFragmentList(
                begin=TimeValue("0.000"), end=TimeValue("10.000")
            )
            for b, e in ins:
                i = TimeInterval(begin=TimeValue(b), end=TimeValue(e))
                s = SyncMapFragment(interval=i)
                fragment_list.add(s)
            c = fragment_list.clone()
            self.assertNotEqual(id(fragment_list), id(c))
            self.assertEqual(len(fragment_list), len(c))
            for j, fragment in enumerate(fragment_list.fragments):
                self.assertNotEqual(id(fragment_list[j]), id(c[j]))
                self.assertEqual(fragment_list[j], c[j])
                fragment.fragment_type = SyncMapFragment.NONSPEECH
                self.assertNotEqual(fragment_list[j].fragment_type, c[j].fragment_type)
                self.assertEqual(
                    fragment_list[j].fragment_type, SyncMapFragment.NONSPEECH
                )
                self.assertEqual(c[j].fragment_type, SyncMapFragment.REGULAR)

    def test_time_interval_list_has_zero_length_fragments(self):
        params = [
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
        ]
        for frags, exp, exp_inside in params:
            fragment_list = SyncMapFragmentList(
                begin=TimeValue("0.000"), end=TimeValue("10.000")
            )
            for b, e in frags:
                i = TimeInterval(begin=TimeValue(b), end=TimeValue(e))
                s = SyncMapFragment(interval=i)
                fragment_list.add(s)
            self.assertEqual(fragment_list.has_zero_length_fragments(), exp)
            self.assertEqual(
                fragment_list.has_zero_length_fragments(
                    min_index=1, max_index=len(fragment_list) - 1
                ),
                exp_inside,
            )

    def test_time_interval_list_has_adjacent_fragments_only(self):
        params = [
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
        ]
        for frags, exp, exp_inside in params:
            fragment_list = SyncMapFragmentList(
                begin=TimeValue("0.000"), end=TimeValue("10.000")
            )
            for b, e in frags:
                i = TimeInterval(begin=TimeValue(b), end=TimeValue(e))
                s = SyncMapFragment(interval=i)
                fragment_list.add(s)
            self.assertEqual(fragment_list.has_adjacent_fragments_only(), exp)
            self.assertEqual(
                fragment_list.has_adjacent_fragments_only(
                    min_index=1, max_index=len(fragment_list) - 1
                ),
                exp_inside,
            )

    def test_time_interval_list_offset(self):
        params = [
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
        ]
        for ins, off, exp in params:
            fragment_list = SyncMapFragmentList(
                begin=TimeValue("0.000"), end=TimeValue("10.000")
            )
            for b, e in ins:
                i = TimeInterval(begin=TimeValue(b), end=TimeValue(e))
                s = SyncMapFragment(interval=i)
                fragment_list.add(s)
            fragment_list.offset(TimeValue(off))
            for j, fragment in enumerate(fragment_list.fragments):
                b, e = exp[j]
                exp_i = TimeInterval(begin=TimeValue(b), end=TimeValue(e))
                exp_s = SyncMapFragment(interval=exp_i)
                self.assertTrue(fragment == exp_s)

    def test_time_interval_list_fix_zero_length_fragments(self):
        params = [
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
        ]
        for ins, exp in params:
            fragment_list = SyncMapFragmentList(
                begin=TimeValue("0.000"), end=TimeValue("10.000")
            )
            for b, e in ins:
                i = TimeInterval(begin=TimeValue(b), end=TimeValue(e))
                s = SyncMapFragment(interval=i)
                fragment_list.add(s)
            fragment_list.fix_zero_length_fragments()
            for j, fragment in enumerate(fragment_list.fragments):
                b, e = exp[j]
                exp_i = TimeInterval(begin=TimeValue(b), end=TimeValue(e))
                exp_s = SyncMapFragment(interval=exp_i)
                self.assertTrue(fragment == exp_s)

    def test_time_interval_list_fix_zero_length_fragments_middle(self):
        params = [
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
        ]
        for ins, exp in params:
            fragment_list = SyncMapFragmentList(
                begin=TimeValue("0.000"), end=TimeValue("10.000")
            )
            for b, e in ins:
                i = TimeInterval(begin=TimeValue(b), end=TimeValue(e))
                s = SyncMapFragment(interval=i)
                fragment_list.add(s)
            fragment_list.fix_zero_length_fragments(
                duration=TimeValue("0.001"),
                min_index=1,
                max_index=(len(fragment_list) - 1),
            )
            for j, fragment in enumerate(fragment_list.fragments):
                b, e = exp[j]
                exp_i = TimeInterval(begin=TimeValue(b), end=TimeValue(e))
                exp_s = SyncMapFragment(interval=exp_i)
                self.assertTrue(fragment == exp_s)
