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

import unittest

from aeneas.exacttiming import TimeValue
from aeneas.runtimeconfiguration import RuntimeConfiguration


class TestRuntimeConfiguration(unittest.TestCase):
    def test_config_string(self):
        rconf = RuntimeConfiguration()
        rconf.config_string

    def test_safety_checks(self):
        rconf = RuntimeConfiguration()
        self.assertEqual(rconf.safety_checks, True)

    def test_sample_rate(self):
        rconf = RuntimeConfiguration()
        self.assertEqual(rconf.sample_rate, 16000)

    def test_dtw_margin(self):
        rconf = RuntimeConfiguration()
        self.assertEqual(rconf.dtw_margin, TimeValue("60.000"))

    def test_mmn(self):
        rconf = RuntimeConfiguration()
        self.assertEqual(rconf.mmn, False)

    def test_mws(self):
        rconf = RuntimeConfiguration()
        self.assertEqual(rconf.mws, TimeValue("0.040"))

    def test_mwl(self):
        rconf = RuntimeConfiguration()
        self.assertEqual(rconf.mwl, TimeValue("0.100"))

    def test_default_tts(self):
        rconf = RuntimeConfiguration()
        self.assertEqual(rconf.tts, "espeak-ng")

    def test_tts_path(self):
        rconf = RuntimeConfiguration()
        self.assertEqual(rconf.tts_path, None)

    def test_set_granularity(self):
        rconf = RuntimeConfiguration()
        rconf.set_granularity(level=1)
        self.assertEqual(rconf.mmn, False)
        self.assertEqual(rconf.mwl, TimeValue("0.100"))
        self.assertEqual(rconf.mws, TimeValue("0.040"))
        rconf.set_granularity(level=2)
        self.assertEqual(rconf.mmn, False)
        self.assertEqual(rconf.mwl, TimeValue("0.050"))
        self.assertEqual(rconf.mws, TimeValue("0.020"))
        rconf.set_granularity(level=3)
        self.assertEqual(rconf.mmn, False)
        self.assertEqual(rconf.mwl, TimeValue("0.020"))
        self.assertEqual(rconf.mws, TimeValue("0.005"))

    def test_set_tts(self):
        rconf = RuntimeConfiguration()
        rconf.set_tts(level=1)
        self.assertEqual(rconf.tts, "espeak-ng")
        self.assertEqual(rconf.tts_path, None)
        rconf.set_tts(level=2)
        self.assertEqual(rconf.tts, "espeak-ng")
        self.assertEqual(rconf.tts_path, None)
        rconf.set_tts(level=3)
        self.assertEqual(rconf.tts, "espeak-ng")
        self.assertEqual(rconf.tts_path, None)

    def test_clone(self):
        rconf = RuntimeConfiguration()
        rconf2 = rconf.clone()
        self.assertNotEqual(id(rconf), id(rconf2))
        self.assertEqual(rconf.config_string, rconf2.config_string)

    def test_set_rconf_string(self):
        params = (
            (
                "aba_nonspeech_tolerance=0.040",
                "aba_nonspeech_tolerance",
                TimeValue("0.040"),
            ),
            ("aba_no_zero_duration=0.040", "aba_no_zero_duration", TimeValue("0.040")),
            ("allow_unlisted_languages=True", "allow_unlisted_languages", True),
            ("c_extensions=False", "c_extensions", False),
            ("cdtw=False", "cdtw", False),
            ("cew=False", "cew", False),
            ("cengw=False", "cengw", False),
            ("cmfcc=False", "cmfcc", False),
            ("cew_subprocess_enabled=True", "cew_subprocess_enabled", True),
            (
                "cew_subprocess_path=/foo/bar/python",
                "cew_subprocess_path",
                "/foo/bar/python",
            ),
            ("dtw_algorithm=exact", "dtw_algorithm", "exact"),
            ("dtw_margin=100", "dtw_margin", TimeValue("100")),
            ("ffmpeg_path=/foo/bar/ffmpeg", "ffmpeg_path", "/foo/bar/ffmpeg"),
            ("ffmpeg_sample_rate=8000", "ffmpeg_sample_rate", 8000),
            ("ffprobe_path=/foo/bar/ffprobe", "ffprobe_path", "/foo/bar/ffprobe"),
            ("mfcc_filters=100", "mfcc_filters", 100),
            ("mfcc_size=20", "mfcc_size", 20),
            ("mfcc_fft_order=256", "mfcc_fft_order", 256),
            ("mfcc_lower_frequency=120.0", "mfcc_lower_frequency", 120.0),
            ("mfcc_upper_frequency=5000.0", "mfcc_upper_frequency", 5000.0),
            ("mfcc_emphasis_factor=1.0", "mfcc_emphasis_factor", 1.0),
            ("mfcc_mask_nonspeech=True", "mfcc_mask_nonspeech", True),
            ("mfcc_window_length=0.360", "mfcc_window_length", TimeValue("0.360")),
            ("mfcc_window_shift=0.160", "mfcc_window_shift", TimeValue("0.160")),
            ("dtw_margin_l1=100", "dtw_margin_l1", TimeValue("100")),
            ("mfcc_mask_nonspeech_l1=True", "mfcc_mask_nonspeech_l1", True),
            (
                "mfcc_window_length_l1=0.360",
                "mfcc_window_length_l1",
                TimeValue("0.360"),
            ),
            ("mfcc_window_shift_l1=0.160", "mfcc_window_shift_l1", TimeValue("0.160")),
            ("dtw_margin_l2=30", "dtw_margin_l2", TimeValue("30")),
            ("mfcc_mask_nonspeech_l2=True", "mfcc_mask_nonspeech_l2", True),
            (
                "mfcc_window_length_l2=0.360",
                "mfcc_window_length_l2",
                TimeValue("0.360"),
            ),
            ("mfcc_window_shift_l2=0.160", "mfcc_window_shift_l2", TimeValue("0.160")),
            ("dtw_margin_l3=10", "dtw_margin_l3", TimeValue("10")),
            ("mfcc_mask_nonspeech_l3=True", "mfcc_mask_nonspeech_l3", True),
            (
                "mfcc_window_length_l3=0.360",
                "mfcc_window_length_l3",
                TimeValue("0.360"),
            ),
            ("mfcc_window_shift_l3=0.160", "mfcc_window_shift_l3", TimeValue("0.160")),
            ("mfcc_mask_extend_speech_after=1", "mfcc_mask_extend_speech_after", 1),
            ("mfcc_mask_extend_speech_before=1", "mfcc_mask_extend_speech_before", 1),
            (
                "mfcc_mask_log_energy_threshold=0.750",
                "mfcc_mask_log_energy_threshold",
                0.750,
            ),
            ("mfcc_mask_min_nonspeech_length=5", "mfcc_mask_min_nonspeech_length", 5),
            ("safety_checks=False", "safety_checks", False),
            ("task_max_audio_length=1000", "task_max_audio_length", TimeValue("1000")),
            ("task_max_text_length=1000", "task_max_text_length", 1000),
            ("tmp_path=/foo/bar", "tmp_path", "/foo/bar"),
            ("tts=festival", "tts", "festival"),
            ("tts_path=/foo/bar/festival", "tts_path", "/foo/bar/festival"),
            ("tts_voice_code=ru", "tts_voice_code", "ru"),
            ("tts_cache=True", "tts_cache", True),
            ("tts_l1=festival", "tts_l1", "festival"),
            ("tts_path_l1=/foo/bar/festival", "tts_path_l1", "/foo/bar/festival"),
            ("tts_l2=festival", "tts_l2", "festival"),
            ("tts_path_l2=/foo/bar/festival", "tts_path_l2", "/foo/bar/festival"),
            ("tts_l3=festival", "tts_l3", "festival"),
            ("tts_path_l3=/foo/bar/festival", "tts_path_l3", "/foo/bar/festival"),
            (
                "vad_extend_speech_after=1.000",
                "vad_extend_speech_after",
                TimeValue("1.000"),
            ),
            (
                "vad_extend_speech_before=1.000",
                "vad_extend_speech_before",
                TimeValue("1.000"),
            ),
            ("vad_log_energy_threshold=0.750", "vad_log_energy_threshold", 0.750),
            (
                "vad_min_nonspeech_length=0.500",
                "vad_min_nonspeech_length",
                TimeValue("0.500"),
            ),
        )
        for string, key, value in params:
            with self.subTest(string=string, key=key, value=value):
                rconf = RuntimeConfiguration(string)
                self.assertEqual(rconf[key], value)
