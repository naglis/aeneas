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

import multiprocessing
import os
import unittest
import tempfile

from aeneas.tools.execute_task import ExecuteTaskCLI
from aeneas.tests.common import BENCH_DIR, bench_test


@bench_test
class TestBenchmarkExecuteTaskCLI(unittest.TestCase):
    def bench_execute(self, parameters, expected_exit_code, timeout):
        args = (parameters, expected_exit_code)
        p = multiprocessing.Process(target=self.execute, name="funcExecute", args=args)
        p.start()
        p.join(timeout)
        if p.is_alive():
            p.terminate()
            p.join()
            self.assertTrue(False)

    def execute(self, parameters, expected_exit_code):
        with tempfile.TemporaryDirectory() as output_path:
            params = ["placeholder"]
            for p_type, p_value in parameters:
                if p_type == "in":
                    params.append(os.path.join(BENCH_DIR, p_value))
                elif p_type == "out":
                    params.append(os.path.join(output_path, p_value))
                else:
                    params.append(p_value)

            exit_code = ExecuteTaskCLI(use_sys=False).run(arguments=params)

        self.assertEqual(exit_code, expected_exit_code)

    def test_rateaggressive_remove_nonspeech(self):
        self.bench_execute(
            [
                ("in", "010m.mp3"),
                ("in", "010m.plain.word.txt"),
                (
                    "",
                    "task_language=eng|is_text_type=plain|os_task_file_format=srt|task_adjust_boundary_algorithm=rateaggressive|task_adjust_boundary_rate_value=14.000|task_adjust_boundary_nonspeech_min=0.500|task_adjust_boundary_nonspeech_string=REMOVE",
                ),
                ("out", "sonnet.srt"),
            ],
            0,
            40,
        )

    def test_rateaggressive_remove_nonspeech_add(self):
        self.bench_execute(
            [
                ("in", "010m.mp3"),
                ("in", "010m.plain.word.txt"),
                (
                    "",
                    "task_language=eng|is_text_type=plain|os_task_file_format=srt|task_adjust_boundary_algorithm=rateaggressive|task_adjust_boundary_rate_value=14.000|task_adjust_boundary_nonspeech_min=0.500|task_adjust_boundary_nonspeech_string=REMOVE|os_task_file_head_tail_format=add",
                ),
                ("out", "sonnet.srt"),
            ],
            0,
            40,
        )

    def test_rateaggressive_remove_nonspeech_smaller_rate(self):
        self.bench_execute(
            [
                ("in", "010m.mp3"),
                ("in", "010m.plain.word.txt"),
                (
                    "",
                    "task_language=eng|is_text_type=plain|os_task_file_format=srt|task_adjust_boundary_algorithm=rateaggressive|task_adjust_boundary_rate_value=12.000|task_adjust_boundary_nonspeech_min=0.500|task_adjust_boundary_nonspeech_string=REMOVE",
                ),
                ("out", "sonnet.srt"),
            ],
            0,
            40,
        )

    def test_rateaggressive_remove_nonspeech_idiotic_rate(self):
        self.bench_execute(
            [
                ("in", "010m.mp3"),
                ("in", "010m.plain.word.txt"),
                (
                    "",
                    "task_language=eng|is_text_type=plain|os_task_file_format=srt|task_adjust_boundary_algorithm=rateaggressive|task_adjust_boundary_rate_value=2.000|task_adjust_boundary_nonspeech_min=0.500|task_adjust_boundary_nonspeech_string=REMOVE",
                ),
                ("out", "sonnet.srt"),
            ],
            0,
            40,
        )

    def test_rateaggressive_remove_nonspeech_nozero(self):
        self.bench_execute(
            [
                ("in", "010m.mp3"),
                ("in", "010m.plain.word.txt"),
                (
                    "",
                    "task_language=eng|is_text_type=plain|os_task_file_format=srt|task_adjust_boundary_algorithm=rateaggressive|task_adjust_boundary_rate_value=14.000|task_adjust_boundary_nonspeech_min=0.500|task_adjust_boundary_nonspeech_string=REMOVE|task_adjust_boundary_no_zero=True",
                ),
                ("out", "sonnet.srt"),
            ],
            0,
            40,
        )

    def test_rateaggressive_nozero(self):
        self.bench_execute(
            [
                ("in", "010m.mp3"),
                ("in", "010m.plain.word.txt"),
                (
                    "",
                    "task_language=eng|is_text_type=plain|os_task_file_format=srt|task_adjust_boundary_algorithm=rateaggressive|task_adjust_boundary_rate_value=14.000|task_adjust_boundary_no_zero=True",
                ),
                ("out", "sonnet.srt"),
            ],
            0,
            40,
        )

    def test_rateaggressive_nozero_add(self):
        self.bench_execute(
            [
                ("in", "010m.mp3"),
                ("in", "010m.plain.word.txt"),
                (
                    "",
                    "task_language=eng|is_text_type=plain|os_task_file_format=srt|task_adjust_boundary_algorithm=rateaggressive|task_adjust_boundary_rate_value=14.000|task_adjust_boundary_no_zero=True|os_task_file_head_tail_format=add",
                ),
                ("out", "sonnet.srt"),
            ],
            0,
            40,
        )

    def test_mplain_rateaggressive_remove_nonspeech(self):
        self.bench_execute(
            [
                ("in", "010m.mp3"),
                ("in", "010m.mplain.txt"),
                (
                    "",
                    "task_language=eng|is_text_type=mplain|os_task_file_format=json|task_adjust_boundary_algorithm=rateaggressive|task_adjust_boundary_rate_value=14.000|task_adjust_boundary_nonspeech_min=0.500|task_adjust_boundary_nonspeech_string=REMOVE",
                ),
                ("out", "out.json"),
            ],
            0,
            200,
        )

    def test_mplain_rateaggressive_remove_nonspeech_add(self):
        self.bench_execute(
            [
                ("in", "010m.mp3"),
                ("in", "010m.mplain.txt"),
                (
                    "",
                    "task_language=eng|is_text_type=mplain|os_task_file_format=json|task_adjust_boundary_algorithm=rateaggressive|task_adjust_boundary_rate_value=14.000|task_adjust_boundary_nonspeech_min=0.500|task_adjust_boundary_nonspeech_string=REMOVE|os_task_file_head_tail_format=add",
                ),
                ("out", "out.json"),
            ],
            0,
            200,
        )

    def test_mplain_rateaggressive_remove_nonspeech_smaller_rate(self):
        self.bench_execute(
            [
                ("in", "010m.mp3"),
                ("in", "010m.mplain.txt"),
                (
                    "",
                    "task_language=eng|is_text_type=mplain|os_task_file_format=json|task_adjust_boundary_algorithm=rateaggressive|task_adjust_boundary_rate_value=12.000|task_adjust_boundary_nonspeech_min=0.500|task_adjust_boundary_nonspeech_string=REMOVE",
                ),
                ("out", "out.json"),
            ],
            0,
            200,
        )

    def test_mplain_rateaggressive_remove_nonspeech_idiotic_rate(self):
        self.bench_execute(
            [
                ("in", "010m.mp3"),
                ("in", "010m.mplain.txt"),
                (
                    "",
                    "task_language=eng|is_text_type=mplain|os_task_file_format=json|task_adjust_boundary_algorithm=rateaggressive|task_adjust_boundary_rate_value=2.000|task_adjust_boundary_nonspeech_min=0.500|task_adjust_boundary_nonspeech_string=REMOVE",
                ),
                ("out", "out.json"),
            ],
            0,
            200,
        )

    def test_mplain_rateaggressive_remove_nonspeech_nozero(self):
        self.bench_execute(
            [
                ("in", "010m.mp3"),
                ("in", "010m.mplain.txt"),
                (
                    "",
                    "task_language=eng|is_text_type=mplain|os_task_file_format=json|task_adjust_boundary_algorithm=rateaggressive|task_adjust_boundary_rate_value=14.000|task_adjust_boundary_nonspeech_min=0.500|task_adjust_boundary_nonspeech_string=REMOVE|task_adjust_boundary_no_zero=True",
                ),
                ("out", "out.json"),
            ],
            0,
            200,
        )

    def test_mplain_rateaggressive_nozero(self):
        self.bench_execute(
            [
                ("in", "010m.mp3"),
                ("in", "010m.mplain.txt"),
                (
                    "",
                    "task_language=eng|is_text_type=mplain|os_task_file_format=json|task_adjust_boundary_algorithm=rateaggressive|task_adjust_boundary_rate_value=14.000|task_adjust_boundary_no_zero=True",
                ),
                ("out", "out.json"),
            ],
            0,
            200,
        )

    def test_mplain_rateaggressive_nozero_add(self):
        self.bench_execute(
            [
                ("in", "010m.mp3"),
                ("in", "010m.mplain.txt"),
                (
                    "",
                    "task_language=eng|is_text_type=mplain|os_task_file_format=json|task_adjust_boundary_algorithm=rateaggressive|task_adjust_boundary_rate_value=14.000|task_adjust_boundary_no_zero=True|os_task_file_head_tail_format=add",
                ),
                ("out", "out.json"),
            ],
            0,
            200,
        )
