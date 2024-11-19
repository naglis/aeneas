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

from aeneas.validator import Validator
import aeneas.globalfunctions as gf


class TestValidator(unittest.TestCase):
    def test_check_raw_string(self):
        for name, value, passed in (
            ("none_not_ok", None, False),
            ("unicode_string_not_ok", "Unicode string should fail", False),
            ("empty_byte_string_not_ok", b"", False),
            ("latin1_encoded_byte_string_not_ok", "abcdé".encode("latin-1"), False),
            ("utf8_encoded_byte_string_ok", "abcdé".encode("utf-8"), True),
            (
                "byte_string_w_reserved_char_not_ok",
                b"string with ~ reserved char",
                False,
            ),
            ("byte_string_wo_reserved_char_ok", b"string without reserved char", True),
        ):
            with self.subTest(name=name, value=value, passed=passed):
                validator = Validator()
                validator.check_raw_string(value, is_bstring=True)
                self.assertEqual(validator.result.passed, passed)

    def test_check_file_encoding(self):
        for name, path, passed in (
            ("none_not_ok", None, False),
            ("empty_file_ok", "res/validator/empty.txt", True),
            (
                "iso8859_encoded_file_not_ok",
                "res/validator/encoding_iso8859.txt",
                False,
            ),
            ("utf32_encoded_file_not_ok", "res/validator/encoding_utf32.xhtml", False),
            ("utf8_encoded_file_ok", "res/validator/encoding_utf8.xhtml", True),
            (
                "utf8_encoded_file_w_bom_ok",
                "res/validator/encoding_utf8_bom.xhtml",
                True,
            ),
        ):
            with self.subTest(name=name, path=path, passed=passed):
                validator = Validator()
                result = validator.check_file_encoding(gf.absolute_path(path, __file__))
                self.assertEqual(result.passed, passed)

    def test_check_configuration_string(self):
        for name, value, is_job, passed in (
            # Job (is_job=True)
            (
                "job_reserved_characters",
                "dummy config string with ~ reserved characters",
                True,
                False,
            ),
            (
                "job_bad_encoding",
                "config string with bad encoding: à".encode("latin-1"),
                True,
                False,
            ),
            ("job_malformed_string", "malformed config string", True, False),
            ("job_no_key", "=malformed", True, False),
            ("job_no_value", "malformed=", True, False),
            ("job_invalid_keys", "not=relevant|config=string", True, False),
            (
                "job_valid",
                "job_language=it|os_job_file_name=output.zip|os_job_file_container=zip",
                True,
                True,
            ),
            (
                "job_missing_required_job_language",
                "os_job_file_name=output.zip|os_job_file_container=zip",
                True,
                False,
            ),
            (
                "job_missing_required_os_job_file_container",
                "job_language=it|os_job_file_name=output.zip",
                True,
                False,
            ),
            (
                "job_missing_required_os_job_file_name",
                "job_language=it|os_job_file_container=zip",
                True,
                False,
            ),
            (
                "job_invalid_value_os_job_file_container",
                "job_language=it|os_job_file_name=output.zip|os_job_file_container=zzzzzz",
                True,
                False,
            ),
            (
                "job_invalid_value_is_hierarchy_type",
                "job_language=it|os_job_file_name=output.zip|os_job_file_container=zip|is_hierarchy_type=zzzzzz",
                True,
                False,
            ),
            (
                "job_valid_flat",
                "job_language=it|os_job_file_name=output.zip|os_job_file_container=zip|is_hierarchy_type=flat",
                True,
                True,
            ),
            (
                "job_valid_paged_with_required",
                "job_language=it|os_job_file_name=output.zip|os_job_file_container=zip|is_hierarchy_type=paged|is_task_dir_name_regex=[0-9]*",
                True,
                True,
            ),
            (
                "job_missing_paged_required_is_task_dir_name_regex",
                "job_language=it|os_job_file_name=output.zip|os_job_file_container=zip|is_hierarchy_type=paged",
                True,
                False,
            ),
            (
                "job_invalid_value_os_job_file_hierarchy_type",
                "job_language=it|os_job_file_name=output.zip|os_job_file_container=zip|os_job_file_hierarchy_type=zzzzzz",
                True,
                False,
            ),
            (
                "job_valid_os_flat",
                "job_language=it|os_job_file_name=output.zip|os_job_file_container=zip|os_job_file_hierarchy_type=flat",
                True,
                True,
            ),
            (
                "job_valid_os_paged",
                "job_language=it|os_job_file_name=output.zip|os_job_file_container=zip|os_job_file_hierarchy_type=paged",
                True,
                True,
            ),
            # language is no longer checked
            # ("job_invalid_value_job_language", "job_language=zzzz|os_job_file_name=output.zip|os_job_file_container=zip", True, False),
            # Task (is_job=False)
            (
                "task_bad_encoding",
                "config string with bad encoding: à".encode("latin-1"),
                False,
                False,
            ),
            (
                "task_reserved_characters",
                "dummy config string with ~ reserved characters",
                False,
                False,
            ),
            ("task_malformed", "malformed config string", False, False),
            ("task_no_key", "=malformed", False, False),
            ("task_no_value", "malformed=", False, False),
            ("task_invalid_keys", "not=relevant|config=string", False, False),
            (
                "task_valid",
                "task_language=it|is_text_type=plain|os_task_file_name=output.txt|os_task_file_format=txt",
                False,
                True,
            ),
            (
                "task_missing_required_task_language",
                "is_text_type=plain|os_task_file_name=output.txt|os_task_file_format=txt",
                False,
                False,
            ),
            (
                "task_missing_required_is_text_type",
                "task_language=it|os_task_file_name=output.txt|os_task_file_format=txt",
                False,
                False,
            ),
            (
                "task_missing_required_os_task_file_name",
                "task_language=it|is_text_type=plain|os_task_file_format=txt",
                False,
                False,
            ),
            (
                "task_missing_required_os_task_file_format",
                "task_language=it|is_text_type=plain|os_task_file_name=output.txt",
                False,
                False,
            ),
            # language is no longer checked
            # ("task_invalid_value_task_language", "task_language=zzzz|is_text_type=plain|os_task_file_name=output.txt|os_task_file_format=txt", False, False),
            (
                "task_invalid_value_is_text_type",
                "task_language=it|is_text_type=zzzzzz|os_task_file_name=output.txt|os_task_file_format=txt",
                False,
                False,
            ),
            (
                "task_invalid_value_os_task_file_format",
                "task_language=it|is_text_type=plain|os_task_file_name=output.txt|os_task_file_format=zzzzzz",
                False,
                False,
            ),
            (
                "task_missing_unparsed_required_is_text_unparsed_class_regex",
                "task_language=it|is_text_type=unparsed|os_task_file_name=output.txt|os_task_file_format=txt",
                False,
                False,
            ),
            (
                "task_valid_unparsed_is_text_unparsed_class_regex",
                "task_language=it|is_text_type=unparsed|is_text_unparsed_class_regex=ra|is_text_unparsed_id_sort=numeric|os_task_file_name=output.txt|os_task_file_format=txt",
                False,
                True,
            ),
            (
                "task_valid_unparsed_is_text_unparsed_id_regex",
                "task_language=it|is_text_type=unparsed|is_text_unparsed_id_regex=f[0-9]*|is_text_unparsed_id_sort=numeric|os_task_file_name=output.txt|os_task_file_format=txt",
                False,
                True,
            ),
            (
                "task_valid_unparsed_both",
                "task_language=it|is_text_type=unparsed|is_text_unparsed_class_regex=ra|is_text_unparsed_id_regex=f[0-9]*|is_text_unparsed_id_sort=numeric|os_task_file_name=output.txt|os_task_file_format=txt",
                False,
                True,
            ),
            (
                "task_invalid_value_is_text_unparsed_id_sort",
                "task_language=it|is_text_type=unparsed|is_text_unparsed_class_regex=ra|is_text_unparsed_id_regex=f[0-9]*|is_text_unparsed_id_sort=foo|os_task_file_name=output.txt|os_task_file_format=txt",
                False,
                False,
            ),
            (
                "task_missing_required_is_text_unparsed_id_sort",
                "task_language=it|is_text_type=unparsed|is_text_unparsed_class_regex=ra|is_text_unparsed_id_regex=f[0-9]*|os_task_file_name=output.txt|os_task_file_format=txt",
                False,
                False,
            ),
            (
                "task_valid_smil",
                "task_language=it|is_text_type=plain|os_task_file_name=output.txt|os_task_file_format=smil|os_task_file_smil_page_ref=page.xhtml|os_task_file_smil_audio_ref=../Audio/audio.mp3",
                False,
                True,
            ),
            (
                "task_missing_smil_required_os_task_file_smil_audio_ref",
                "task_language=it|is_text_type=plain|os_task_file_name=output.txt|os_task_file_format=smil|os_task_file_smil_page_ref=page.xhtml",
                False,
                False,
            ),
            (
                "task_missing_smil_required_os_task_file_smil_page_ref",
                "task_language=it|is_text_type=plain|os_task_file_name=output.txt|os_task_file_format=smil|os_task_file_smil_audio_ref=../Audio/audio.mp3",
                False,
                False,
            ),
            (
                "task_missing_smil_required_both",
                "task_language=it|is_text_type=plain|os_task_file_name=output.txt|os_task_file_format=smil",
                False,
                False,
            ),
            (
                "task_valid_aba_auto",
                "task_language=it|is_text_type=plain|os_task_file_name=output.txt|os_task_file_format=txt|task_adjust_boundary_algorithm=auto",
                False,
                True,
            ),
            (
                "task_invalid_aba_value_task_adjust_boundary_algorithm",
                "task_language=it|is_text_type=plain|os_task_file_name=output.txt|os_task_file_format=txt|task_adjust_boundary_algorithm=foo",
                False,
                False,
            ),
            (
                "task_missing_aba_rate_required_task_adjust_boundary_rate_value",
                "task_language=it|is_text_type=plain|os_task_file_name=output.txt|os_task_file_format=txt|task_adjust_boundary_algorithm=rate",
                False,
                False,
            ),
            (
                "task_valid_aba_rate",
                "task_language=it|is_text_type=plain|os_task_file_name=output.txt|os_task_file_format=txt|task_adjust_boundary_algorithm=rate|task_adjust_boundary_rate_value=21",
                False,
                True,
            ),
            (
                "task_missing_aba_percent_required_task_adjust_boundary_percent_value",
                "task_language=it|is_text_type=plain|os_task_file_name=output.txt|os_task_file_format=txt|task_adjust_boundary_algorithm=percent",
                False,
                False,
            ),
            (
                "task_valid_aba_percent",
                "task_language=it|is_text_type=plain|os_task_file_name=output.txt|os_task_file_format=txt|task_adjust_boundary_algorithm=percent|task_adjust_boundary_percent_value=50",
                False,
                True,
            ),
            (
                "task_missing_aba_aftercurrent_required_task_adjust_boundary_aftercurrent_value",
                "task_language=it|is_text_type=plain|os_task_file_name=output.txt|os_task_file_format=txt|task_adjust_boundary_algorithm=aftercurrent",
                False,
                False,
            ),
            (
                "task_valid_aba_aftercurrent",
                "task_language=it|is_text_type=plain|os_task_file_name=output.txt|os_task_file_format=txt|task_adjust_boundary_algorithm=aftercurrent|task_adjust_boundary_aftercurrent_value=0.200",
                False,
                True,
            ),
            (
                "task_missing_aba_beforenext_required_task_adjust_boundary_beforenext_value",
                "task_language=it|is_text_type=plain|os_task_file_name=output.txt|os_task_file_format=txt|task_adjust_boundary_algorithm=beforenext",
                False,
                False,
            ),
            (
                "task_valid_aba_beforenext",
                "task_language=it|is_text_type=plain|os_task_file_name=output.txt|os_task_file_format=txt|task_adjust_boundary_algorithm=beforenext|task_adjust_boundary_beforenext_value=0.200",
                False,
                True,
            ),
            (
                "task_missing_aba_rateaggressive_required_task_adjust_boundary_rate_value",
                "task_language=it|is_text_type=plain|os_task_file_name=output.txt|os_task_file_format=txt|task_adjust_boundary_algorithm=rateagressive",
                False,
                False,
            ),
            (
                "task_valid_aba_rateaggressive",
                "task_language=it|is_text_type=plain|os_task_file_name=output.txt|os_task_file_format=txt|task_adjust_boundary_algorithm=rateaggressive|task_adjust_boundary_rate_value=21",
                False,
                True,
            ),
            (
                "task_missing_aba_offset_required_task_adjust_boundary_offset_value",
                "task_language=it|is_text_type=plain|os_task_file_name=output.txt|os_task_file_format=txt|task_adjust_boundary_algorithm=offset",
                False,
                False,
            ),
            (
                "task_valid_aba_offset",
                "task_language=it|is_text_type=plain|os_task_file_name=output.txt|os_task_file_format=txt|task_adjust_boundary_algorithm=offset|task_adjust_boundary_offset_value=0.200",
                False,
                True,
            ),
            (
                "task_invalid_value_os_task_file_head_tail_format",
                "task_language=it|is_text_type=plain|os_task_file_name=output.txt|os_task_file_format=txt|os_task_file_head_tail_format=foo",
                False,
                False,
            ),
            (
                "task_valid_head_tail_format",
                "task_language=it|is_text_type=plain|os_task_file_name=output.txt|os_task_file_format=txt|os_task_file_head_tail_format=add",
                False,
                True,
            ),
        ):
            with self.subTest(name=name, value=value, is_job=is_job, passed=passed):
                validator = Validator()
                result = validator.check_configuration_string(
                    value, is_job=is_job, external_name=False
                )
                self.assertEqual(result.passed, passed)
                if passed:
                    self.assertEqual(len(result.errors), 0)
                else:
                    self.assertGreater(len(result.errors), 0)

    def test_check_container(self):
        for name, path, passed in (
            ("txt_valid", "res/validator/job_txt_config", True),
            ("not_existing", "res/validator/x/y/z/not_existing", False),
            ("empty", "res/validator/job_empty", False),
            ("empty_zip", "res/validator/empty.zip", False),
            ("txt_no_config", "res/validator/job_no_config", False),
            ("txt_bad_config_01", "res/validator/job_txt_config_bad_1", False),
            ("txt_bad_config_02", "res/validator/job_txt_config_bad_2", False),
            ("txt_bad_config_03", "res/validator/job_txt_config_bad_3", False),
            ("txt_not_root", "res/validator/job_txt_config_not_root", True),
            (
                "txt_not_root_nested",
                "res/validator/job_txt_config_not_root_nested",
                True,
            ),
            ("xml_valid", "res/validator/job_xml_config", True),
            ("xml_bad_config_01", "res/validator/job_xml_config_bad_1", False),
            ("xml_bad_config_02", "res/validator/job_xml_config_bad_2", False),
            ("xml_bad_config_03", "res/validator/job_xml_config_bad_3", False),
            ("xml_bad_config_04", "res/validator/job_xml_config_bad_4", False),
            ("xml_not_root", "res/validator/job_xml_config_not_root", True),
            (
                "xml_not_root_nested",
                "res/validator/job_xml_config_not_root_nested",
                True,
            ),
        ):
            validator = Validator()
            result = validator.check_container(gf.absolute_path(path, __file__))
            self.assertEqual(result.passed, passed)
            if passed:
                self.assertEqual(len(result.errors), 0)
            else:
                self.assertGreater(len(result.errors), 0)
