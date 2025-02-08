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

    def test_file_extension_None(self):
        self.assertIsNone(gf.file_extension(None))

    def test_file_extension(self):
        for path, expected in (
            ("", ""),
            ("/", ""),
            ("/foo", ""),
            ("/foo.", ""),
            ("/.foo", ""),
            ("/foo.bar", "bar"),
            ("/foo/bar/foo.baz", "baz"),
            ("/foo/bar/baz", ""),
            ("/foo/bar/.baz", ""),
            ("foo", ""),
            ("foo.", ""),
            (".foo", ""),
            ("foo.bar", "bar"),
            ("foo/bar/foo.baz", "baz"),
            ("foo/bar/baz", ""),
            ("foo/bar/.baz", ""),
        ):
            with self.subTest(path=path, expected=expected):
                self.assertEqual(gf.file_extension(path), expected)

    def test_file_name_without_extension_None(self):
        self.assertIsNone(gf.file_name_without_extension(None))

    def test_file_name_without_extension(self):
        for path, expected in (
            ("", ""),
            ("/", ""),
            ("/foo", "foo"),
            ("/foo.", "foo"),
            ("/.foo", ".foo"),
            ("/foo.bar", "foo"),
            ("/foo/bar/foo.baz", "foo"),
            ("/foo/bar/baz", "baz"),
            ("/foo/bar/.baz", ".baz"),
            ("foo", "foo"),
            ("foo.", "foo"),
            (".foo", ".foo"),
            ("foo.bar", "foo"),
            ("foo/bar/foo.baz", "foo"),
            ("foo/bar/baz", "baz"),
            ("foo/bar/.baz", ".baz"),
        ):
            with self.subTest(path=path, expected=expected):
                self.assertEqual(gf.file_name_without_extension(path), expected)

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

    def test_norm_join(self):
        for prefix, suffix, expected in (
            (None, None, "."),
            (None, "", "."),
            (None, "/foo", "/foo"),
            (None, "/foo.bar", "/foo.bar"),
            (None, "/foo/../bar", "/bar"),
            (None, "/foo/./bar", "/foo/bar"),
            (None, "/foo/bar/baz", "/foo/bar/baz"),
            (None, "/foo/bar/../../baz", "/baz"),
            (None, "/foo/bar/./baz", "/foo/bar/baz"),
            ("", None, "."),
            ("/foo", None, "/foo"),
            ("/foo.bar", None, "/foo.bar"),
            ("/foo/../bar", None, "/bar"),
            ("/foo/./bar", None, "/foo/bar"),
            ("/foo/bar/baz", None, "/foo/bar/baz"),
            ("/foo/bar/../../baz", None, "/baz"),
            ("/foo/bar/./baz", None, "/foo/bar/baz"),
            ("", "", "."),
            ("/", "", "/"),
            ("", "/", "/"),
            ("/", "/", "/"),
            ("/foo", "bar", "/foo/bar"),
            ("/foo", "bar/foo.baz", "/foo/bar/foo.baz"),
            ("/foo", "bar/../foo.baz", "/foo/foo.baz"),
            ("/foo", "bar/../../foo.baz", "/foo.baz"),
            ("/foo", "bar.baz", "/foo/bar.baz"),
            ("/foo/../", "bar.baz", "/bar.baz"),
            ("/foo/", "../bar.baz", "/bar.baz"),
            ("/foo/./", "bar.baz", "/foo/bar.baz"),
            ("/foo/", "./bar.baz", "/foo/bar.baz"),
            ("foo", "bar", "foo/bar"),
            ("foo", "bar/foo.baz", "foo/bar/foo.baz"),
            ("foo", "bar/../foo.baz", "foo/foo.baz"),
            ("foo", "bar/../../foo.baz", "foo.baz"),
            ("foo", "bar.baz", "foo/bar.baz"),
            ("foo/../", "bar.baz", "bar.baz"),
            ("foo/", "../bar.baz", "bar.baz"),
            ("foo/./", "bar.baz", "foo/bar.baz"),
            ("foo/", "./bar.baz", "foo/bar.baz"),
        ):
            with self.subTest(prefix=prefix, suffix=suffix, expected=expected):
                self.assertEqual(gf.norm_join(prefix, suffix), expected)

    def test_config_txt_None_to_string(self):
        self.assertIsNone(gf.config_txt_to_string(None))

    def test_config_txt_to_string(self):
        for txt, expected in (
            ("", ""),
            ("k1=v1", "k1=v1"),
            ("k1=v1\n\n", "k1=v1"),
            ("k1=v1\nk2=v2", "k1=v1|k2=v2"),
            ("k1=v1\nk2=v2\n\n\nk3=v3\n", "k1=v1|k2=v2|k3=v3"),
            (" k1=v1\n k2=v2 \n\n\nk3=v3 \n", "k1=v1|k2=v2|k3=v3"),
            ("k1=v1\nk2\nk3=v3", "k1=v1|k2|k3=v3"),
        ):
            with self.subTest(txt=txt, expected=expected):
                self.assertEqual(gf.config_txt_to_string(txt), expected)

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

    def test_config_xml_to_dict_job(self):
        for xml, expected in (
            (None, {}),
            ("", {}),
            ("<job></job>", {}),
            ("<job><k1>v1</k1></job>", {"k1": "v1"}),
            ("<job><k1>v1</k1><k2></k2></job>", {"k1": "v1"}),
            ("<job><k1>v1</k1><k2>  </k2></job>", {"k1": "v1"}),
            ("<job><k1>v1</k1><k2>v2</k2></job>", {"k1": "v1", "k2": "v2"}),
            ("<job><k1>v1</k1><k2> v2</k2></job>", {"k1": "v1", "k2": "v2"}),
            ("<job><k1>v1</k1><k2> v2 </k2></job>", {"k1": "v1", "k2": "v2"}),
            ("<job><k1>v1</k1><k2>v2 </k2></job>", {"k1": "v1", "k2": "v2"}),
        ):
            with self.subTest(xml=xml, expected=expected):
                self.assertEqual(
                    gf.config_xml_to_dict(xml, result=None, parse_job=True), expected
                )

    def test_config_xml_to_dict_task(self):
        for xml, expected in (
            (None, []),
            ("", []),
            ("<job></job>", []),
            ("<job><k1>v1</k1></job>", []),
            ("<job><k1>v1</k1><k2></k2></job>", []),
            ("<job><tasks></tasks></job>", []),
            ("<job><tasks><foo></foo></tasks></job>", []),
            ("<job><tasks><task></task></tasks></job>", [{}]),
            ("<job><tasks><task></task><foo></foo></tasks></job>", [{}]),
            (
                "<job><tasks><task></task><foo></foo><task></task></tasks></job>",
                [{}, {}],
            ),
            ("<job><tasks><task><k1></k1></task><foo></foo></tasks></job>", [{}]),
            ("<job><tasks><task><k1>v1</k1></task></tasks></job>", [{"k1": "v1"}]),
            (
                "<job><tasks><task><k1>v1</k1><k2>v2</k2></task></tasks></job>",
                [{"k1": "v1", "k2": "v2"}],
            ),
            (
                "<job><tasks><task><k1>v1</k1><k2> v2</k2></task></tasks></job>",
                [{"k1": "v1", "k2": "v2"}],
            ),
            (
                "<job><tasks><task><k1>v1</k1><k2> v2 </k2></task></tasks></job>",
                [{"k1": "v1", "k2": "v2"}],
            ),
            (
                "<job><tasks><task><k1>v1</k1><k2>v2 </k2></task></tasks></job>",
                [{"k1": "v1", "k2": "v2"}],
            ),
            (
                "<job><tasks><task><k1>v1</k1></task><task><k2>v2</k2></task></tasks></job>",
                [{"k1": "v1"}, {"k2": "v2"}],
            ),
            (
                "<job><tasks><task><k1>v1</k1></task><task><k2>v2</k2></task><task></task></tasks></job>",
                [{"k1": "v1"}, {"k2": "v2"}, {}],
            ),
        ):
            with self.subTest(xml=xml, expected=expected):
                self.assertEqual(
                    gf.config_xml_to_dict(xml, result=None, parse_job=False), expected
                )

    def test_config_dict_to_string(self):
        self.assertEqual(gf.config_dict_to_string({}), "")
        self.assertEqual(gf.config_dict_to_string({"k1": "v1"}), "k1=v1")
        self.assertEqual(
            gf.config_dict_to_string({"k1": "v1", "k2": "v2"}), "k1=v1|k2=v2"
        )

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

    def test_split_url(self):
        for url, expected in (
            (None, (None, None)),
            ("", ("", None)),
            ("foo", ("foo", None)),
            ("foo.html", ("foo.html", None)),
            ("foo.html#", ("foo.html", "")),
            ("foo.html#id", ("foo.html", "id")),
            ("foo.html#id#bad", ("foo.html", "id")),
        ):
            with self.subTest(url=url, expected=expected):
                self.assertEqual(gf.split_url(url), expected)

    def test_is_posix(self):
        self.skipTest("TODO")

    def test_is_linux(self):
        self.skipTest("TODO")

    def test_is_osx(self):
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

    def test_file_can_be_written_true(self):
        handler, path = gf.tmp_file()
        self.assertTrue(gf.file_can_be_written(path))
        gf.delete_file(handler, path)

    def test_file_can_be_written_false(self):
        path = "/foo/bar/baz"
        self.assertFalse(gf.file_can_be_written(path))

    def test_file_size_nonzero(self):
        handler, path = gf.tmp_file()
        with open(path, "w", encoding="utf-8") as tmp_file:
            tmp_file.write("Foo bar")
        self.assertEqual(gf.file_size(path), 7)
        gf.delete_file(handler, path)

    def test_file_size_zero(self):
        handler, path = gf.tmp_file()
        self.assertEqual(gf.file_size(path), 0)
        gf.delete_file(handler, path)

    def test_file_size_not_existing(self):
        path = "/foo/bar/baz"
        self.assertEqual(gf.file_size(path), -1)

    def test_delete_directory_existing(self):
        tmp_dir = tempfile.mkdtemp()
        self.assertTrue(os.path.isdir(tmp_dir))
        gf.delete_directory(tmp_dir)
        self.assertFalse(os.path.isdir(tmp_dir))

    def test_delete_directory_not_existing(self):
        orig = "/foo/bar/baz"
        self.assertFalse(os.path.isdir(orig))
        gf.delete_directory(orig)
        self.assertFalse(os.path.isdir(orig))

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

    def test_read_file_bytes(self):
        handler, path = gf.tmp_file()
        with open(path, "w", encoding="utf-8") as tmp_file:
            tmp_file.write("Foo bar")
        contents = gf.read_file_bytes(path)
        self.assertIsInstance(contents, bytes)
        self.assertEqual(len(contents), 7)
        gf.delete_file(handler, path)

    def test_human_readable_number(self):
        tests = [
            (0, "0.0"),
            (0.0, "0.0"),
            (1, "1.0"),
            (1.0, "1.0"),
            (10, "10.0"),
            (100, "100.0"),
            (1000, "1000.0"),
            (2000, "2.0K"),
            (3000, "2.9K"),
            (1000000, "976.6K"),
            (2000000, "1.9M"),
            (3000000, "2.9M"),
        ]
        for test in tests:
            self.assertEqual(gf.human_readable_number(test[0]), test[1])

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
