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


from aeneas.syncmap.smfgsubtitles import SyncMapFormatGenericSubtitles
import aeneas.globalfunctions as gf


class SyncMapFormatVTT(SyncMapFormatGenericSubtitles):
    """
    Handler for WebVTT (VTT) I/O format.
    """

    TAG = "SyncMapFormatVTT"

    DEFAULT = "vtt"

    def __init__(self, variant=DEFAULT, parameters=None, rconf=None, logger=None):
        super().__init__(variant=variant, parameters=parameters, rconf=rconf, logger=logger)
        self.header_string = "WEBVTT"
        self.header_might_not_have_trailing_blank_line = False
        self.footer_string = None
        self.cue_has_identifier = False
        self.cue_has_optional_identifier = True
        self.time_values_separator = " --> "
        self.line_break_symbol = "\n"
        self.parse_time_function = gf.time_from_hhmmssmmm
        self.format_time_function = gf.time_to_hhmmssmmm

    def ignore_block(self, block_lines):
        return (
            (len(block_lines) > 0) and
            (
                (block_lines[0].startswith("NOTE")) or
                (block_lines[0].startswith("REGION")) or
                (block_lines[0].startswith("STYLE"))
            )
        )
