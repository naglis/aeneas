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


from aeneas.tests.common import ExecuteTaskCLICase, slow_test


@slow_test
class TestExecuteTaskCLI(ExecuteTaskCLICase):
    def test_exec_faster_rate(self):
        self.execute(
            [
                ("in", "../tools/res/audio.mp3"),
                ("in", "../tools/res/subtitles.txt"),
                (
                    "",
                    "task_language=eng|is_text_type=subtitles|os_task_file_format=srt|task_adjust_boundary_algorithm=rate|task_adjust_boundary_rate_value=12.000",
                ),
                ("out", "sonnet.srt"),
                ("", "--faster-rate"),
            ],
            0,
        )

    def test_exec_keep_audio(self):
        self.execute(
            [
                ("in", "../tools/res/audio.mp3"),
                ("in", "../tools/res/subtitles.txt"),
                (
                    "",
                    "task_language=eng|is_text_type=subtitles|os_task_file_format=srt",
                ),
                ("out", "sonnet.srt"),
                ("", "--keep-audio"),
            ],
            0,
        )

    def test_exec_output_html(self):
        self.execute(
            [
                ("in", "../tools/res/audio.mp3"),
                ("in", "../tools/res/subtitles.txt"),
                (
                    "",
                    "task_language=eng|is_text_type=subtitles|os_task_file_format=srt",
                ),
                ("out", "sonnet.srt"),
                ("", "--output-html"),
            ],
            0,
        )

    def test_exec_presets_word(self):
        self.execute(
            [
                ("in", "../tools/res/audio.mp3"),
                ("in", "../tools/res/words.txt"),
                ("", "task_language=eng|is_text_type=plain|os_task_file_format=json"),
                ("out", "sonnet.json"),
                ("", "--presets-word"),
            ],
            0,
        )

    def test_exec_rate(self):
        self.execute(
            [
                ("in", "../tools/res/audio.mp3"),
                ("in", "../tools/res/subtitles.txt"),
                (
                    "",
                    "task_language=eng|is_text_type=subtitles|os_task_file_format=srt|task_adjust_boundary_algorithm=rate|task_adjust_boundary_rate_value=12.000",
                ),
                ("out", "sonnet.srt"),
                ("", "--rate"),
            ],
            0,
        )

    def test_exec_skip_validator(self):
        self.execute(
            [
                ("in", "../tools/res/audio.mp3"),
                ("in", "../tools/res/subtitles.txt"),
                (
                    "",
                    "task_language=eng|is_text_type=subtitles|os_task_file_format=srt",
                ),
                ("out", "sonnet.srt"),
                ("", "--skip-validator"),
            ],
            0,
        )

    def test_exec_zero(self):
        self.execute(
            [
                ("in", "../tools/res/audio.mp3"),
                ("in", "../tools/res/subtitles.txt"),
                (
                    "",
                    "task_language=eng|is_text_type=subtitles|os_task_file_format=srt",
                ),
                ("out", "sonnet.srt"),
                ("", "--zero"),
            ],
            0,
        )

    # NOTE disabling these ones as they require a network connection
    def zzz_test_exec_youtube(self):
        self.execute(
            [
                ("", "https://www.youtube.com/watch?v=rU4a7AA8wM0"),
                ("in", "../tools/res/plain.txt"),
                ("", "task_language=eng|is_text_type=plain|os_task_file_format=txt"),
                ("out", "sonnet.txt"),
                ("", "-y"),
            ],
            0,
        )

    def zzz_test_exec_youtube_largest_audio(self):
        self.execute(
            [
                ("", "https://www.youtube.com/watch?v=rU4a7AA8wM0"),
                ("in", "../tools/res/plain.txt"),
                ("", "task_language=eng|is_text_type=plain|os_task_file_format=txt"),
                ("out", "sonnet.txt"),
                ("", "-y"),
                ("", "--largest-audio"),
            ],
            0,
        )
