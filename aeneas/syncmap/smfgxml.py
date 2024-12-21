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

from itertools import chain

import lxml.etree as ET

from aeneas.syncmap.smfbase import SyncMapFormatBase
import aeneas.globalfunctions as gf


class SyncMapFormatGenericXML(SyncMapFormatBase):
    """
    Base class for XML-like I/O format handlers.
    """

    TAG = "SyncMapFormatGenericTabular"

    DEFAULT = "genericxml"
    """
    The code for the default variant
    associated with this format.
    """

    @classmethod
    def _get_lines_from_node_text(cls, node):
        """
        Given an ``lxml`` node, get lines from ``node.text``,
        where the line separator is ``<br xmlns=... />``.
        """
        # TODO more robust parsing

        parts = (
            [node.text]
            + list(
                chain(
                    *(
                        [ET.tostring(c, with_tail=False), c.tail]
                        for c in node.getchildren()
                    )
                )
            )
            + [node.tail]
        )
        parts = [gf.safe_unicode(p) for p in parts]
        parts = [p.strip() for p in parts if not p.startswith("<br ")]
        parts = [p for p in parts if len(p) > 0]
        uparts = []
        for part in parts:
            uparts.append(gf.safe_unicode(part))
        return uparts

    @classmethod
    def _tree_to_string(
        cls, root_element, *, xml_declaration: bool = True, pretty_print: bool = True
    ) -> str:
        """
        Return an ``lxml`` tree serialized as a string.
        """
        return ET.tostring(
            root_element,
            encoding="UTF-8",
            method="xml",
            xml_declaration=xml_declaration,
            pretty_print=pretty_print,
        ).decode("utf-8")
