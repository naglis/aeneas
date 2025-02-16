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

import numpy

from aeneas.exacttiming import TimeInterval, TimeValue

from .common import BaseCase


class TestExactTiming(BaseCase):
    def check(self, value, expected=None):
        self.assertIsInstance(value, TimeValue)
        if expected is not None:
            self.assertEqual(value, expected)

    def check_numpy(self, value, expected=None):
        self.assertIsInstance(value[0], TimeValue)
        self.assertTrue((value == expected).all())

    def test_create_from_float(self):
        tv1 = TimeValue(1.234)
        self.check(tv1)

    def test_create_from_string(self):
        tv1 = TimeValue("1.234")
        self.check(tv1)

    def test_repr(self):
        tv1 = TimeValue("1.234")
        self.assertEqual(tv1.__repr__(), "TimeValue('1.234')")

    def test_geq_multiple(self):
        tv1 = TimeValue("0.005")
        tv2 = TimeValue("0.000")
        tv3 = TimeValue("0.001")
        tv4 = TimeValue("0.006")
        tv5 = TimeValue("0.010")
        self.check(tv1.geq_multiple(tv1), tv1)
        self.check(tv1.geq_multiple(tv2), tv1)
        self.check(tv1.geq_multiple(tv3), tv1)
        self.check(tv1.geq_multiple(tv4), tv5)
        self.check(tv1.geq_multiple(tv5), tv5)

    def test_add(self):
        tv1 = TimeValue("1.100")
        tv2 = TimeValue("2.200")
        tv3 = TimeValue("3.300")
        self.check(tv1 + tv2, tv3)
        self.check(tv2 + tv1, tv3)
        d = decimal.Decimal("2.200")
        self.check(tv1 + d, tv3)
        self.check(d + tv1, tv3)

    def test_div(self):
        tv1 = TimeValue("1.100")
        tv2 = TimeValue("2.200")
        tv3 = TimeValue("0.500")
        self.check(tv1 / tv2, tv3)
        d = decimal.Decimal("2.200")
        self.check(tv1 / d, tv3)

    def test_floordiv(self):
        tv1 = TimeValue("1.100")
        tv2 = TimeValue("2.200")
        tv3 = TimeValue("0.000")
        self.check(tv1 // tv2, tv3)
        d = decimal.Decimal("2.200")
        self.check(tv1 // d, tv3)

    def test_mod(self):
        tv1 = TimeValue("1.100")
        tv2 = TimeValue("2.200")
        tv3 = TimeValue("0.000")
        self.check(tv2 % tv1, tv3)
        d = decimal.Decimal("1.100")
        self.check(tv2 % d, tv3)

    def test_mul(self):
        tv1 = TimeValue("1.100")
        tv2 = TimeValue("2.200")
        tv3 = TimeValue("2.420")
        self.check(tv1 * tv2, tv3)
        self.check(tv2 * tv1, tv3)
        d = decimal.Decimal("2.200")
        self.check(tv1 * d, tv3)

    def test_sub(self):
        tv1 = TimeValue("1.100")
        tv2 = TimeValue("2.200")
        tv3 = TimeValue("-1.100")
        tv4 = TimeValue("1.100")
        self.check(tv1 - tv2, tv3)
        self.check(tv2 - tv1, tv4)
        d = decimal.Decimal("2.200")
        self.check(tv1 - d, tv3)

    def test_truediv(self):
        tv1 = TimeValue("1")
        tv2 = TimeValue("2")
        tv3 = TimeValue("0.5")
        self.check(tv1 / tv2, tv3)
        d = decimal.Decimal("2")
        self.check(tv1 / d, tv3)

    def test_op_float(self):
        tv1 = TimeValue("1.100")
        tv2 = 2.200
        tv3 = TimeValue("3.300")
        with self.assertRaises(TypeError):
            self.check(tv1 + tv2, tv3)
        with self.assertRaises(TypeError):
            self.check(tv1 / tv2, tv3)
        with self.assertRaises(TypeError):
            self.check(tv1 // tv2, tv3)
        with self.assertRaises(TypeError):
            self.check(tv1 * tv2, tv3)
        with self.assertRaises(TypeError):
            self.check(tv1 - tv2, tv3)

    def test_numpy_int(self):
        tv1 = TimeValue("1.000")
        n1 = numpy.array([0, 1, 2], dtype=int)
        n2 = numpy.array(
            [TimeValue("1.000"), TimeValue("2.000"), TimeValue("3.000")],
            dtype=TimeValue,
        )
        n3 = numpy.array(
            [TimeValue("0.000"), TimeValue("1.000"), TimeValue("2.000")],
            dtype=TimeValue,
        )
        self.check_numpy(n1 + tv1, n2)
        self.check_numpy(n1 * tv1, n3)

    def test_numpy_float(self):
        tv1 = TimeValue("1.000")
        n1 = numpy.array([0.0, 1.0, 2.0], dtype=float)
        n2 = numpy.array(
            [TimeValue("1.000"), TimeValue("2.000"), TimeValue("3.000")],
            dtype=TimeValue,
        )
        n3 = numpy.array(
            [TimeValue("0.000"), TimeValue("1.000"), TimeValue("2.000")],
            dtype=TimeValue,
        )
        with self.assertRaises(TypeError):
            self.check_numpy(n1 + tv1, n2)
        with self.assertRaises(TypeError):
            self.check_numpy(n1 * tv1, n3)

    def test_numpy_tv(self):
        tv1 = TimeValue("1.000")
        n1 = numpy.array(
            [TimeValue("0.000"), TimeValue("1.000"), TimeValue("2.000")],
            dtype=TimeValue,
        )
        n2 = numpy.array(
            [TimeValue("1.000"), TimeValue("2.000"), TimeValue("3.000")],
            dtype=TimeValue,
        )
        n3 = numpy.array(
            [TimeValue("0.000"), TimeValue("1.000"), TimeValue("2.000")],
            dtype=TimeValue,
        )
        self.check_numpy(n1 + tv1, n2)
        self.check_numpy(n1 * tv1, n3)

    def test_numpy_decimal(self):
        tv1 = TimeValue("1.000")
        n1 = numpy.array(
            [
                decimal.Decimal("0.000"),
                decimal.Decimal("1.000"),
                decimal.Decimal("2.000"),
            ],
            dtype=decimal.Decimal,
        )
        n2 = numpy.array(
            [TimeValue("1.000"), TimeValue("2.000"), TimeValue("3.000")],
            dtype=TimeValue,
        )
        n3 = numpy.array(
            [TimeValue("0.000"), TimeValue("1.000"), TimeValue("2.000")],
            dtype=TimeValue,
        )
        self.check_numpy(n1 + tv1, n2)
        self.check_numpy(n1 * tv1, n3)

    def test_is_integer(self):
        for v, e in [
            ("0", True),
            ("0.0", True),
            ("0.00", True),
            ("0.000", True),
            ("0.0000000", True),
            ("1", True),
            ("1.0", True),
            ("1.00", True),
            ("1.000", True),
            ("1.000000", True),
            ("-1", True),
            ("-1.0", True),
            ("-1.00", True),
            ("-1.000", True),
            ("-1.000000", True),
            ("0.1", False),
            ("0.01", False),
            ("0.001", False),
            ("0.000001", False),
            ("-0.1", False),
            ("-0.01", False),
            ("-0.001", False),
            ("-0.000001", False),
            ("1.1", False),
            ("1.01", False),
            ("1.001", False),
            ("1.000001", False),
            ("-1.1", False),
            ("-1.01", False),
            ("-1.001", False),
            ("-1.000001", False),
        ]:
            v = TimeValue(v)
            self.assertEqual(v.is_integer, e)

    def test_product_is_integer(self):
        for m, s, e in [
            ("0.001", 16000, True),
            ("0.001", 22050, False),
            ("0.001", 44100, False),
            ("0.005", 16000, True),
            ("0.005", 22050, False),
            ("0.005", 44100, False),
            ("0.010", 16000, True),
            ("0.010", 22050, False),
            ("0.010", 44100, True),
            ("0.020", 16000, True),
            ("0.020", 22050, True),
            ("0.020", 44100, True),
            ("0.040", 16000, True),
            ("0.040", 22050, True),
            ("0.040", 44100, True),
            ("1.000", 16000, True),
            ("1.000", 22050, True),
            ("1.000", 44100, True),
        ]:
            prod = TimeValue(m) * s
            self.assertIsInstance(prod, TimeValue)
            self.assertEqual(int(prod) == prod, e)
            self.assertEqual(prod.is_integer, e)

    def test_time_interval_bad_value(self):
        params = (
            ("1.000", "0.000"),
            ("-1.000", "0.000"),
            ("0.000", "-1.000"),
            ("-2.000", "-1.000"),
        )
        for begin, end in params:
            with self.subTest(begin=begin, end=end), self.assertRaises(ValueError):
                TimeInterval(begin=TimeValue(begin), end=TimeValue(end))

    def test_time_interval_constructor(self):
        params = (
            ("0.000", "0.000"),
            ("0.000", "1.000"),
            ("1.000", "1.000"),
            ("1.234", "1.235"),
        )
        for begin, end in params:
            with self.subTest(begin=begin, end=end):
                TimeInterval(begin=TimeValue(begin), end=TimeValue(end))

    def test_time_interval_percent(self):
        params = (
            (-100, "0.000"),
            (-50, "0.000"),
            (0, "0.000"),
            (10, "0.100"),
            (25, "0.250"),
            (50, "0.500"),
            (75, "0.750"),
            (90, "0.900"),
            (100, "1.000"),
            (150, "1.000"),
            (200, "1.000"),
        )
        t = TimeInterval(begin=TimeValue("0.000"), end=TimeValue("1.000"))
        for p, e in params:
            with self.subTest(p=p, e=e):
                p = decimal.Decimal(p)
                e = TimeValue(e)
                self.assertEqual(t.percent_value(p), e)

    def test_time_interval_ordering(self):
        t_0_0 = TimeInterval(begin=TimeValue("0.000"), end=TimeValue("0.000"))
        t_0_1 = TimeInterval(begin=TimeValue("0.000"), end=TimeValue("1.000"))
        t_0_3 = TimeInterval(begin=TimeValue("0.000"), end=TimeValue("3.000"))
        q_0_3 = TimeInterval(begin=TimeValue("0.000"), end=TimeValue("3.000"))
        t_2_2 = TimeInterval(begin=TimeValue("2.000"), end=TimeValue("2.000"))
        q_2_2 = TimeInterval(begin=TimeValue("2.000"), end=TimeValue("2.000"))
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

    def test_time_interval_length(self):
        params = (
            ("0.000", "0.000", "0.000"),
            ("0.000", "1.000", "1.000"),
            ("1.000", "1.000", "0.000"),
            ("1.234", "1.235", "0.001"),
        )
        for begin, end, length in params:
            with self.subTest(begin=begin, end=end, length=length):
                ti = TimeInterval(begin=TimeValue(begin), end=TimeValue(end))
                self.assertEqual(ti.length, TimeValue(length))

    def test_time_interval_has_zero_length(self):
        params = (
            ("0.000", "0.000", True),
            ("0.000", "1.000", False),
            ("1.000", "1.000", True),
            ("1.234", "1.235", False),
        )
        for begin, end, f in params:
            with self.subTest(begin=begin, end=end, f=f):
                ti = TimeInterval(begin=TimeValue(begin), end=TimeValue(end))
                self.assertEqual(ti.has_zero_length, f)

    def test_time_interval_starts_at(self):
        params = (
            ("1.234", "1.237", "0.000", False),
            ("1.234", "1.237", "1.233", False),
            ("1.234", "1.237", "1.234", True),
            ("1.234", "1.237", "1.235", False),
            ("1.234", "1.237", "1.236", False),
            ("1.234", "1.237", "1.237", False),
            ("1.234", "1.237", "1.238", False),
            ("1.234", "1.237", "2.000", False),
        )
        for b, e, p, f in params:
            ti = TimeInterval(begin=TimeValue(b), end=TimeValue(e))
            self.assertEqual(ti.starts_at(TimeValue(p)), f)

    def test_time_interval_ends_at(self):
        params = (
            ("1.234", "1.237", "0.000", False),
            ("1.234", "1.237", "1.233", False),
            ("1.234", "1.237", "1.234", False),
            ("1.234", "1.237", "1.235", False),
            ("1.234", "1.237", "1.236", False),
            ("1.234", "1.237", "1.237", True),
            ("1.234", "1.237", "1.238", False),
            ("1.234", "1.237", "2.000", False),
        )
        for begin, end, p, f in params:
            with self.subTest(begin=begin, end=end, p=p, f=f):
                ti = TimeInterval(begin=TimeValue(begin), end=TimeValue(end))
                self.assertEqual(ti.ends_at(TimeValue(p)), f)

    def test_time_interval_offset(self):
        params = (
            (("0.000", "0.000"), "-1.000", False, ("0.000", "0.000")),
            (("0.000", "0.000"), "-0.000", False, ("0.000", "0.000")),
            (("0.000", "0.000"), "0.000", False, ("0.000", "0.000")),
            (("0.000", "0.000"), "0.500", False, ("0.500", "0.500")),
            (("1.000", "2.000"), "-2.500", False, ("0.000", "0.000")),
            (("1.000", "2.000"), "-2.000", False, ("0.000", "0.000")),
            (("1.000", "2.000"), "-1.500", False, ("0.000", "0.500")),
            (("1.000", "2.000"), "-1.000", False, ("0.000", "1.000")),
            (("1.000", "2.000"), "-0.000", False, ("1.000", "2.000")),
            (("1.000", "2.000"), "0.000", False, ("1.000", "2.000")),
            (("1.000", "2.000"), "0.500", False, ("1.500", "2.500")),
            (("1.000", "2.000"), "1.000", False, ("2.000", "3.000")),
            (("0.000", "0.000"), "-1.000", True, ("-1.000", "-1.000")),
            (("0.000", "0.000"), "-0.000", True, ("0.000", "0.000")),
            (("0.000", "0.000"), "0.000", True, ("0.000", "0.000")),
            (("0.000", "0.000"), "0.500", True, ("0.500", "0.500")),
            (("1.000", "2.000"), "-2.500", True, ("-1.500", "-0.500")),
            (("1.000", "2.000"), "-2.000", True, ("-1.000", "0.000")),
            (("1.000", "2.000"), "-1.500", True, ("-0.500", "0.500")),
            (("1.000", "2.000"), "-1.000", True, ("0.000", "1.000")),
            (("1.000", "2.000"), "-0.000", True, ("1.000", "2.000")),
            (("1.000", "2.000"), "0.000", True, ("1.000", "2.000")),
            (("1.000", "2.000"), "0.500", True, ("1.500", "2.500")),
            (("1.000", "2.000"), "1.000", True, ("2.000", "3.000")),
        )
        for ti1, offset, allow_negative, expected in params:
            with self.subTest(
                ti1=ti1, offset=offset, allow_negative=allow_negative, expected=expected
            ):
                ti1 = TimeInterval(begin=TimeValue(ti1[0]), end=TimeValue(ti1[1]))
                ti1.offset(offset=TimeValue(offset), allow_negative=allow_negative)
                self.assertEqual(ti1.begin, TimeValue(expected[0]))
                self.assertEqual(ti1.end, TimeValue(expected[1]))

    def test_time_interval_contains(self):
        params = (
            ("1.000", "1.000", "0.000", False),
            ("1.000", "1.000", "0.999", False),
            ("1.000", "1.000", "1.000", True),
            ("1.000", "1.000", "1.001", False),
            ("1.000", "1.000", "2.000", False),
            ("1.000", "1.001", "0.000", False),
            ("1.000", "1.001", "0.999", False),
            ("1.000", "1.001", "1.000", True),
            ("1.000", "1.001", "1.001", True),
            ("1.000", "1.001", "1.002", False),
            ("1.000", "1.001", "2.000", False),
            ("1.000", "1.002", "0.000", False),
            ("1.000", "1.002", "0.999", False),
            ("1.000", "1.002", "1.000", True),
            ("1.000", "1.002", "1.001", True),
            ("1.000", "1.002", "1.002", True),
            ("1.000", "1.002", "1.003", False),
            ("1.000", "1.002", "2.000", False),
            ("1.234", "1.237", "0.000", False),
            ("1.234", "1.237", "1.233", False),
            ("1.234", "1.237", "1.234", True),
            ("1.234", "1.237", "1.235", True),
            ("1.234", "1.237", "1.236", True),
            ("1.234", "1.237", "1.237", True),
            ("1.234", "1.237", "1.238", False),
            ("1.234", "1.237", "2.000", False),
        )
        for begin, end, p, f in params:
            with self.subTest(begin=begin, end=end, p=p, f=f):
                ti = TimeInterval(begin=TimeValue(begin), end=TimeValue(end))
                self.assertEqual(ti.contains(TimeValue(p)), f)

    def test_time_interval_inner_contains(self):
        params = (
            ("1.000", "1.000", "0.000", False),
            ("1.000", "1.000", "0.999", False),
            ("1.000", "1.000", "1.000", False),
            ("1.000", "1.000", "1.001", False),
            ("1.000", "1.000", "2.000", False),
            ("1.000", "1.001", "0.000", False),
            ("1.000", "1.001", "0.999", False),
            ("1.000", "1.001", "1.000", False),
            ("1.000", "1.001", "1.001", False),
            ("1.000", "1.001", "1.002", False),
            ("1.000", "1.001", "2.000", False),
            ("1.000", "1.002", "0.000", False),
            ("1.000", "1.002", "0.999", False),
            ("1.000", "1.002", "1.000", False),
            ("1.000", "1.002", "1.001", True),
            ("1.000", "1.002", "1.002", False),
            ("1.000", "1.002", "1.003", False),
            ("1.000", "1.002", "2.000", False),
            ("1.234", "1.237", "0.000", False),
            ("1.234", "1.237", "1.233", False),
            ("1.234", "1.237", "1.234", False),
            ("1.234", "1.237", "1.235", True),
            ("1.234", "1.237", "1.236", True),
            ("1.234", "1.237", "1.237", False),
            ("1.234", "1.237", "1.238", False),
            ("1.234", "1.237", "2.000", False),
        )
        for begin, end, p, f in params:
            with self.subTest(beging=begin, end=end, p=p, f=f):
                ti = TimeInterval(begin=TimeValue(begin), end=TimeValue(end))
                self.assertEqual(ti.inner_contains(TimeValue(p)), f)

    def test_time_interval_relative_position_of(self):
        params = (
            # TABLE 1
            (
                ("1.000", "1.000"),
                ("0.000", "0.000"),
                TimeInterval.RELATIVE_POSITION_PP_L,
            ),
            (
                ("1.000", "1.000"),
                ("1.000", "1.000"),
                TimeInterval.RELATIVE_POSITION_PP_C,
            ),
            (
                ("1.000", "1.000"),
                ("2.000", "2.000"),
                TimeInterval.RELATIVE_POSITION_PP_G,
            ),
            # TABLE 2
            (
                ("1.000", "1.000"),
                ("0.000", "0.500"),
                TimeInterval.RELATIVE_POSITION_PI_LL,
            ),
            (
                ("1.000", "1.000"),
                ("0.500", "1.000"),
                TimeInterval.RELATIVE_POSITION_PI_LC,
            ),
            (
                ("1.000", "1.000"),
                ("0.500", "1.500"),
                TimeInterval.RELATIVE_POSITION_PI_LG,
            ),
            (
                ("1.000", "1.000"),
                ("1.000", "1.500"),
                TimeInterval.RELATIVE_POSITION_PI_CG,
            ),
            (
                ("1.000", "1.000"),
                ("1.500", "2.000"),
                TimeInterval.RELATIVE_POSITION_PI_GG,
            ),
            # TABLE 3
            (
                ("1.000", "2.000"),
                ("0.000", "0.000"),
                TimeInterval.RELATIVE_POSITION_IP_L,
            ),
            (
                ("1.000", "2.000"),
                ("1.000", "1.000"),
                TimeInterval.RELATIVE_POSITION_IP_B,
            ),
            (
                ("1.000", "2.000"),
                ("1.500", "1.500"),
                TimeInterval.RELATIVE_POSITION_IP_I,
            ),
            (
                ("1.000", "2.000"),
                ("2.000", "2.000"),
                TimeInterval.RELATIVE_POSITION_IP_E,
            ),
            (
                ("1.000", "2.000"),
                ("2.500", "2.500"),
                TimeInterval.RELATIVE_POSITION_IP_G,
            ),
            # TABLE 4
            (
                ("1.000", "2.000"),
                ("0.000", "0.500"),
                TimeInterval.RELATIVE_POSITION_II_LL,
            ),
            (
                ("1.000", "2.000"),
                ("0.000", "1.000"),
                TimeInterval.RELATIVE_POSITION_II_LB,
            ),
            (
                ("1.000", "2.000"),
                ("0.000", "1.500"),
                TimeInterval.RELATIVE_POSITION_II_LI,
            ),
            (
                ("1.000", "2.000"),
                ("0.000", "2.000"),
                TimeInterval.RELATIVE_POSITION_II_LE,
            ),
            (
                ("1.000", "2.000"),
                ("0.000", "2.500"),
                TimeInterval.RELATIVE_POSITION_II_LG,
            ),
            # TABLE 5
            (
                ("1.000", "2.000"),
                ("1.000", "1.500"),
                TimeInterval.RELATIVE_POSITION_II_BI,
            ),
            (
                ("1.000", "2.000"),
                ("1.000", "2.000"),
                TimeInterval.RELATIVE_POSITION_II_BE,
            ),
            (
                ("1.000", "2.000"),
                ("1.000", "2.500"),
                TimeInterval.RELATIVE_POSITION_II_BG,
            ),
            # TABLE 6
            (
                ("1.000", "2.000"),
                ("1.100", "1.500"),
                TimeInterval.RELATIVE_POSITION_II_II,
            ),
            (
                ("1.000", "2.000"),
                ("1.100", "2.000"),
                TimeInterval.RELATIVE_POSITION_II_IE,
            ),
            (
                ("1.000", "2.000"),
                ("1.100", "2.500"),
                TimeInterval.RELATIVE_POSITION_II_IG,
            ),
            # TABLE 7
            (
                ("1.000", "2.000"),
                ("2.000", "2.500"),
                TimeInterval.RELATIVE_POSITION_II_EG,
            ),
            # TABLE 8
            (
                ("1.000", "2.000"),
                ("2.500", "3.000"),
                TimeInterval.RELATIVE_POSITION_II_GG,
            ),
        )
        for ti1, ti2, expected in params:
            with self.subTest(ti1=ti1, ti2=ti2, expected=expected):
                ti1 = TimeInterval(begin=TimeValue(ti1[0]), end=TimeValue(ti1[1]))
                ti2 = TimeInterval(begin=TimeValue(ti2[0]), end=TimeValue(ti2[1]))
                self.assertEqual(ti1.relative_position_of(ti2), expected)
                self.assertEqual(ti2.relative_position_wrt(ti1), expected)

    def test_time_interval_intersection(self):
        params = (
            # TABLE 1
            (("1.000", "1.000"), ("0.000", "0.000"), None),
            (("1.000", "1.000"), ("1.000", "1.000"), ("1.000", "1.000")),
            (("1.000", "1.000"), ("2.000", "2.000"), None),
            # TABLE 2
            (("1.000", "1.000"), ("0.000", "0.500"), None),
            (("1.000", "1.000"), ("0.500", "1.000"), ("1.000", "1.000")),
            (("1.000", "1.000"), ("0.500", "1.500"), ("1.000", "1.000")),
            (("1.000", "1.000"), ("1.000", "1.500"), ("1.000", "1.000")),
            (("1.000", "1.000"), ("1.500", "2.000"), None),
            # TABLE 3
            (("1.000", "2.000"), ("0.000", "0.000"), None),
            (("1.000", "2.000"), ("1.000", "1.000"), ("1.000", "1.000")),
            (("1.000", "2.000"), ("1.500", "1.500"), ("1.500", "1.500")),
            (("1.000", "2.000"), ("2.000", "2.000"), ("2.000", "2.000")),
            (("1.000", "2.000"), ("2.500", "2.500"), None),
            # TABLE 4
            (("1.000", "2.000"), ("0.000", "0.500"), None),
            (("1.000", "2.000"), ("0.000", "1.000"), ("1.000", "1.000")),
            (("1.000", "2.000"), ("0.000", "1.500"), ("1.000", "1.500")),
            (("1.000", "2.000"), ("0.000", "2.000"), ("1.000", "2.000")),
            (("1.000", "2.000"), ("0.000", "2.500"), ("1.000", "2.000")),
            # TABLE 5
            (("1.000", "2.000"), ("1.000", "1.500"), ("1.000", "1.500")),
            (("1.000", "2.000"), ("1.000", "2.000"), ("1.000", "2.000")),
            (("1.000", "2.000"), ("1.000", "2.500"), ("1.000", "2.000")),
            # TABLE 6
            (("1.000", "2.000"), ("1.100", "1.500"), ("1.100", "1.500")),
            (("1.000", "2.000"), ("1.100", "2.000"), ("1.100", "2.000")),
            (("1.000", "2.000"), ("1.100", "2.500"), ("1.100", "2.000")),
            # TABLE 7
            (("1.000", "2.000"), ("2.000", "2.500"), ("2.000", "2.000")),
            # TABLE 8
            (("1.000", "2.000"), ("2.500", "3.000"), None),
        )
        for ti1, ti2, expected in params:
            with self.subTest(ti1=ti1, ti2=ti2, expected=expected):
                ti1 = TimeInterval(begin=TimeValue(ti1[0]), end=TimeValue(ti1[1]))
                ti2 = TimeInterval(begin=TimeValue(ti2[0]), end=TimeValue(ti2[1]))
                if expected is not None:
                    expected = TimeInterval(
                        begin=TimeValue(expected[0]), end=TimeValue(expected[1])
                    )
                self.assertEqual(ti1.intersection(ti2), expected)
                self.assertEqual(ti2.intersection(ti1), expected)
                self.assertEqual(ti1.overlaps(ti2), expected is not None)
                self.assertEqual(ti2.overlaps(ti1), expected is not None)

    def test_time_interval_adjacent(self):
        params = (
            (("1.000", "1.000"), ("0.000", "2.000"), False),
            (("1.000", "1.000"), ("0.999", "2.000"), False),
            (("1.000", "1.000"), ("1.000", "1.000"), True),
            (("1.000", "1.000"), ("1.000", "2.000"), True),
            (("1.000", "1.000"), ("1.001", "2.000"), False),
            (("1.000", "1.000"), ("2.000", "2.000"), False),
            (("0.000", "1.000"), ("0.000", "2.000"), False),
            (("0.000", "1.000"), ("0.999", "2.000"), False),
            (("0.000", "1.000"), ("1.000", "1.000"), True),
            (("0.000", "1.000"), ("1.000", "2.000"), True),
            (("0.000", "1.000"), ("1.001", "2.000"), False),
            (("0.000", "1.000"), ("2.000", "2.000"), False),
        )
        for ti1, ti2, expected in params:
            with self.subTest(ti1=ti1, ti2=ti2, expected=expected):
                ti1 = TimeInterval(begin=TimeValue(ti1[0]), end=TimeValue(ti1[1]))
                ti2 = TimeInterval(begin=TimeValue(ti2[0]), end=TimeValue(ti2[1]))
                self.assertEqual(ti1.is_adjacent_before(ti2), expected)
                self.assertEqual(ti2.is_adjacent_after(ti1), expected)

    def test_time_interval_non_zero_before_non_zero(self):
        params = (
            (("1.000", "1.000"), ("0.000", "2.000"), False),
            (("1.000", "1.000"), ("0.999", "2.000"), False),
            (("1.000", "1.000"), ("1.000", "1.000"), False),
            (("1.000", "1.000"), ("1.000", "2.000"), False),
            (("1.000", "1.000"), ("1.001", "2.000"), False),
            (("1.000", "1.000"), ("2.000", "2.000"), False),
            (("0.000", "1.000"), ("0.000", "2.000"), False),
            (("0.000", "1.000"), ("0.999", "2.000"), False),
            (("0.000", "1.000"), ("1.000", "1.000"), False),
            (("0.000", "1.000"), ("1.000", "2.000"), True),
            (("0.000", "1.000"), ("1.001", "2.000"), False),
            (("0.000", "1.000"), ("2.000", "2.000"), False),
        )
        for ti1, ti2, expected in params:
            with self.subTest(ti1=ti1, ti2=ti2, expected=expected):
                ti1 = TimeInterval(begin=TimeValue(ti1[0]), end=TimeValue(ti1[1]))
                ti2 = TimeInterval(begin=TimeValue(ti2[0]), end=TimeValue(ti2[1]))
                self.assertEqual(ti1.is_non_zero_before_non_zero(ti2), expected)
                self.assertEqual(ti2.is_non_zero_after_non_zero(ti1), expected)
