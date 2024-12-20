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

from aeneas.tests.common import ExecuteTaskCLICase, slow_test, extra_test


@slow_test
class TestExecuteTaskCLI(ExecuteTaskCLICase):
    def test_exec_tts_no_cache_empty_fragments(self):
        self.execute(
            [
                ("in", "../tools/res/audio.mp3"),
                ("in", "../tests/res/inputtext/plain_with_empty_lines.txt"),
                ("", "task_language=eng|is_text_type=plain|os_task_file_format=json"),
                ("out", "sonnet.json"),
                ("", '-r="tts_cache=False"'),
            ],
            0,
        )

    def test_exec_tts_cache_empty_fragments(self):
        self.execute(
            [
                ("in", "../tools/res/audio.mp3"),
                ("in", "../tests/res/inputtext/plain_with_empty_lines.txt"),
                ("", "task_language=eng|is_text_type=plain|os_task_file_format=json"),
                ("out", "sonnet.json"),
                ("", '-r="tts_cache=True"'),
            ],
            0,
        )

    def test_exec_tts_cache_empty_fragments_pure(self):
        self.execute(
            [
                ("in", "../tools/res/audio.mp3"),
                ("in", "../tests/res/inputtext/plain_with_empty_lines.txt"),
                ("", "task_language=eng|is_text_type=plain|os_task_file_format=json"),
                ("out", "sonnet.json"),
                ("", '-r="tts_cache=True|cew=False"'),
            ],
            0,
        )

    @extra_test
    def test_exec_tts_cache_empty_fragments_festival(self):
        self.execute(
            [
                ("in", "../tools/res/audio.mp3"),
                ("in", "../tests/res/inputtext/plain_with_empty_lines.txt"),
                ("", "task_language=eng|is_text_type=plain|os_task_file_format=json"),
                ("out", "sonnet.json"),
                ("", '-r="tts=festival|tts_cache=True|cfw=True"'),
            ],
            0,
        )

    @extra_test
    def test_exec_tts_cache_empty_fragments_festival_pure(self):
        self.execute(
            [
                ("in", "../tools/res/audio.mp3"),
                ("in", "../tests/res/inputtext/plain_with_empty_lines.txt"),
                ("", "task_language=eng|is_text_type=plain|os_task_file_format=json"),
                ("out", "sonnet.json"),
                ("", '-r="tts=festival|tts_cache=True|cfw=False"'),
            ],
            0,
        )

    def test_exec_rateaggressive_remove_nonspeech(self):
        self.execute(
            [
                ("in", "../tools/res/audio.mp3"),
                ("in", "../tools/res/subtitles.txt"),
                (
                    "",
                    "task_language=eng|is_text_type=subtitles|os_task_file_format=srt|task_adjust_boundary_algorithm=rateaggressive|task_adjust_boundary_rate_value=14.000|task_adjust_boundary_nonspeech_min=0.500|task_adjust_boundary_nonspeech_string=REMOVE",
                ),
                ("out", "sonnet.srt"),
            ],
            0,
        )

    def test_exec_rateaggressive_remove_nonspeech_add(self):
        self.execute(
            [
                ("in", "../tools/res/audio.mp3"),
                ("in", "../tools/res/subtitles.txt"),
                (
                    "",
                    "task_language=eng|is_text_type=subtitles|os_task_file_format=srt|task_adjust_boundary_algorithm=rateaggressive|task_adjust_boundary_rate_value=14.000|task_adjust_boundary_nonspeech_min=0.500|task_adjust_boundary_nonspeech_string=REMOVE|os_task_file_head_tail_format=add",
                ),
                ("out", "sonnet.srt"),
            ],
            0,
        )

    def test_exec_rateaggressive_remove_nonspeech_smaller_rate(self):
        self.execute(
            [
                ("in", "../tools/res/audio.mp3"),
                ("in", "../tools/res/subtitles.txt"),
                (
                    "",
                    "task_language=eng|is_text_type=subtitles|os_task_file_format=srt|task_adjust_boundary_algorithm=rateaggressive|task_adjust_boundary_rate_value=12.000|task_adjust_boundary_nonspeech_min=0.500|task_adjust_boundary_nonspeech_string=REMOVE",
                ),
                ("out", "sonnet.srt"),
            ],
            0,
        )

    def test_exec_rateaggressive_remove_nonspeech_idiotic_rate(self):
        self.execute(
            [
                ("in", "../tools/res/audio.mp3"),
                ("in", "../tools/res/subtitles.txt"),
                (
                    "",
                    "task_language=eng|is_text_type=subtitles|os_task_file_format=srt|task_adjust_boundary_algorithm=rateaggressive|task_adjust_boundary_rate_value=2.000|task_adjust_boundary_nonspeech_min=0.500|task_adjust_boundary_nonspeech_string=REMOVE",
                ),
                ("out", "sonnet.srt"),
            ],
            0,
        )

    def test_exec_rateaggressive_remove_nonspeech_nozero(self):
        self.execute(
            [
                ("in", "../tools/res/audio.mp3"),
                ("in", "../tools/res/subtitles.txt"),
                (
                    "",
                    "task_language=eng|is_text_type=subtitles|os_task_file_format=srt|task_adjust_boundary_algorithm=rateaggressive|task_adjust_boundary_rate_value=14.000|task_adjust_boundary_nonspeech_min=0.500|task_adjust_boundary_nonspeech_string=REMOVE|task_adjust_boundary_no_zero=True",
                ),
                ("out", "sonnet.srt"),
            ],
            0,
        )

    def test_exec_rateaggressive_nozero(self):
        self.execute(
            [
                ("in", "../tools/res/audio.mp3"),
                ("in", "../tools/res/subtitles.txt"),
                (
                    "",
                    "task_language=eng|is_text_type=subtitles|os_task_file_format=srt|task_adjust_boundary_algorithm=rateaggressive|task_adjust_boundary_rate_value=14.000|task_adjust_boundary_no_zero=True",
                ),
                ("out", "sonnet.srt"),
            ],
            0,
        )

    def test_exec_rateaggressive_nozero_add(self):
        self.execute(
            [
                ("in", "../tools/res/audio.mp3"),
                ("in", "../tools/res/subtitles.txt"),
                (
                    "",
                    "task_language=eng|is_text_type=subtitles|os_task_file_format=srt|task_adjust_boundary_algorithm=rateaggressive|task_adjust_boundary_rate_value=14.000|task_adjust_boundary_no_zero=True|os_task_file_head_tail_format=add",
                ),
                ("out", "sonnet.srt"),
            ],
            0,
        )

    def test_exec_mplain_rateaggressive_remove_nonspeech(self):
        self.execute(
            [
                ("in", "../tools/res/audio.mp3"),
                ("in", "../tools/res/mplain.txt"),
                (
                    "",
                    "task_language=eng|is_text_type=mplain|os_task_file_format=json|task_adjust_boundary_algorithm=rateaggressive|task_adjust_boundary_rate_value=14.000|task_adjust_boundary_nonspeech_min=0.500|task_adjust_boundary_nonspeech_string=REMOVE",
                ),
                ("out", "sonnet.json"),
            ],
            0,
        )

    def test_exec_mplain_rateaggressive_remove_nonspeech_add(self):
        self.execute(
            [
                ("in", "../tools/res/audio.mp3"),
                ("in", "../tools/res/mplain.txt"),
                (
                    "",
                    "task_language=eng|is_text_type=mplain|os_task_file_format=json|task_adjust_boundary_algorithm=rateaggressive|task_adjust_boundary_rate_value=14.000|task_adjust_boundary_nonspeech_min=0.500|task_adjust_boundary_nonspeech_string=REMOVE|os_task_file_head_tail_format=add",
                ),
                ("out", "sonnet.json"),
            ],
            0,
        )

    def test_exec_mplain_rateaggressive_remove_nonspeech_smaller_rate(self):
        self.execute(
            [
                ("in", "../tools/res/audio.mp3"),
                ("in", "../tools/res/mplain.txt"),
                (
                    "",
                    "task_language=eng|is_text_type=mplain|os_task_file_format=json|task_adjust_boundary_algorithm=rateaggressive|task_adjust_boundary_rate_value=12.000|task_adjust_boundary_nonspeech_min=0.500|task_adjust_boundary_nonspeech_string=REMOVE",
                ),
                ("out", "sonnet.json"),
            ],
            0,
        )

    def test_exec_mplain_rateaggressive_remove_nonspeech_idiotic_rate(self):
        self.execute(
            [
                ("in", "../tools/res/audio.mp3"),
                ("in", "../tools/res/mplain.txt"),
                (
                    "",
                    "task_language=eng|is_text_type=mplain|os_task_file_format=json|task_adjust_boundary_algorithm=rateaggressive|task_adjust_boundary_rate_value=2.000|task_adjust_boundary_nonspeech_min=0.500|task_adjust_boundary_nonspeech_string=REMOVE",
                ),
                ("out", "sonnet.json"),
            ],
            0,
        )

    def test_exec_mplain_rateaggressive_remove_nonspeech_nozero(self):
        self.execute(
            [
                ("in", "../tools/res/audio.mp3"),
                ("in", "../tools/res/mplain.txt"),
                (
                    "",
                    "task_language=eng|is_text_type=mplain|os_task_file_format=json|task_adjust_boundary_algorithm=rateaggressive|task_adjust_boundary_rate_value=14.000|task_adjust_boundary_nonspeech_min=0.500|task_adjust_boundary_nonspeech_string=REMOVE|task_adjust_boundary_no_zero=True",
                ),
                ("out", "sonnet.json"),
            ],
            0,
        )

    def test_exec_mplain_rateaggressive_nozero(self):
        self.execute(
            [
                ("in", "../tools/res/audio.mp3"),
                ("in", "../tools/res/mplain.txt"),
                (
                    "",
                    "task_language=eng|is_text_type=mplain|os_task_file_format=json|task_adjust_boundary_algorithm=rateaggressive|task_adjust_boundary_rate_value=14.000|task_adjust_boundary_no_zero=True",
                ),
                ("out", "sonnet.json"),
            ],
            0,
        )

    def test_exec_mplain_rateaggressive_nozero_add(self):
        self.execute(
            [
                ("in", "../tools/res/audio.mp3"),
                ("in", "../tools/res/mplain.txt"),
                (
                    "",
                    "task_language=eng|is_text_type=mplain|os_task_file_format=json|task_adjust_boundary_algorithm=rateaggressive|task_adjust_boundary_rate_value=14.000|task_adjust_boundary_no_zero=True|os_task_file_head_tail_format=add",
                ),
                ("out", "sonnet.json"),
            ],
            0,
        )
