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

import tempfile

from aeneas.tests.common import ExecuteJobCLICase, slow_test, extra_test


@slow_test
class TestExecuteJobCLI(ExecuteJobCLICase):
    def test_exec_aba_no_zero_duration(self):
        self.execute(
            [
                ("in", "../tools/res/job.zip"),
                ("out", ""),
                ("", '-r="aba_no_zero_duration=0.005"'),
            ],
            0,
        )

    def test_exec_aba_nonspeech_tolerance(self):
        self.execute(
            [
                ("in", "../tools/res/job.zip"),
                ("out", ""),
                ("", '-r="aba_nonspeech_tolerance=0.040"'),
            ],
            0,
        )

    def test_exec_allow_unlisted_language(self):
        self.execute(
            [
                ("in", "../tools/res/job.zip"),
                ("out", ""),
                ("", '-r="allow_unlisted_languages=True"'),
            ],
            0,
        )

    def test_exec_c_extensions(self):
        self.execute(
            [
                ("in", "../tools/res/job.zip"),
                ("out", ""),
                ("", '-r="c_extensions=False"'),
            ],
            0,
        )

    def test_exec_cdtw(self):
        self.execute(
            [("in", "../tools/res/job.zip"), ("out", ""), ("", '-r="cdtw=False"')], 0
        )

    def test_exec_cengw(self):
        self.execute(
            [("in", "../tools/res/job.zip"), ("out", ""), ("", '-r="cengw=False"')], 0
        )

    def test_exec_cew(self):
        self.execute(
            [("in", "../tools/res/job.zip"), ("out", ""), ("", '-r="cew=False"')], 0
        )

    def test_exec_cew_subprocess_enabled(self):
        self.execute(
            [
                ("in", "../tools/res/job.zip"),
                ("out", ""),
                ("", '-r="cew_subprocess_enabled=True"'),
            ],
            0,
        )

    def test_exec_cew_subprocess_path(self):
        self.execute(
            [
                ("in", "../tools/res/job.zip"),
                ("out", ""),
                ("", '-r="cew_subprocess_enabled=True|cew_subprocess_path=python"'),
            ],
            0,
        )

    @extra_test
    def test_exec_cfw(self):
        self.execute(
            [
                ("in", "../tools/res/job.zip"),
                ("out", ""),
                ("", '-r="cfw=False|tts=festival"'),
            ],
            0,
        )

    def test_exec_cmfcc(self):
        self.execute(
            [("in", "../tools/res/job.zip"), ("out", ""), ("", '-r="cmfcc=False"')], 0
        )

    def test_exec_dtw_algorithm(self):
        self.execute(
            [
                ("in", "../tools/res/job.zip"),
                ("out", ""),
                ("", '-r="dtw_algorithm=exact"'),
            ],
            0,
        )

    def test_exec_dtw_margin(self):
        self.execute(
            [("in", "../tools/res/job.zip"), ("out", ""), ("", '-r="dtw_margin=100"')],
            0,
        )

    def test_exec_ffmpeg_sample_rate(self):
        self.execute(
            [
                ("in", "../tools/res/job.zip"),
                ("out", ""),
                ("", '-r="ffmpeg_sample_rate=22050"'),
            ],
            0,
        )

    def test_exec_mfcc_emphasis_factor(self):
        self.execute(
            [
                ("in", "../tools/res/job.zip"),
                ("out", ""),
                ("", '-r="mfcc_emphasis_factor=0.95"'),
            ],
            0,
        )

    def test_exec_mfcc_fft_order(self):
        self.execute(
            [
                ("in", "../tools/res/job.zip"),
                ("out", ""),
                ("", '-r="mfcc_fft_order=256"'),
            ],
            0,
        )

    def test_exec_mfcc_filters(self):
        self.execute(
            [("in", "../tools/res/job.zip"), ("out", ""), ("", '-r="mfcc_filters=32"')],
            0,
        )

    def test_exec_mfcc_lower_frequency(self):
        self.execute(
            [
                ("in", "../tools/res/job.zip"),
                ("out", ""),
                ("", '-r="mfcc_lower_frequency=100"'),
            ],
            0,
        )

    def test_exec_mfcc_size(self):
        self.execute(
            [("in", "../tools/res/job.zip"), ("out", ""), ("", '-r="mfcc_size=16"')], 0
        )

    def test_exec_mfcc_upper_frequency(self):
        self.execute(
            [
                ("in", "../tools/res/job.zip"),
                ("out", ""),
                ("", '-r="mfcc_upper_frequency=5000"'),
            ],
            0,
        )

    def test_exec_mfcc_window_length(self):
        self.execute(
            [
                ("in", "../tools/res/job.zip"),
                ("out", ""),
                ("", '-r="mfcc_window_length=0.200"'),
            ],
            0,
        )

    def test_exec_mfcc_window_shift(self):
        self.execute(
            [
                ("in", "../tools/res/job.zip"),
                ("out", ""),
                ("", '-r="mfcc_window_shift=0.050"'),
            ],
            0,
        )

    def test_exec_mfcc_mask_nonspeech(self):
        self.execute(
            [
                ("in", "../tools/res/job.zip"),
                ("out", ""),
                ("", '-r="mfcc_mask_nonspeech=True"'),
            ],
            0,
        )

    def test_exec_mfcc_mask_extend_speech_after(self):
        self.execute(
            [
                ("in", "../tools/res/job.zip"),
                ("out", ""),
                ("", '-r="mfcc_mask_nonspeech=True|mfcc_mask_extend_speech_after=1"'),
            ],
            0,
        )

    def test_exec_mfcc_mask_extend_speech_before(self):
        self.execute(
            [
                ("in", "../tools/res/job.zip"),
                ("out", ""),
                ("", '-r="mfcc_mask_nonspeech=True|mfcc_mask_extend_speech_before=1"'),
            ],
            0,
        )

    def test_exec_mfcc_mask_log_energy_threshold(self):
        self.execute(
            [
                ("in", "../tools/res/job.zip"),
                ("out", ""),
                (
                    "",
                    '-r="mfcc_mask_nonspeech=True|mfcc_mask_log_energy_threshold=0.750"',
                ),
            ],
            0,
        )

    def test_exec_mfcc_mask_min_nonspeech_length(self):
        self.execute(
            [
                ("in", "../tools/res/job.zip"),
                ("out", ""),
                ("", '-r="mfcc_mask_nonspeech=True|mfcc_mask_min_nonspeech_length=2"'),
            ],
            0,
        )

    def test_exec_safety_checks(self):
        self.execute(
            [
                ("in", "../tools/res/job.zip"),
                ("out", ""),
                ("", '-r="safety_checks=False"'),
            ],
            0,
        )

    def test_exec_tmp_path(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            self.execute(
                [
                    ("in", "../tools/res/job.zip"),
                    ("out", ""),
                    ("", '-r="tmp_path=%s"' % tmp_dir),
                ],
                0,
            )

    @extra_test
    def test_exec_tts(self):
        self.execute(
            [("in", "../tools/res/job.zip"), ("out", ""), ("", '-r="tts=festival"')], 0
        )

    @extra_test
    def test_exec_tts_cache(self):
        self.execute(
            [
                ("in", "../tools/res/job.zip"),
                ("out", ""),
                ("", '-r="tts=festival|tts_cache=True"'),
            ],
            0,
        )

    def test_exec_voice_code(self):
        self.execute(
            [
                ("in", "../tools/res/job.zip"),
                ("out", ""),
                ("", '-r="tts_voice_code=it"'),
            ],
            0,
        )

    def test_exec_vad_extend_speech_after(self):
        self.execute(
            [
                ("in", "../tools/res/job.zip"),
                ("out", ""),
                ("", '-r="vad_extend_speech_after=0.100"'),
            ],
            0,
        )

    def test_exec_vad_extend_speech_before(self):
        self.execute(
            [
                ("in", "../tools/res/job.zip"),
                ("out", ""),
                ("", '-r="vad_extend_speech_before=0.100"'),
            ],
            0,
        )

    def test_exec_vad_log_energy_threshold(self):
        self.execute(
            [
                ("in", "../tools/res/job.zip"),
                ("out", ""),
                ("", '-r="vad_log_energy_threshold=0.750"'),
            ],
            0,
        )

    def test_exec_vad_min_nonspeech_length(self):
        self.execute(
            [
                ("in", "../tools/res/job.zip"),
                ("out", ""),
                ("", '-r="vad_min_nonspeech_length=0.500"'),
            ],
            0,
        )
