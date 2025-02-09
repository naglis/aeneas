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


from aeneas.syncmap.fragment import SyncMapFragment
from aeneas.syncmap.smfgxml import SyncMapFormatGenericXML
from aeneas.textfile import TextFragment
import aeneas.globalfunctions as gf

import lxml.etree as ET


class SyncMapFormatXML(SyncMapFormatGenericXML):
    """
    Handler for XML I/O format.
    """

    DEFAULT = "xml"

    def parse(self, buf):
        for frag in ET.parse(buf).getroot():
            yield SyncMapFragment.from_begin_end(
                begin=gf.time_from_ssmmm(frag.get("begin")),
                end=gf.time_from_ssmmm(frag.get("end")),
                text_fragment=TextFragment(
                    identifier=frag.get("id"),
                    lines=[c.text for c in frag if c.tag == "line"],
                ),
            )

    def format(self, syncmap):
        def visit_children(node, parent_elem):
            """Recursively visit the fragments_tree"""
            for child in node.children_not_empty:
                fragment = child.value
                fragment_elem = ET.SubElement(parent_elem, "fragment")
                fragment_elem.attrib["id"] = fragment.text_fragment.identifier
                fragment_elem.attrib["begin"] = gf.time_to_ssmmm(fragment.begin)
                fragment_elem.attrib["end"] = gf.time_to_ssmmm(fragment.end)
                for line in fragment.text_fragment.lines:
                    line_elem = ET.SubElement(fragment_elem, "line")
                    line_elem.text = line
                children_elem = ET.SubElement(fragment_elem, "children")
                visit_children(child, children_elem)

        map_elem = ET.Element("map")
        visit_children(syncmap.fragments_tree, map_elem)
        return self._tree_to_string(map_elem)
