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

import os
import sys
import tempfile
import unittest

from aeneas.exacttiming import TimeValue
import aeneas.globalfunctions as gf


class TestGlobalFunctions(unittest.TestCase):
    def test_tmp_file(self):
        tmp_handler, tmp_file = gf.tmp_file()
        self.assertTrue(os.path.isfile(tmp_file))
        gf.delete_file(tmp_handler, tmp_file)

    def test_tmp_file_suffix(self):
        tmp_handler, tmp_file = gf.tmp_file(suffix=".txt")
        self.assertTrue(os.path.isfile(tmp_file))
        gf.delete_file(tmp_handler, tmp_file)

    def test_safe_float(self):
        for value, default, expected in (
            ("3.14", 1.23, 3.14),
            (" 3.14", 1.23, 3.14),
            (" 3.14 ", 1.23, 3.14),
            ("3.14f", 1.23, 1.23),
            ("0x3.14", 1.23, 1.23),
            ("", 1.23, 1.23),
            ("foo", 1.23, 1.23),
            (None, 1.23, 1.23),
        ):
            with self.subTest(value=value, default=default, expected=expected):
                self.assertEqual(gf.safe_float(value, default), expected)

    def test_safe_int(self):
        for value, default, expected in (
            ("3.14", 1, 3),
            ("3.14 ", 1, 3),
            (" 3.14", 1, 3),
            (" 3.14 ", 1, 3),
            ("3.14f", 1, 1),
            ("0x3.14", 1, 1),
            ("3", 1, 3),
            ("3 ", 1, 3),
            (" 3", 1, 3),
            (" 3 ", 1, 3),
            ("3f", 1, 1),
            ("0x3", 1, 1),
            ("", 1, 1),
            ("foo", 1, 1),
            (None, 1, 1),
        ):
            with self.subTest(value=value, default=default, expected=expected):
                self.assertEqual(gf.safe_int(value, default), expected)

    def test_safe_get(self):
        for dictionary, key, default, expected in (
            (None, None, "default", "default"),
            (None, "key", "default", "default"),
            ({}, None, "default", "default"),
            ({}, "key", "default", "default"),
            ([], "key", "default", "default"),
            ({"key": "value"}, None, "default", "default"),
            ({"key": "value"}, "key", "default", "value"),
        ):
            with self.subTest(
                dictionary=dictionary, key=key, default=default, expected=expected
            ):
                self.assertEqual(gf.safe_get(dictionary, key, default), expected)

    def test_config_string_to_dict(self):
        for string, expected in (
            (None, {}),
            ("", {}),
            ("k1=v1", {"k1": "v1"}),
            ("k1=v1|", {"k1": "v1"}),
            ("|k1=v1|", {"k1": "v1"}),
            ("|k1=v1", {"k1": "v1"}),
            ("k1=v1|k1=v2", {"k1": "v2"}),
            ("k1=v1|k2=v2", {"k1": "v1", "k2": "v2"}),
            ("k1=v1|k2=v2|k1=v3", {"k1": "v3", "k2": "v2"}),
            ("k1=v1||k2=v2", {"k1": "v1", "k2": "v2"}),
            ("k1=v1|k2=v2|k3=v3", {"k1": "v1", "k2": "v2", "k3": "v3"}),
            ("k1=v1|k2=|k3=v3", {"k1": "v1", "k3": "v3"}),
            ("k1=v1|=v2|k3=v3", {"k1": "v1", "k3": "v3"}),
        ):
            with self.subTest(string=string, expected=expected):
                self.assertEqual(gf.config_string_to_dict(string), expected)

    def test_pairs_to_dict(self):
        for pairs, expected in (
            ([], {}),
            ([""], {}),
            (["k1"], {}),
            (["k1="], {}),
            (["=v1"], {}),
            (["k1=v1"], {"k1": "v1"}),
            (["k1=v1", ""], {"k1": "v1"}),
            (["k1=v1", "k2"], {"k1": "v1"}),
            (["k1=v1", "k2="], {"k1": "v1"}),
            (["k1=v1", "=v2"], {"k1": "v1"}),
            (["k1=v1", "k2=v2"], {"k1": "v1", "k2": "v2"}),
        ):
            with self.subTest(pairs=pairs, expected=expected):
                self.assertEqual(gf.pairs_to_dict(pairs), expected)

    def test_copytree(self):
        with (
            tempfile.TemporaryDirectory() as orig,
            tempfile.TemporaryDirectory() as dest,
        ):
            tmp_path = os.path.join(orig, "foo.bar")
            with open(tmp_path, "w", encoding="utf-8") as tmp_file:
                tmp_file.write("Foo bar")

            gf.copytree(orig, dest)

            self.assertTrue(os.path.isfile(os.path.join(dest, "foo.bar")))

    def test_ensure_parent_directory(self):
        with tempfile.TemporaryDirectory() as orig:
            tmp_path = os.path.join(orig, "foo.bar")
            tmp_parent = orig
            gf.ensure_parent_directory(tmp_path)
            self.assertTrue(os.path.isdir(tmp_parent))
            tmp_path = os.path.join(orig, "foo/bar.baz")
            tmp_parent = os.path.join(orig, "foo")
            gf.ensure_parent_directory(tmp_path)
            self.assertTrue(os.path.isdir(tmp_parent))
            tmp_path = os.path.join(orig, "bar")
            gf.ensure_parent_directory(tmp_path, ensure_parent=False)
            self.assertTrue(os.path.isdir(tmp_path))

    def test_ensure_parent_directory_parent_error(self):
        with self.assertRaises(OSError):
            gf.ensure_parent_directory("/foo/bar/baz")

    def test_ensure_parent_directory_no_parent_error(self):
        with self.assertRaises(OSError):
            gf.ensure_parent_directory("/foo/bar/baz", ensure_parent=False)

    def test_datetime_string(self):
        self.assertEqual(type(gf.datetime_string()), str)
        self.assertEqual(len(gf.datetime_string()), len("2016-01-01T00:00:00"))
        self.assertEqual(type(gf.datetime_string(time_zone=True)), str)
        self.assertEqual(
            len(gf.datetime_string(time_zone=True)), len("2016-01-01T00:00:00+00:00")
        )

    def test_time_from_ttml(self):
        for value, expected in (
            (None, TimeValue("0")),
            ("", TimeValue("0")),
            ("s", TimeValue("0")),
            ("0s", TimeValue("0")),
            ("000s", TimeValue("0")),
            ("1s", TimeValue("1")),
            ("001s", TimeValue("1")),
            ("1s", TimeValue("1")),
            ("001.234s", TimeValue("1.234")),
        ):
            with self.subTest(value=value, expected=expected):
                self.assertEqual(gf.time_from_ttml(value), expected)

    def test_time_to_ttml(self):
        for value, expected in (
            (None, "0.000s"),
            (0, "0.000s"),
            (1, "1.000s"),
            (1.234, "1.234s"),
        ):
            with self.subTest(value=value, expected=expected):
                self.assertEqual(gf.time_to_ttml(value), expected)

    def test_time_from_ssmmm(self):
        for value, expected in (
            (None, TimeValue("0")),
            ("", TimeValue("0")),
            ("0", TimeValue("0")),
            ("000", TimeValue("0")),
            ("1", TimeValue("1")),
            ("001", TimeValue("1")),
            ("1.234", TimeValue("1.234")),
            ("001.234", TimeValue("1.234")),
        ):
            with self.subTest(value=value, expected=expected):
                self.assertEqual(gf.time_from_ssmmm(value), expected)

    def test_time_to_ssmm(self):
        for value, expected in (
            (None, "0.000"),
            (0, "0.000"),
            (1, "1.000"),
            (1.234, "1.234"),
        ):
            with self.subTest(value=value, expected=expected):
                self.assertEqual(gf.time_to_ssmmm(value), expected)

    def test_time_from_hhmmssmmm(self):
        for value, expected in (
            (None, TimeValue("0.000")),
            ("", TimeValue("0.000")),
            ("23:45.678", TimeValue("0.000")),  # no 2 ":"
            ("3:45.678", TimeValue("0.000")),  # no 2 ":"
            ("45.678", TimeValue("0.000")),  # no 2 ":"
            ("5.678", TimeValue("0.000")),  # no 2 ":"
            ("5", TimeValue("0.000")),  # no 2 ":"
            ("00:00:01", TimeValue("0.000")),  # no "."
            ("1:23:45.678", TimeValue("5025.678")),  # tolerate this (?)
            ("1:2:45.678", TimeValue("3765.678")),  # tolerate this (?)
            ("1:23:4.678", TimeValue("4984.678")),  # tolerate this (?)
            ("1:23:4.", TimeValue("4984.000")),  # tolerate this (?)
            ("00:00:00.000", TimeValue("0.000")),
            ("00:00:12.000", TimeValue("12.000")),
            ("00:00:12.345", TimeValue("12.345")),
            ("00:01:00.000", TimeValue("60")),
            ("00:01:23.000", TimeValue("83.000")),
            ("00:01:23.456", TimeValue("83.456")),
            ("01:00:00.000", TimeValue("3600.000")),
            ("01:00:12.000", TimeValue("3612.000")),
            ("01:00:12.345", TimeValue("3612.345")),
            ("01:23:00.000", TimeValue("4980.000")),
            ("01:23:45.000", TimeValue("5025.000")),
            ("01:23:45.678", TimeValue("5025.678")),
        ):
            with self.subTest(value=value, expected=expected):
                self.assertEqual(gf.time_from_hhmmssmmm(value), expected)

    def test_time_to_hhmmssmmm(self):
        for value, expected in (
            (None, "00:00:00.000"),
            (0.000, "00:00:00.000"),
            (12.000, "00:00:12.000"),
            (12.345, "00:00:12.345"),
            (60, "00:01:00.000"),
            (83.000, "00:01:23.000"),
            (83.456, "00:01:23.456"),
            (3600.000, "01:00:00.000"),
            (3612.000, "01:00:12.000"),
            (3612.340, "01:00:12.340"),  # numerical issues
            (4980.000, "01:23:00.000"),
            (5025.000, "01:23:45.000"),
            (5025.670, "01:23:45.670"),  # numerical issues
        ):
            with self.subTest(value=value, expected=expected):
                self.assertEqual(gf.time_to_hhmmssmmm(value), expected)

    def test_time_to_srt(self):
        for value, expected in (
            (None, "00:00:00,000"),
            (0.000, "00:00:00,000"),
            (12.000, "00:00:12,000"),
            (12.345, "00:00:12,345"),
            (60, "00:01:00,000"),
            (83.000, "00:01:23,000"),
            (83.456, "00:01:23,456"),
            (3600.000, "01:00:00,000"),
            (3612.000, "01:00:12,000"),
            (3612.340, "01:00:12,340"),  # numerical issues
            (4980.000, "01:23:00,000"),
            (5025.000, "01:23:45,000"),
            (5025.670, "01:23:45,670"),  # numerical issues
        ):
            with self.subTest(value=value, expected=expected):
                self.assertEqual(gf.time_to_srt(value), expected)

    def test_is_posix(self):
        self.skipTest("TODO")

    def test_is_windows(self):
        self.skipTest("TODO")

    def test_fix_slash(self):
        self.skipTest("TODO")

    def test_can_run_c_extension(self):
        gf.can_run_c_extension()
        gf.can_run_c_extension("cdtw")
        gf.can_run_c_extension("cew")
        gf.can_run_c_extension("cmfcc")
        gf.can_run_c_extension("foo")
        gf.can_run_c_extension("bar")

    def test_run_c_extension_with_fallback(self):
        self.skipTest("TODO")

    def test_close_file_handler(self):
        handler, path = gf.tmp_file()
        self.assertTrue(os.path.isfile(path))
        gf.close_file_handler(handler)
        self.assertTrue(os.path.isfile(path))
        gf.delete_file(handler, path)
        self.assertFalse(os.path.isfile(path))

    def test_delete_file_existing(self):
        handler, path = gf.tmp_file()
        self.assertTrue(os.path.isfile(path))
        gf.delete_file(handler, path)
        self.assertFalse(os.path.isfile(path))

    def test_delete_file_not_existing(self):
        handler = None
        path = "/foo/bar/baz"
        self.assertFalse(os.path.isfile(path))
        gf.delete_file(handler, path)
        self.assertFalse(os.path.isfile(path))

    def test_relative_path(self):
        tests = [
            ("res", "aeneas/tools/somefile.py", "aeneas/tools/res"),
            ("res/foo", "aeneas/tools/somefile.py", "aeneas/tools/res/foo"),
            ("res/bar.baz", "aeneas/tools/somefile.py", "aeneas/tools/res/bar.baz"),
            (
                "res/bar/baz/foo",
                "aeneas/tools/somefile.py",
                "aeneas/tools/res/bar/baz/foo",
            ),
            (
                "res/bar/baz/foo.bar",
                "aeneas/tools/somefile.py",
                "aeneas/tools/res/bar/baz/foo.bar",
            ),
        ]
        for test in tests:
            self.assertEqual(gf.relative_path(test[0], test[1]), test[2])

    def test_absolute_path(self):
        base = os.path.dirname(os.path.realpath(sys.argv[0]))
        tests = [
            ("res", "aeneas/tools/somefile.py", os.path.join(base, "aeneas/tools/res")),
            (
                "res/foo",
                "aeneas/tools/somefile.py",
                os.path.join(base, "aeneas/tools/res/foo"),
            ),
            (
                "res/bar.baz",
                "aeneas/tools/somefile.py",
                os.path.join(base, "aeneas/tools/res/bar.baz"),
            ),
            ("res", "/aeneas/tools/somefile.py", "/aeneas/tools/res"),
            ("res/foo", "/aeneas/tools/somefile.py", "/aeneas/tools/res/foo"),
            ("res/bar.baz", "/aeneas/tools/somefile.py", "/aeneas/tools/res/bar.baz"),
        ]
        for test in tests:
            self.assertEqual(gf.absolute_path(test[0], test[1]), test[2])

    def test_is_utf8_encoded(self):
        tests = [
            (b"foo", True),
            (b"foo", True),
            (b"foo", True),
            ("foo".encode("utf-16"), False),
            ("foo".encode("utf-32"), False),
            ("foà".encode("latin-1"), False),
            ("foà".encode(), True),
            ("foà".encode("utf-16"), False),
            ("foà".encode("utf-32"), False),
        ]
        for test in tests:
            self.assertEqual(gf.is_utf8_encoded(test[0]), test[1])

    def test_safe_unicode(self):
        tests = [
            ("", ""),
            ("foo", "foo"),
            ("foà", "foà"),
            ("", ""),
            ("foo", "foo"),
            ("foà", "foà"),
        ]
        self.assertIsNone(gf.safe_unicode(None))
        for test in tests:
            self.assertEqual(gf.safe_unicode(test[0]), test[1])

    def test_safe_bytes(self):
        tests = [
            ("", b""),
            ("foo", b"foo"),
            (b"", b""),
            (b"foo", b"foo"),
            (b"fo\x99", b"fo\x99"),
        ]
        self.assertIsNone(gf.safe_bytes(None))
        for test in tests:
            self.assertEqual(gf.safe_bytes(test[0]), test[1])

    def test_safe_unicode_stdin(self):
        # TODO
        pass

    def test_safe_print(self):
        # TODO
        pass
