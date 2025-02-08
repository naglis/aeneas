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

import functools
import urllib.parse

import lxml.etree as ET

from aeneas.exacttiming import TimeValue
from aeneas.syncmap.missingparametererror import SyncMapMissingParameterError
from aeneas.syncmap.smfgxml import SyncMapFormatGenericXML
import aeneas.globalconstants as gc
import aeneas.globalfunctions as gf

SMIL_NS = "http://www.w3.org/ns/SMIL"
EPUB_NS = "http://www.idpf.org/2007/ops"

with_smil_ns = functools.partial(gf.with_ns, ns=SMIL_NS)
with_epub_ns = functools.partial(gf.with_ns, ns=EPUB_NS)


class SyncMapFormatSMIL(SyncMapFormatGenericXML):
    """
    Handler for SMIL for EPUB 3 I/O format.
    """

    DEFAULT = "smil"

    HUMAN = "smilh"

    MACHINE = "smilm"

    MACHINE_ALIASES = (MACHINE,)

    def __init__(self, variant: str = DEFAULT, parameters: dict | None = None):
        super().__init__(variant=variant, parameters=parameters)
        if self.variant in self.MACHINE_ALIASES:
            self.format_time_function = gf.time_to_ssmmm
        else:
            self.format_time_function = gf.time_to_hhmmssmmm

    @staticmethod
    def _autodetect_parse_duration(value: str) -> TimeValue:
        if ":" in value:
            return gf.time_from_hhmmssmmm(value)
        else:
            return gf.time_from_ssmmm(value)

    def parse(self, input_text: str, syncmap):
        """
        Read from SMIL file.

        Limitations:
        1. parses only ``<par>`` elements, in order
        2. timings must have ``hh:mm:ss.mmm`` or ``ss.mmm`` format (autodetected)
        3. both ``clipBegin`` and ``clipEnd`` attributes of ``<audio>`` must be populated
        """
        root = ET.fromstring(input_text)
        for par in root.iter(with_smil_ns("par")):
            for child in par:
                if child.tag == with_smil_ns("text"):
                    identifier = urllib.parse.urlparse(child.get("src")).fragment
                elif child.tag == with_smil_ns("audio"):
                    begin = self._autodetect_parse_duration(child.get("clipBegin"))
                    end = self._autodetect_parse_duration(child.get("clipEnd"))
            # TODO read text from additional text_file?
            self._add_fragment(
                syncmap=syncmap, identifier=identifier, lines=[""], begin=begin, end=end
            )

    def format(self, syncmap) -> str:
        # check for required parameters
        for key in (
            gc.PPN_TASK_OS_FILE_SMIL_PAGE_REF,
            gc.PPN_TASK_OS_FILE_SMIL_AUDIO_REF,
        ):
            if gf.safe_get(self.parameters, key, None) is None:
                raise SyncMapMissingParameterError(
                    f"Parameter {key!r} must be specified for format {self.variant!r}"
                )

        # we are sure we have them
        text_ref = urllib.parse.quote(
            self.parameters[gc.PPN_TASK_OS_FILE_SMIL_PAGE_REF]
        )
        audio_ref = urllib.parse.quote(
            self.parameters[gc.PPN_TASK_OS_FILE_SMIL_AUDIO_REF]
        )

        # build tree
        smil_elem = ET.Element(
            with_smil_ns("smil"),
            attrib={
                "version": "3.0",
            },
            nsmap={
                None: SMIL_NS,
                "epub": EPUB_NS,
            },
        )
        body_elem = ET.SubElement(smil_elem, with_smil_ns("body"))
        seq_elem = ET.SubElement(
            body_elem,
            with_smil_ns("seq"),
            attrib={
                "id": "seq000001",
                with_epub_ns("textref"): text_ref,
            },
        )

        if syncmap.is_single_level:
            self._smil_single_level(syncmap, seq_elem, text_ref, audio_ref)
        else:
            self._smil_multi_level(syncmap, seq_elem, text_ref, audio_ref)

        return self._tree_to_string(smil_elem, xml_declaration=False)

    def _smil_single_level(self, syncmap, seq_elem, text_ref: str, audio_ref: str):
        for i, fragment in enumerate(syncmap.fragments, start=1):
            text = fragment.text_fragment
            par_elem = ET.SubElement(
                seq_elem,
                with_smil_ns("par"),
                attrib={
                    "id": f"par{i:06d}",
                },
            )
            ET.SubElement(
                par_elem,
                with_smil_ns("text"),
                attrib={
                    "src": f"{text_ref}#{text.identifier}",
                },
            )
            ET.SubElement(
                par_elem,
                with_smil_ns("audio"),
                attrib={
                    "src": audio_ref,
                    "clipBegin": self.format_time_function(fragment.begin),
                    "clipEnd": self.format_time_function(fragment.end),
                },
            )

    def _smil_multi_level(self, syncmap, seq_elem, text_ref: str, audio_ref: str):
        # TODO support generic multiple levels
        for par_index, par_child in enumerate(
            syncmap.fragments_tree.children_not_empty, start=1
        ):
            par_seq_elem = ET.SubElement(
                seq_elem,
                with_smil_ns("seq"),
                attrib={
                    # COMMENTED "id": f"p{par_index:06d}",
                    with_epub_ns("type"): "paragraph",
                    with_epub_ns(
                        "textref"
                    ): f"{text_ref}#{par_child.value.text_fragment.identifier}",
                },
            )
            for sen_index, sen_child in enumerate(
                par_child.children_not_empty, start=1
            ):
                sen_seq_elem = ET.SubElement(
                    par_seq_elem,
                    with_smil_ns("seq"),
                    attrib={
                        # COMMENTED "id": par_seq_elem.attrib["id"] + f"s{sen_index:06d}",
                        with_epub_ns("type"): "sentence",
                        with_epub_ns(
                            "textref"
                        ): f"{text_ref}#{sen_child.value.text_fragment.identifier}",
                    },
                )
                for word_index, word_child in enumerate(
                    sen_child.children_not_empty, start=1
                ):
                    fragment = word_child.value
                    text = fragment.text_fragment
                    word_seq_elem = ET.SubElement(
                        sen_seq_elem,
                        with_smil_ns("seq"),
                        attrib={
                            # COMMENTED "id": sen_seq_elem.attrib["id"] + f"w{wor_index:06d}",
                            with_epub_ns("type"): "word",
                            with_epub_ns("textref"): f"{text_ref}#{text.identifier}",
                        },
                    )
                    wor_par_elem = ET.SubElement(word_seq_elem, with_smil_ns("par"))
                    ET.SubElement(
                        wor_par_elem,
                        with_smil_ns("text"),
                        attrib={
                            "src": f"{text_ref}#{text.identifier}",
                        },
                    )
                    ET.SubElement(
                        wor_par_elem,
                        with_smil_ns("audio"),
                        attrib={
                            "src": audio_ref,
                            "clipBegin": self.format_time_function(fragment.begin),
                            "clipEnd": self.format_time_function(fragment.end),
                        },
                    )
