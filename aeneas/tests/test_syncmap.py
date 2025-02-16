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

import io
import unittest
import tempfile
import typing

from aeneas.exacttiming import TimeInterval, TimeValue
from aeneas.language import Language
from aeneas.syncmap import SyncMap, SyncMapFormat, SyncMapFragment
from aeneas.syncmap.missingparametererror import SyncMapMissingParameterError
from aeneas.tree import Tree
from aeneas.textfile import TextFragment
import aeneas.globalconstants as gc
import aeneas.globalfunctions as gf


class _Sentinel: ...


class BaseSyncMapCase(unittest.TestCase):
    NOT_SET = _Sentinel()
    PARAMETERS = {
        gc.PPN_TASK_OS_FILE_SMIL_PAGE_REF: "sonnet001.xhtml",
        gc.PPN_TASK_OS_FILE_SMIL_AUDIO_REF: "sonnet001.mp3",
        gc.PPN_SYNCMAP_LANGUAGE: Language.ENG,
    }

    def load(self, fmt, multiline: bool = False, utf8: bool = False):
        if multiline and utf8:
            path = f"res/syncmaps/sonnet001_mu.{fmt}"
        elif multiline:
            path = f"res/syncmaps/sonnet001_m.{fmt}"
        elif utf8:
            path = f"res/syncmaps/sonnet001_u.{fmt}"
        else:
            path = f"res/syncmaps/sonnet001.{fmt}"

        with open(gf.absolute_path(path, __file__), mode="rb") as f:
            return SyncMap.load(f, fmt, parameters=self.PARAMETERS)

    def dump(
        self,
        fmt: str,
        multiline: bool = False,
        utf8: bool = False,
        parameters: dict | None | _Sentinel = NOT_SET,
    ):
        if parameters is self.NOT_SET:
            parameters = self.PARAMETERS

        syn = self.load(SyncMapFormat.XML, multiline=multiline, utf8=utf8)
        syn.dump(io.StringIO(), fmt, parameters=parameters)


class TestSyncMap(BaseSyncMapCase):
    maxDiff = None

    NOT_EXISTING_SRT = gf.absolute_path("not_existing.srt", __file__)
    EXISTING_SRT = gf.absolute_path("res/syncmaps/sonnet001.srt", __file__)
    EMPTY_INTERVAL = TimeInterval(begin=TimeValue("0.000"), end=TimeValue("0.000"))

    def build_tree_from_intervals(
        self, intervals: typing.Sequence[tuple[str, str]]
    ) -> Tree:
        tree = Tree()
        for begin, end in intervals:
            smf = SyncMapFragment.from_begin_end(
                begin=TimeValue(begin), end=TimeValue(end)
            )
            child = Tree(value=smf)
            tree.add_child(child, as_last=True)

        return tree

    def test_constructor(self):
        syn = SyncMap()
        self.assertEqual(len(syn), 0)

    def test_constructor_none(self):
        syn = SyncMap(tree=None)
        self.assertEqual(len(syn), 0)

    def test_fragments_tree_not_given(self):
        syn = SyncMap()
        self.assertEqual(len(syn.fragments_tree), 0)

    def test_fragments_tree_empty(self):
        tree = Tree()
        syn = SyncMap(tree=tree)
        self.assertEqual(len(syn.fragments_tree), 0)

    def test_fragments_tree_not_empty(self):
        smf = SyncMapFragment(interval=self.EMPTY_INTERVAL)
        child = Tree(value=smf)
        tree = Tree()
        tree.add_child(child)
        syn = SyncMap(tree=tree)
        self.assertEqual(len(syn.fragments_tree), 1)

    def test_is_single_level_true_empty(self):
        syn = SyncMap()
        self.assertTrue(syn.is_single_level)

    def test_is_single_level_true_not_empty(self):
        smf = SyncMapFragment(interval=self.EMPTY_INTERVAL)
        child = Tree(value=smf)
        tree = Tree()
        tree.add_child(child)
        syn = SyncMap(tree=tree)
        self.assertTrue(syn.is_single_level)

    def test_is_single_level_false(self):
        smf2 = SyncMapFragment(interval=self.EMPTY_INTERVAL)
        child2 = Tree(value=smf2)
        smf = SyncMapFragment(interval=self.EMPTY_INTERVAL)
        child = Tree(value=smf)
        child.add_child(child2)
        tree = Tree()
        tree.add_child(child)
        syn = SyncMap(tree=tree)
        self.assertFalse(syn.is_single_level)

    def test_fragments_empty(self):
        syn = SyncMap()
        self.assertEqual(len(syn.fragments), 0)

    def test_fragments(self):
        syn = self.load("txt")
        self.assertTrue(syn.fragments)

    def test_leaves_empty(self):
        syn = SyncMap()
        self.assertFalse(syn.leaves())

    def test_leaves(self):
        syn = self.load("txt")
        self.assertTrue(syn.leaves())

    def test_json_dict(self):
        json_dict = self.load("txt").json_dict

        self.assertIn("fragments", json_dict)
        self.assertEqual(len(json_dict["fragments"]), 15)
        self.assertEqual(
            json_dict["fragments"][0],
            {
                "begin": "0.000",
                "children": [],
                "end": "2.680",
                "id": "f000001",
                "language": Language.ENG,
                "lines": ["1"],
            },
        )

    def test_clear(self):
        syn = self.load("txt")
        self.assertEqual(len(syn), 15)
        syn.clear()
        self.assertEqual(len(syn), 0)

    def test_has_adjacent_leaves_only_empty(self):
        syn = SyncMap()
        self.assertTrue(syn.has_adjacent_leaves_only)

    def test_has_adjacent_leaves_only_not_empty(self):
        syn = self.load("txt")
        self.assertTrue(syn.has_adjacent_leaves_only)

    def test_has_adjacent_leaves_only(self):
        cases = [
            ([("0.000", "0.000"), ("0.000", "0.000")], True),
            ([("0.000", "0.000"), ("0.000", "1.000")], True),
            ([("0.000", "1.000"), ("1.000", "1.000")], True),
            ([("0.000", "1.000"), ("1.000", "2.000")], True),
            ([("0.000", "0.000"), ("1.000", "1.000")], False),
            ([("0.000", "0.000"), ("1.000", "2.000")], False),
            ([("0.000", "1.000"), ("2.000", "2.000")], False),
            ([("0.000", "1.000"), ("2.000", "3.000")], False),
        ]
        for intervals, expexted in cases:
            with self.subTest(intervals=intervals, expected=expexted):
                syn = SyncMap(tree=self.build_tree_from_intervals(intervals))

                self.assertEqual(syn.has_adjacent_leaves_only, expexted)

    def test_has_zero_length_leaves_empty(self):
        syn = SyncMap()
        self.assertFalse(syn.has_zero_length_leaves)

    def test_has_zero_length_leaves_not_empty(self):
        syn = self.load("txt")
        self.assertFalse(syn.has_zero_length_leaves)

    def test_has_zero_length_leaves(self):
        cases = [
            ([("0.000", "0.000"), ("0.000", "0.000")], True),
            ([("0.000", "0.000"), ("0.000", "1.000")], True),
            ([("0.000", "1.000"), ("1.000", "1.000")], True),
            ([("0.000", "1.000"), ("1.000", "2.000")], False),
            ([("0.000", "0.000"), ("1.000", "1.000")], True),
            ([("0.000", "0.000"), ("1.000", "2.000")], True),
            ([("0.000", "1.000"), ("2.000", "2.000")], True),
            ([("0.000", "1.000"), ("2.000", "3.000")], False),
        ]
        for intervals, expected in cases:
            with self.subTest(intervals=intervals, expected=expected):
                syn = SyncMap(tree=self.build_tree_from_intervals(intervals))

                self.assertEqual(syn.has_zero_length_leaves, expected)

    def test_leaves_are_consistent_empty(self):
        syn = SyncMap()
        self.assertTrue(syn.leaves_are_consistent)

    def test_leaves_are_consistent_not_empty(self):
        syn = self.load("txt")
        self.assertTrue(syn.leaves_are_consistent)

    def test_leaves_are_consistent(self):
        cases = [
            ([("0.000", "0.000"), ("0.000", "0.000")], True),
            ([("0.000", "0.000"), ("0.000", "1.000")], True),
            ([("0.000", "1.000"), ("1.000", "1.000")], True),
            ([("0.000", "1.000"), ("1.000", "2.000")], True),
            ([("0.000", "0.000"), ("1.000", "1.000")], True),
            ([("0.000", "0.000"), ("1.000", "2.000")], True),
            ([("0.000", "1.000"), ("2.000", "2.000")], True),
            ([("0.000", "1.000"), ("2.000", "3.000")], True),
            ([("0.000", "1.000"), ("1.000", "1.000"), ("1.000", "2.000")], True),
            ([("0.000", "1.000"), ("1.000", "1.000"), ("2.000", "2.000")], True),
            ([("0.000", "1.000"), ("2.000", "3.000"), ("1.500", "1.500")], True),
            ([("0.000", "1.000"), ("2.000", "3.000"), ("1.500", "1.750")], True),
            ([("0.000", "1.000"), ("1.040", "2.000")], True),
            ([("0.000", "1.000"), ("0.000", "0.500")], False),
            ([("0.000", "1.000"), ("0.000", "1.000")], False),
            ([("0.000", "1.000"), ("0.000", "1.500")], False),
            ([("0.000", "1.000"), ("0.500", "0.500")], False),
            ([("0.000", "1.000"), ("0.500", "0.750")], False),
            ([("0.000", "1.000"), ("0.500", "1.000")], False),
            ([("0.000", "1.000"), ("0.500", "1.500")], False),
            ([("0.000", "1.000"), ("2.000", "2.000"), ("1.500", "2.500")], False),
            ([("0.000", "1.000"), ("2.000", "3.000"), ("1.500", "2.500")], False),
            ([("0.000", "1.000"), ("0.960", "2.000")], False),
        ]
        for intervals, expexted in cases:
            syn = SyncMap(tree=self.build_tree_from_intervals(intervals))

            self.assertEqual(syn.leaves_are_consistent, expexted)

    def test_load_unknown_format_raises_keyerror(self):
        with self.assertRaises(KeyError):
            SyncMap.load(io.BytesIO(), "foo")

    def test_dump_unknown_format_raises_keyerror(self):
        syn = SyncMap()
        with self.assertRaises(KeyError):
            syn.dump(io.StringIO(), "foo")

    def test_dump_smil_no_both(self):
        fmt = SyncMapFormat.SMIL
        with self.assertRaises(SyncMapMissingParameterError):
            self.dump(fmt, parameters=None)

    def test_dump_smil_no_page(self):
        fmt = SyncMapFormat.SMIL
        parameters = {gc.PPN_TASK_OS_FILE_SMIL_AUDIO_REF: "sonnet001.mp3"}
        with self.assertRaises(SyncMapMissingParameterError):
            self.dump(fmt, parameters=parameters)

    def test_dump_smil_no_audio(self):
        fmt = SyncMapFormat.SMIL
        parameters = {gc.PPN_TASK_OS_FILE_SMIL_PAGE_REF: "sonnet001.xhtml"}
        with self.assertRaises(SyncMapMissingParameterError):
            self.dump(fmt, parameters=parameters)

    def _dump_smil(
        self, intervals: list[tuple[str, str, str]], *, parameters: dict | None = None
    ) -> str:
        tree = Tree()
        for begin, end, text_fragment in intervals:
            smf = SyncMapFragment.from_begin_end(
                begin=TimeValue(begin),
                end=TimeValue(end),
                text_fragment=TextFragment(text_fragment),
            )
            tree.add_child(Tree(value=smf), as_last=True)

        syn = SyncMap(tree=tree)

        buf = io.StringIO()
        syn.dump(buf, SyncMapFormat.SMIL, parameters=parameters)
        return buf.getvalue().strip()

    def test_dump_valid_smil(self):
        intervals = [("0.000", "1.000", "foo"), ("1.000", "2.000", "bar")]

        data = self._dump_smil(intervals, parameters=self.PARAMETERS)

        self.assertEqual(
            data,
            """
<smil xmlns="http://www.w3.org/ns/SMIL" xmlns:epub="http://www.idpf.org/2007/ops" version="3.0">
  <body>
    <seq id="seq000001" epub:textref="sonnet001.xhtml">
      <par id="par000001">
        <text src="sonnet001.xhtml#foo"/>
        <audio src="sonnet001.mp3" clipBegin="00:00:00.000" clipEnd="00:00:01.000"/>
      </par>
      <par id="par000002">
        <text src="sonnet001.xhtml#bar"/>
        <audio src="sonnet001.mp3" clipBegin="00:00:01.000" clipEnd="00:00:02.000"/>
      </par>
    </seq>
  </body>
</smil>""".strip(),
        )

    def test_dump_smil_spaces_in_refs_are_quoted(self):
        intervals = [("0.000", "1.000", "foo"), ("1.000", "2.000", "bar")]

        data = self._dump_smil(
            intervals,
            parameters={
                gc.PPN_TASK_OS_FILE_SMIL_PAGE_REF: "sonnet 001.xhtml",
                gc.PPN_TASK_OS_FILE_SMIL_AUDIO_REF: "sonnet 001.mp3",
                gc.PPN_SYNCMAP_LANGUAGE: Language.ENG,
            },
        )

        self.assertEqual(
            data,
            """
<smil xmlns="http://www.w3.org/ns/SMIL" xmlns:epub="http://www.idpf.org/2007/ops" version="3.0">
  <body>
    <seq id="seq000001" epub:textref="sonnet%20001.xhtml">
      <par id="par000001">
        <text src="sonnet%20001.xhtml#foo"/>
        <audio src="sonnet%20001.mp3" clipBegin="00:00:00.000" clipEnd="00:00:01.000"/>
      </par>
      <par id="par000002">
        <text src="sonnet%20001.xhtml#bar"/>
        <audio src="sonnet%20001.mp3" clipBegin="00:00:01.000" clipEnd="00:00:02.000"/>
      </par>
    </seq>
  </body>
</smil>""".strip(),
        )

    def test_dump_ttml_no_language(self):
        fmt = SyncMapFormat.TTML
        self.dump(fmt, parameters=None)

    def test_dump_ttml_language(self):
        self.dump(
            SyncMapFormat.TTML, parameters={gc.PPN_SYNCMAP_LANGUAGE: Language.ENG}
        )

    def test_dump_finetuneas_html(self):
        syn = self.load(SyncMapFormat.XML, multiline=True, utf8=True)
        with tempfile.NamedTemporaryFile(suffix=".html", mode="w") as tmp_file:
            syn.dump_finetuneas_html(tmp_file, "test", "foo.mp3")
