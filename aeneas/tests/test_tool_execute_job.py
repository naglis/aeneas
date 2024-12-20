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


from aeneas.tests.common import ExecuteJobCLICase


class TestExecuteJobCLI(ExecuteJobCLICase):
    def test_help(self):
        self.execute([], 2)
        self.execute([("", "-h")], 2)
        self.execute([("", "--help")], 2)
        self.execute([("", "--help-rconf")], 2)
        self.execute([("", "--version")], 2)

    def test_exec_container_too_many_jobs(self):
        self.execute(
            [("in", "../tools/res/job.zip"), ("out", ""), ("", '-r="job_max_tasks=1"')],
            1,
        )

    def test_exec_container_bad_1(self):
        self.execute([("in", "../tools/res/job_no_config.zip"), ("out", "")], 1)

    def test_exec_container_bad_2(self):
        self.execute([("in", "../tools/res/job.bad.zip"), ("out", "")], 1)

    def test_exec_container_skip_validator_2(self):
        self.execute(
            [
                ("in", "../tools/res/job_no_config.zip"),
                ("out", ""),
                ("", "--skip-validator"),
            ],
            1,
        )

    def test_exec_missing_1(self):
        self.execute([("in", "../tools/res/job.zip")], 2)

    def test_exec_missing_2(self):
        self.execute([("out", "")], 2)

    def test_exec_cannot_read(self):
        self.execute([("in", "/foo/bar/baz"), ("out", "")], 1)

    def test_exec_cannot_write(self):
        self.execute([("in", "../tools/res/job.zip"), ("", "/foo/bar/baz.txt")], 1)
