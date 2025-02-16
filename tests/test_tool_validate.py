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


from aeneas.tools.validate import ValidateCLI

from .common import ExecuteCLICase


class TestValidateCLI(ExecuteCLICase):
    CLI_CLS = ValidateCLI

    def test_help(self):
        self.execute([], 2)
        self.execute([("", "-h")], 2)
        self.execute([("", "--help")], 2)
        self.execute([("", "--help-rconf")], 2)
        self.execute([("", "--version")], 2)

    def test_bad_type(self):
        self.execute([("", "foo"), ("in", "../aeneas/tools/res/config.txt")], 2)

    def test_task(self):
        self.execute(
            [
                ("", "task"),
                (
                    "",
                    "task_language=it|is_text_type=plain|os_task_file_name=output.txt|os_task_file_format=txt",
                ),
            ],
            0,
        )

    def test_task_bad(self):
        self.execute(
            [
                ("", "task"),
                (
                    "",
                    "task_language=it|is_text_type=plain|os_task_file_name=output.txt",
                ),
            ],
            1,
        )

    def test_read_missing_1(self):
        self.execute([("", "config")], 2)

    def test_read_missing_2(self):
        self.execute([("in", "../aeneas/tools/res/config.txt")], 2)

    def test_read_missing_3(self):
        self.execute(
            [
                ("", "job_language=it|invalid=string"),
                ("in", "../aeneas/tools/res/job_no_config.zip"),
            ],
            2,
        )
