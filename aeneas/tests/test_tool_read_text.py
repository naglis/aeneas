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


from aeneas.tests.common import ExecuteCLICase
from aeneas.tools.read_text import ReadTextCLI


class TestReadTextCLI(ExecuteCLICase):
    CLI_CLS = ReadTextCLI

    def test_help(self):
        self.execute([], 2)
        self.execute([("", "-h")], 2)
        self.execute([("", "--help")], 2)
        self.execute([("", "--help-rconf")], 2)
        self.execute([("", "--version")], 2)

    def test_read_list(self):
        self.execute(
            [("", "list"), ("", "From|fairest|creatures|we|desire|increase")], 0
        )

    def test_read_parsed(self):
        self.execute([("", "parsed"), ("in", "../tools/res/parsed.txt")], 0)

    def test_read_plain(self):
        self.execute([("", "plain"), ("in", "../tools/res/plain.txt")], 0)

    def test_read_subtitles(self):
        self.execute([("", "subtitles"), ("in", "../tools/res/subtitles.txt")], 0)

    def test_read_subtitles_id_format(self):
        self.execute(
            [
                ("", "subtitles"),
                ("in", "../tools/res/subtitles.txt"),
                ("", "--id-format=Sub%03d"),
            ],
            0,
        )

    def test_read_unparsed_id_regex(self):
        self.execute(
            [
                ("", "unparsed"),
                ("in", "../tools/res/unparsed.xhtml"),
                ("", "--id-regex=f[0-9]*"),
            ],
            0,
        )

    def test_read_unparsed_class_regex(self):
        self.execute(
            [
                ("", "unparsed"),
                ("in", "../tools/res/unparsed.xhtml"),
                ("", "--class-regex=ra"),
                ("", "--sort=unsorted"),
            ],
            0,
        )

    def test_read_unparsed_sort_numeric(self):
        self.execute(
            [
                ("", "unparsed"),
                ("in", "../tools/res/unparsed.xhtml"),
                ("", "--id-regex=f[0-9]*"),
                ("", "--sort=numeric"),
            ],
            0,
        )

    def test_read_unparsed_sort_lexicographic(self):
        self.execute(
            [
                ("", "unparsed"),
                ("in", "../tools/res/unparsed.xhtml"),
                ("", "--id-regex=f[0-9]*"),
                ("", "--sort=lexicographic"),
            ],
            0,
        )

    def test_read_missing_1(self):
        self.execute([("", "list")], 2)

    def test_read_missing_2(self):
        self.execute([("", "From|fairest|creatures|we|desire|increase")], 2)

    def test_read_cannot_read(self):
        self.execute([("", "plain"), ("", "/foo/bar/baz.wav")], 1)

    def test_read_unparsed_missing(self):
        self.execute([("", "unparsed"), ("in", "../tools/res/unparsed.xhtml")], 1)
