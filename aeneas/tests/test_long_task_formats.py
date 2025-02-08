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
    def test_exec_aud(self):
        self.execute(
            [
                ("in", "../tools/res/audio.mp3"),
                ("in", "../tools/res/plain.txt"),
                ("", "task_language=eng|is_text_type=plain|os_task_file_format=aud"),
                ("out", "sonnet.aud"),
            ],
            0,
        )

    def test_exec_audh(self):
        self.execute(
            [
                ("in", "../tools/res/audio.mp3"),
                ("in", "../tools/res/plain.txt"),
                ("", "task_language=eng|is_text_type=plain|os_task_file_format=audh"),
                ("out", "sonnet.audh"),
            ],
            0,
        )

    def test_exec_audm(self):
        self.execute(
            [
                ("in", "../tools/res/audio.mp3"),
                ("in", "../tools/res/plain.txt"),
                ("", "task_language=eng|is_text_type=plain|os_task_file_format=audm"),
                ("out", "sonnet.audm"),
            ],
            0,
        )

    def test_exec_csv(self):
        self.execute(
            [
                ("in", "../tools/res/audio.mp3"),
                ("in", "../tools/res/plain.txt"),
                ("", "task_language=eng|is_text_type=plain|os_task_file_format=csv"),
                ("out", "sonnet.csv"),
            ],
            0,
        )

    def test_exec_csvh(self):
        self.execute(
            [
                ("in", "../tools/res/audio.mp3"),
                ("in", "../tools/res/plain.txt"),
                ("", "task_language=eng|is_text_type=plain|os_task_file_format=csvh"),
                ("out", "sonnet.csvh"),
            ],
            0,
        )

    def test_exec_dfxp(self):
        self.execute(
            [
                ("in", "../tools/res/audio.mp3"),
                ("in", "../tools/res/plain.txt"),
                ("", "task_language=eng|is_text_type=plain|os_task_file_format=dfxp"),
                ("out", "sonnet.dfxp"),
            ],
            0,
        )

    def test_exec_eaf(self):
        self.execute(
            [
                ("in", "../tools/res/audio.mp3"),
                ("in", "../tools/res/plain.txt"),
                ("", "task_language=eng|is_text_type=plain|os_task_file_format=eaf"),
                ("out", "sonnet.eaf"),
            ],
            0,
        )

    def test_exec_json(self):
        self.execute(
            [
                ("in", "../tools/res/audio.mp3"),
                ("in", "../tools/res/plain.txt"),
                ("", "task_language=eng|is_text_type=plain|os_task_file_format=json"),
                ("out", "sonnet.json"),
            ],
            0,
        )

    def test_exec_rbse(self):
        self.execute(
            [
                ("in", "../tools/res/audio.mp3"),
                ("in", "../tools/res/plain.txt"),
                ("", "task_language=eng|is_text_type=plain|os_task_file_format=rbse"),
                ("out", "sonnet.rbse"),
            ],
            0,
        )

    def test_exec_sbv(self):
        self.execute(
            [
                ("in", "../tools/res/audio.mp3"),
                ("in", "../tools/res/subtitles.txt"),
                (
                    "",
                    "task_language=eng|is_text_type=subtitles|os_task_file_format=sbv",
                ),
                ("out", "sonnet.sbv"),
            ],
            0,
        )

    def test_exec_smil(self):
        self.execute(
            [
                ("in", "../tools/res/audio.mp3"),
                ("in", "../tools/res/page.xhtml"),
                (
                    "",
                    "task_language=eng|is_text_type=unparsed|is_text_unparsed_id_regex=f[0-9]+|is_text_unparsed_id_sort=numeric|os_task_file_format=smil|os_task_file_smil_audio_ref=p001.mp3|os_task_file_smil_page_ref=p001.xhtml",
                ),
                ("out", "sonnet.smil"),
            ],
            0,
        )

    def test_exec_smilh(self):
        self.execute(
            [
                ("in", "../tools/res/audio.mp3"),
                ("in", "../tools/res/page.xhtml"),
                (
                    "",
                    "task_language=eng|is_text_type=unparsed|is_text_unparsed_id_regex=f[0-9]+|is_text_unparsed_id_sort=numeric|os_task_file_format=smilh|os_task_file_smil_audio_ref=p001.mp3|os_task_file_smil_page_ref=p001.xhtml",
                ),
                ("out", "sonnet.smilh"),
            ],
            0,
        )

    def test_exec_smilm(self):
        self.execute(
            [
                ("in", "../tools/res/audio.mp3"),
                ("in", "../tools/res/page.xhtml"),
                (
                    "",
                    "task_language=eng|is_text_type=unparsed|is_text_unparsed_id_regex=f[0-9]+|is_text_unparsed_id_sort=numeric|os_task_file_format=smilm|os_task_file_smil_audio_ref=p001.mp3|os_task_file_smil_page_ref=p001.xhtml",
                ),
                ("out", "sonnet.smilm"),
            ],
            0,
        )

    def test_exec_srt(self):
        self.execute(
            [
                ("in", "../tools/res/audio.mp3"),
                ("in", "../tools/res/subtitles.txt"),
                (
                    "",
                    "task_language=eng|is_text_type=subtitles|os_task_file_format=srt",
                ),
                ("out", "sonnet.srt"),
            ],
            0,
        )

    def test_exec_ssv(self):
        self.execute(
            [
                ("in", "../tools/res/audio.mp3"),
                ("in", "../tools/res/plain.txt"),
                ("", "task_language=eng|is_text_type=plain|os_task_file_format=ssv"),
                ("out", "sonnet.ssv"),
            ],
            0,
        )

    def test_exec_ssvh(self):
        self.execute(
            [
                ("in", "../tools/res/audio.mp3"),
                ("in", "../tools/res/plain.txt"),
                ("", "task_language=eng|is_text_type=plain|os_task_file_format=ssvh"),
                ("out", "sonnet.ssvh"),
            ],
            0,
        )

    def test_exec_ssvm(self):
        self.execute(
            [
                ("in", "../tools/res/audio.mp3"),
                ("in", "../tools/res/plain.txt"),
                ("", "task_language=eng|is_text_type=plain|os_task_file_format=ssvm"),
                ("out", "sonnet.ssvm"),
            ],
            0,
        )

    def test_exec_sub(self):
        self.execute(
            [
                ("in", "../tools/res/audio.mp3"),
                ("in", "../tools/res/subtitles.txt"),
                (
                    "",
                    "task_language=eng|is_text_type=subtitles|os_task_file_format=sub",
                ),
                ("out", "sonnet.sub"),
            ],
            0,
        )

    def test_exec_tab(self):
        self.execute(
            [
                ("in", "../tools/res/audio.mp3"),
                ("in", "../tools/res/plain.txt"),
                ("", "task_language=eng|is_text_type=plain|os_task_file_format=tab"),
                ("out", "sonnet.tab"),
            ],
            0,
        )

    def test_exec_tsv(self):
        self.execute(
            [
                ("in", "../tools/res/audio.mp3"),
                ("in", "../tools/res/plain.txt"),
                ("", "task_language=eng|is_text_type=plain|os_task_file_format=tsv"),
                ("out", "sonnet.tsv"),
            ],
            0,
        )

    def test_exec_tsvh(self):
        self.execute(
            [
                ("in", "../tools/res/audio.mp3"),
                ("in", "../tools/res/plain.txt"),
                ("", "task_language=eng|is_text_type=plain|os_task_file_format=tsvh"),
                ("out", "sonnet.tsvh"),
            ],
            0,
        )

    def test_exec_tsvm(self):
        self.execute(
            [
                ("in", "../tools/res/audio.mp3"),
                ("in", "../tools/res/plain.txt"),
                ("", "task_language=eng|is_text_type=plain|os_task_file_format=tsvm"),
                ("out", "sonnet.tsvm"),
            ],
            0,
        )

    def test_exec_ttml(self):
        self.execute(
            [
                ("in", "../tools/res/audio.mp3"),
                ("in", "../tools/res/subtitles.txt"),
                (
                    "",
                    "task_language=eng|is_text_type=subtitles|os_task_file_format=ttml",
                ),
                ("out", "sonnet.ttml"),
            ],
            0,
        )

    def test_exec_txt(self):
        self.execute(
            [
                ("in", "../tools/res/audio.mp3"),
                ("in", "../tools/res/plain.txt"),
                ("", "task_language=eng|is_text_type=plain|os_task_file_format=txt"),
                ("out", "sonnet.txt"),
            ],
            0,
        )

    def test_exec_txth(self):
        self.execute(
            [
                ("in", "../tools/res/audio.mp3"),
                ("in", "../tools/res/plain.txt"),
                ("", "task_language=eng|is_text_type=plain|os_task_file_format=txth"),
                ("out", "sonnet.txth"),
            ],
            0,
        )

    def test_exec_txtm(self):
        self.execute(
            [
                ("in", "../tools/res/audio.mp3"),
                ("in", "../tools/res/plain.txt"),
                ("", "task_language=eng|is_text_type=plain|os_task_file_format=txtm"),
                ("out", "sonnet.txtm"),
            ],
            0,
        )

    def test_exec_vtt(self):
        self.execute(
            [
                ("in", "../tools/res/audio.mp3"),
                ("in", "../tools/res/subtitles.txt"),
                (
                    "",
                    "task_language=eng|is_text_type=subtitles|os_task_file_format=vtt",
                ),
                ("out", "sonnet.vtt"),
            ],
            0,
        )

    def test_exec_xml(self):
        self.execute(
            [
                ("in", "../tools/res/audio.mp3"),
                ("in", "../tools/res/plain.txt"),
                ("", "task_language=eng|is_text_type=plain|os_task_file_format=xml"),
                ("out", "sonnet.xml"),
            ],
            0,
        )

    def test_exec_xml_legacy(self):
        self.execute(
            [
                ("in", "../tools/res/audio.mp3"),
                ("in", "../tools/res/plain.txt"),
                (
                    "",
                    "task_language=eng|is_text_type=plain|os_task_file_format=xml_legacy",
                ),
                ("out", "sonnet.xml_legacy"),
            ],
            0,
        )
