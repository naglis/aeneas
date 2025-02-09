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

from aeneas.syncmap.fragment import SyncMapFragment
from aeneas.syncmap.smfgxml import SyncMapFormatGenericXML
from aeneas.textfile import TextFragment
import aeneas.globalfunctions as gf

import lxml.etree as ET

TTML_NS = "http://www.w3.org/ns/ttml"
XML_NS = "http://www.w3.org/XML/1998/namespace"


with_ttml_ns = functools.partial(gf.with_ns, ns=TTML_NS)
with_xml_ns = functools.partial(gf.with_ns, ns=XML_NS)


class SyncMapFormatTTML(SyncMapFormatGenericXML):
    """
    Handler for TTML I/O format.
    """

    TTML = "ttml"

    DFXP = "dfxp"

    DEFAULT = TTML

    def parse(self, buf):
        root = ET.parse(buf).getroot()
        language = root.get(with_xml_ns("lang"))
        for elem in root.iter(with_ttml_ns("p")):
            yield SyncMapFragment.from_begin_end(
                begin=gf.time_from_ttml(elem.get("begin")),
                end=gf.time_from_ttml(elem.get("end")),
                text_fragment=TextFragment(
                    identifier=elem.get(with_xml_ns("id")),
                    language=language,
                    lines=self._get_lines_from_node_text(elem),
                ),
            )

    def format(self, syncmap):
        # get language
        language = None
        if self.parameters is not None and "language" in self.parameters:
            language = self.parameters["language"]
        elif len(syncmap.fragments) > 0:
            language = syncmap.fragments[0].text_fragment.language
        if language is None:
            language = ""

        # build tree
        tt_elem = ET.Element(with_ttml_ns("tt"), nsmap={None: TTML_NS})
        tt_elem.attrib[with_xml_ns("lang")] = language
        # TODO add metadata from parameters here?
        # COMMENTED head_elem = ET.SubElement(tt_elem, with_ttml_ns("head"))
        body_elem = ET.SubElement(tt_elem, with_ttml_ns("body"))
        div_elem = ET.SubElement(body_elem, with_ttml_ns("div"))

        if syncmap.is_single_level:
            # single level
            for fragment in syncmap.fragments:
                text = fragment.text_fragment
                p_string = '<p xml:id="{}" begin="{}" end="{}">{}</p>'.format(
                    text.identifier,
                    gf.time_to_ttml(fragment.begin),
                    gf.time_to_ttml(fragment.end),
                    "<br/>".join(text.lines),
                )
                p_elem = ET.fromstring(p_string)
                div_elem.append(p_elem)
        else:
            # TODO support generic multiple levels
            # multiple levels
            for par_child in syncmap.fragments_tree.children_not_empty:
                text = par_child.value.text_fragment
                p_elem = ET.SubElement(div_elem, with_ttml_ns("p"))
                p_elem.attrib["id"] = text.identifier
                for sen_child in par_child.children_not_empty:
                    text = sen_child.value.text_fragment
                    sen_span_elem = ET.SubElement(p_elem, with_ttml_ns("span"))
                    sen_span_elem.attrib["id"] = text.identifier
                    for wor_child in sen_child.children_not_empty:
                        fragment = wor_child.value
                        wor_span_elem = ET.SubElement(
                            sen_span_elem, with_ttml_ns("span")
                        )
                        wor_span_elem.attrib["id"] = fragment.text_fragment.identifier
                        wor_span_elem.attrib["begin"] = gf.time_to_ttml(fragment.begin)
                        wor_span_elem.attrib["end"] = gf.time_to_ttml(fragment.end)
                        wor_span_elem.text = "<br/>".join(fragment.text_fragment.lines)
        # write tree
        return self._tree_to_string(tt_elem)
