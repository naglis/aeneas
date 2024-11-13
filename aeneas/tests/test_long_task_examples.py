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
    def test_example_aftercurrent(self):
        self.execute([("", "--example-aftercurrent")], 0)

    def test_example_beforenext(self):
        self.execute([("", "--example-beforenext")], 0)

    def test_example_cewsubprocess(self):
        self.execute([("", "--example-cewsubprocess")], 0)

    @extra_test
    def test_example_ctw_espeak(self):
        self.execute([("", "--example-ctw-espeak")], 0)

    # NOTE disabling this test since it requires a speect voice
    def test_example_ctw_speect(self):
        # unable to run speect with Python 3,
        # perform the test only on Python 2
        self.execute([("", "--example-ctw-speect")], 0)

    def test_example_eaf(self):
        self.execute([("", "--example-eaf")], 0)

    def test_example_faster_rate(self):
        self.execute([("", "--example-faster-rate")], 0)

    @extra_test
    def test_example_festival(self):
        self.execute([("", "--example-festival")], 0)

    def test_example_flatten_12(self):
        self.execute([("", "--example-flatten-12")], 0)

    def test_example_flatten_2(self):
        self.execute([("", "--example-flatten-2")], 0)

    def test_example_flatten_3(self):
        self.execute([("", "--example-flatten-3")], 0)

    def test_example_head_tail(self):
        self.execute([("", "--example-head-tail")], 0)

    def test_example_json(self):
        self.execute([("", "--example-json")], 0)

    def test_example_mplain_json(self):
        self.execute([("", "--example-mplain-json")], 0)

    def test_example_mplain_smil(self):
        self.execute([("", "--example-mplain-smil")], 0)

    @extra_test
    def test_example_multilevel_tts(self):
        self.execute([("", "--example-multilevel-tts")], 0)

    def test_example_munparsed_json(self):
        self.execute([("", "--example-munparsed-json")], 0)

    def test_example_munparsed_smil(self):
        self.execute([("", "--example-munparsed-smil")], 0)

    def test_example_mws(self):
        self.execute([("", "--example-mws")], 0)

    def test_example_no_zero(self):
        self.execute([("", "--example-no-zero")], 0)

    def test_example_offset(self):
        self.execute([("", "--example-offset")], 0)

    def test_example_percent(self):
        self.execute([("", "--example-percent")], 0)

    def test_example_py(self):
        self.execute([("", "--example-py")], 0)

    def test_example_rate(self):
        self.execute([("", "--example-rate")], 0)

    def test_example_remove_nonspeech(self):
        self.execute([("", "--example-remove-nonspeech")], 0)

    def test_example_remove_nonspeech_rateaggressive(self):
        self.execute([("", "--example-remove-nonspeech-rateaggressive")], 0)

    def test_example_replace_nonspeech(self):
        self.execute([("", "--example-replace-nonspeech")], 0)

    def test_example_sd(self):
        self.execute([("", "--example-sd")], 0)

    def test_example_smil(self):
        self.execute([("", "--example-smil")], 0)

    def test_example_srt(self):
        self.execute([("", "--example-srt")], 0)

    def test_example_textgrid(self):
        self.execute([("", "--example-textgrid")], 0)

    def test_example_tsv(self):
        self.execute([("", "--example-tsv")], 0)

    def test_example_words(self):
        self.execute([("", "--example-words")], 0)

    @extra_test
    def test_example_words_festival_cache(self):
        self.execute([("", "--example-words-festival-cache")], 0)

    def test_example_words_multilevel(self):
        self.execute([("", "--example-words-multilevel")], 0)

    # NOTE disabling this test since it requires a network connection
    def zzz_test_example_youtube(self):
        self.execute([("", "--example-youtube")], 0)
