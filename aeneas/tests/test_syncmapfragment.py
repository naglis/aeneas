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
import unittest

from aeneas.exacttiming import TimeInterval, TimeValue
from aeneas.syncmap.fragment import FragmentType, SyncMapFragment
from aeneas.textfile import TextFragment


class TestSyncMap(unittest.TestCase):
    EMPTY_INTERVAL = TimeInterval(begin=TimeValue("0.000"), end=TimeValue("0.000"))

    def test_fragment_constructor(self):
        frag = SyncMapFragment(interval=self.EMPTY_INTERVAL)
        self.assertEqual(frag.length, 0)
        self.assertEqual(frag.chars, 0)
        self.assertIsNone(frag.rate)

    def test_fragment_constructor_begin_end(self):
        frag = SyncMapFragment.from_begin_end(
            begin=TimeValue("1.000"), end=TimeValue("1.000")
        )
        self.assertEqual(frag.length, 0)
        self.assertEqual(frag.chars, 0)
        self.assertIsNone(frag.rate)

    def test_fragment_constructor_begin_end_nonzero(self):
        frag = SyncMapFragment.from_begin_end(
            begin=TimeValue("1.000"), end=TimeValue("3.000")
        )
        self.assertEqual(frag.length, TimeValue("2.000"))
        self.assertEqual(frag.chars, 0)
        self.assertEqual(frag.rate, 0)

    def test_fragment_constructor_interval(self):
        interval = TimeInterval(begin=TimeValue("1.000"), end=TimeValue("1.000"))
        frag = SyncMapFragment(interval=interval)
        self.assertEqual(frag.length, 0)
        self.assertEqual(frag.chars, 0)
        self.assertIsNone(frag.rate)

    def test_fragment_constructor_interval_nonzero(self):
        interval = TimeInterval(begin=TimeValue("1.000"), end=TimeValue("3.000"))
        frag = SyncMapFragment(interval=interval)
        self.assertEqual(frag.length, TimeValue("2.000"))
        self.assertEqual(frag.chars, 0)
        self.assertEqual(frag.rate, 0)

    def test_fragment_pretty_print_empty(self):
        frag = SyncMapFragment(interval=self.EMPTY_INTERVAL)
        self.assertEqual(frag.pretty_print, "\t0.000\t0.000\t")

    def test_fragment_pretty_print_empty_text(self):
        interval = TimeInterval(begin=TimeValue("1.000"), end=TimeValue("3.000"))
        frag = SyncMapFragment(interval=interval)
        self.assertEqual(frag.pretty_print, "\t1.000\t3.000\t")

    def test_fragment_pretty_print_empty_interval(self):
        text = TextFragment(lines=["Hello", "World"])
        frag = SyncMapFragment(interval=self.EMPTY_INTERVAL, text_fragment=text)
        self.assertEqual(frag.pretty_print, "\t0.000\t0.000\tHello World")

    def test_fragment_pretty_print(self):
        interval = TimeInterval(begin=TimeValue("1.000"), end=TimeValue("3.000"))
        text = TextFragment(identifier="f001", lines=["Hello", "World"])
        frag = SyncMapFragment(text_fragment=text, interval=interval)
        self.assertEqual(frag.pretty_print, "f001\t1.000\t3.000\tHello World")

    def test_fragment_identifier_empty(self):
        frag = SyncMapFragment(interval=self.EMPTY_INTERVAL)
        self.assertIsNone(frag.identifier)

    def test_fragment_identifier_empty_bis(self):
        text = TextFragment()
        frag = SyncMapFragment(interval=self.EMPTY_INTERVAL, text_fragment=text)
        self.assertIsNone(frag.identifier)

    def test_fragment_identifier_not_empty(self):
        text = TextFragment(identifier="f001")
        frag = SyncMapFragment(interval=self.EMPTY_INTERVAL, text_fragment=text)
        self.assertEqual(frag.identifier, "f001")

    def test_fragment_text_empty(self):
        frag = SyncMapFragment(interval=self.EMPTY_INTERVAL)
        self.assertIsNone(frag.text)

    def test_fragment_text_empty_bis(self):
        text = TextFragment()
        frag = SyncMapFragment(interval=self.EMPTY_INTERVAL, text_fragment=text)
        self.assertEqual(frag.text, "")

    def test_fragment_text_not_empty(self):
        text = TextFragment(lines=["Hello", "World"])
        frag = SyncMapFragment(interval=self.EMPTY_INTERVAL, text_fragment=text)
        self.assertEqual(frag.text, "Hello World")

    def test_fragment_ordering(self):
        t_0_0 = SyncMapFragment.from_begin_end(
            begin=TimeValue("0.000"), end=TimeValue("0.000")
        )
        t_0_1 = SyncMapFragment.from_begin_end(
            begin=TimeValue("0.000"), end=TimeValue("1.000")
        )
        t_0_3 = SyncMapFragment.from_begin_end(
            begin=TimeValue("0.000"), end=TimeValue("3.000")
        )
        q_0_3 = SyncMapFragment.from_begin_end(
            begin=TimeValue("0.000"), end=TimeValue("3.000")
        )
        t_2_2 = SyncMapFragment.from_begin_end(
            begin=TimeValue("2.000"), end=TimeValue("2.000")
        )
        q_2_2 = SyncMapFragment.from_begin_end(
            begin=TimeValue("2.000"), end=TimeValue("2.000")
        )
        self.assertTrue(t_0_0 <= t_0_0)
        self.assertTrue(t_0_0 == t_0_0)
        self.assertTrue(t_0_0 >= t_0_0)
        self.assertFalse(t_0_0 != t_0_0)
        self.assertTrue(t_0_1 <= t_0_1)
        self.assertTrue(t_0_1 == t_0_1)
        self.assertTrue(t_0_1 >= t_0_1)
        self.assertTrue(t_0_0 < t_0_1)
        self.assertTrue(t_0_0 < t_0_3)
        self.assertTrue(t_0_0 < t_2_2)
        self.assertTrue(t_0_0 <= t_0_1)
        self.assertTrue(t_0_0 <= t_0_3)
        self.assertTrue(t_0_0 <= t_2_2)
        self.assertFalse(t_0_3 < q_0_3)
        self.assertTrue(t_0_3 <= q_0_3)
        self.assertTrue(t_0_3 == q_0_3)
        self.assertTrue(t_0_3 >= q_0_3)
        self.assertFalse(t_0_3 > q_0_3)
        self.assertFalse(t_0_3 != q_0_3)
        self.assertFalse(t_2_2 < q_2_2)
        self.assertTrue(t_2_2 <= q_2_2)
        self.assertTrue(t_2_2 == q_2_2)
        self.assertTrue(t_2_2 >= q_2_2)
        self.assertFalse(t_2_2 > q_2_2)
        self.assertFalse(t_2_2 != q_2_2)

    def test_fragment_length(self):
        text = TextFragment(lines=["Hello", "World"])
        frag = SyncMapFragment.from_begin_end(
            begin=TimeValue("1.234"), end=TimeValue("6.234"), text_fragment=text
        )
        self.assertEqual(frag.chars, 10)
        self.assertEqual(frag.length, 5)
        self.assertEqual(frag.has_zero_length, False)

    def test_fragment_zero_length(self):
        text = TextFragment(lines=["Hello", "World"])
        frag = SyncMapFragment(interval=self.EMPTY_INTERVAL, text_fragment=text)
        self.assertEqual(frag.chars, 10)
        self.assertEqual(frag.length, 0)
        self.assertEqual(frag.has_zero_length, True)

    def test_fragment_regular_rate_non_zero(self):
        text = TextFragment(lines=["Hello", "World"])
        frag = SyncMapFragment.from_begin_end(
            begin=TimeValue("1.234"),
            end=TimeValue("6.234"),
            text_fragment=text,
            fragment_type=FragmentType.REGULAR,
        )
        self.assertEqual(frag.length, 5)
        self.assertEqual(frag.chars, 10)
        self.assertEqual(frag.rate, 2.000)
        self.assertEqual(frag.rate, decimal.Decimal("2.000"))

    def test_fragment_regular_rate_zero_length(self):
        text = TextFragment(lines=["Hello", "World"])
        frag = SyncMapFragment.from_begin_end(
            begin=TimeValue("1.234"),
            end=TimeValue("1.234"),
            text_fragment=text,
            fragment_type=FragmentType.REGULAR,
        )
        self.assertEqual(frag.length, 0)
        self.assertEqual(frag.chars, 10)
        self.assertIsNone(frag.rate)

    def test_fragment_regular_rate_zero_text(self):
        text = TextFragment()
        frag = SyncMapFragment.from_begin_end(
            begin=TimeValue("1.234"),
            end=TimeValue("6.234"),
            text_fragment=text,
            fragment_type=FragmentType.REGULAR,
        )
        self.assertEqual(frag.length, 5)
        self.assertEqual(frag.chars, 0)
        self.assertEqual(frag.rate, 0)

    def test_fragment_not_regular_rate_non_zero_length(self):
        for fragment_type in SyncMapFragment.NOT_REGULAR_TYPES:
            with self.subTest(fragment_type=fragment_type):
                text = TextFragment()
                frag = SyncMapFragment.from_begin_end(
                    begin=TimeValue("1.234"),
                    end=TimeValue("6.234"),
                    text_fragment=text,
                    fragment_type=fragment_type,
                )
                self.assertEqual(frag.length, 5)
                self.assertEqual(frag.chars, 0)
                self.assertIsNone(frag.rate)

    def test_fragment_not_regular_rate_zero_length(self):
        for fragment_type in SyncMapFragment.NOT_REGULAR_TYPES:
            with self.subTest(fragment_type=fragment_type):
                text = TextFragment()
                frag = SyncMapFragment.from_begin_end(
                    begin=TimeValue("1.234"),
                    end=TimeValue("1.234"),
                    text_fragment=text,
                    fragment_type=fragment_type,
                )
                self.assertEqual(frag.length, 0)
                self.assertEqual(frag.chars, 0)
                self.assertIsNone(frag.rate)

    def test_fragment_regular_rate_lack(self):
        cases = (
            ("20.000", "0.500", "-0.500"),
            ("10.000", "1.000", "0.000"),
            ("5.000", "2.000", "1.000"),
        )
        text = TextFragment(lines=["Hello", "World"])
        for r, e_zero, e_nonzero in cases:
            with self.subTest(r=r, e_zero=e_zero, e_nonzero=e_nonzero):
                frag = SyncMapFragment.from_begin_end(
                    begin=TimeValue("1.000"),
                    end=TimeValue("1.000"),
                    text_fragment=text,
                    fragment_type=FragmentType.REGULAR,
                )
                self.assertEqual(frag.rate_lack(decimal.Decimal(r)), TimeValue(e_zero))

                frag = SyncMapFragment.from_begin_end(
                    begin=TimeValue("0.000"),
                    end=TimeValue("1.000"),
                    text_fragment=text,
                    fragment_type=FragmentType.REGULAR,
                )
                self.assertEqual(
                    frag.rate_lack(decimal.Decimal(r)), TimeValue(e_nonzero)
                )

    def test_fragment_regular_rate_slack(self):
        cases = (
            ("20.000", "-0.500", "0.500"),
            ("10.000", "-1.000", "0.000"),
            ("5.000", "-2.000", "-1.000"),
        )
        text = TextFragment(lines=["Hello", "World"])
        for r, e_zero, e_nonzero in cases:
            with self.subTest(r=r, e_zero=e_zero, e_nonzero=e_nonzero):
                frag = SyncMapFragment.from_begin_end(
                    begin=TimeValue("1.000"),
                    end=TimeValue("1.000"),
                    text_fragment=text,
                    fragment_type=FragmentType.REGULAR,
                )
                self.assertEqual(frag.rate_slack(decimal.Decimal(r)), TimeValue(e_zero))

                frag = SyncMapFragment.from_begin_end(
                    begin=TimeValue("0.000"),
                    end=TimeValue("1.000"),
                    text_fragment=text,
                    fragment_type=FragmentType.REGULAR,
                )
                self.assertEqual(
                    frag.rate_slack(decimal.Decimal(r)), TimeValue(e_nonzero)
                )

    def test_fragment_not_regular_rate_lack(self):
        cases = (
            ("20.000", "0.000", "0.000"),
            ("10.000", "0.000", "0.000"),
            ("5.000", "0.000", "0.000"),
        )
        text = TextFragment()
        for fragment_type in SyncMapFragment.NOT_REGULAR_TYPES:
            for r, e_zero, e_nonzero in cases:
                with self.subTest(
                    fragment_type=fragment_type, r=r, e_zero=e_zero, e_nonzero=e_nonzero
                ):
                    frag = SyncMapFragment.from_begin_end(
                        begin=TimeValue("1.000"),
                        end=TimeValue("1.000"),
                        text_fragment=text,
                        fragment_type=fragment_type,
                    )
                    self.assertEqual(
                        frag.rate_lack(decimal.Decimal(r)), TimeValue(e_zero)
                    )

                    frag = SyncMapFragment.from_begin_end(
                        begin=TimeValue("0.000"),
                        end=TimeValue("1.000"),
                        text_fragment=text,
                        fragment_type=fragment_type,
                    )
                    self.assertEqual(
                        frag.rate_lack(decimal.Decimal(r)), TimeValue(e_nonzero)
                    )

    def test_fragment_nonspeech_rate_slack(self):
        cases = (
            ("20.000", "0.000", "1.000"),
            ("10.000", "0.000", "1.000"),
            ("5.000", "0.000", "1.000"),
        )
        text = TextFragment()
        for r, e_zero, e_nonzero in cases:
            with self.subTest(r=r, e_zero=e_zero, e_nonzero=e_nonzero):
                frag = SyncMapFragment.from_begin_end(
                    begin=TimeValue("1.000"),
                    end=TimeValue("1.000"),
                    text_fragment=text,
                    fragment_type=FragmentType.NONSPEECH,
                )
                self.assertEqual(frag.rate_slack(decimal.Decimal(r)), TimeValue(e_zero))

                frag = SyncMapFragment.from_begin_end(
                    begin=TimeValue("0.000"),
                    end=TimeValue("1.000"),
                    text_fragment=text,
                    fragment_type=FragmentType.NONSPEECH,
                )
                self.assertEqual(
                    frag.rate_slack(decimal.Decimal(r)), TimeValue(e_nonzero)
                )

    def test_fragment_head_tail_rate_slack(self):
        cases = (
            ("20.000", "0.000", "0.000"),
            ("10.000", "0.000", "0.000"),
            ("5.000", "0.000", "0.000"),
        )
        text = TextFragment()
        for fragment_type in (FragmentType.HEAD, FragmentType.TAIL):
            for r, e_zero, e_nonzero in cases:
                with self.subTest(
                    fragment_type=fragment_type, r=r, e_zero=e_zero, e_nonzero=e_nonzero
                ):
                    frag = SyncMapFragment.from_begin_end(
                        begin=TimeValue("1.000"),
                        end=TimeValue("1.000"),
                        text_fragment=text,
                        fragment_type=fragment_type,
                    )
                    self.assertEqual(
                        frag.rate_slack(decimal.Decimal(r)), TimeValue(e_zero)
                    )

                    frag = SyncMapFragment.from_begin_end(
                        begin=TimeValue("0.000"),
                        end=TimeValue("1.000"),
                        text_fragment=text,
                        fragment_type=fragment_type,
                    )
                    self.assertEqual(
                        frag.rate_slack(decimal.Decimal(r)), TimeValue(e_nonzero)
                    )
