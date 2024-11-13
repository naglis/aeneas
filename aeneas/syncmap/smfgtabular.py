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

import typing

from aeneas.syncmap.smfbase import SyncMapFormatBase
import aeneas.globalfunctions as gf


class SyncMapFormatGenericTabular(SyncMapFormatBase):
    """
    Base class for tabular-like I/O format handlers.
    """

    TAG = "SyncMapFormatGenericTabular"

    DEFAULT = "tabular"
    """
    The code for the default variant
    associated with this format.
    """

    HUMAN = "tabularh"
    """
    The code for the human-readable variant
    associated with this format.
    """

    MACHINE = "tabularm"
    """
    The code for the machine-readable variant
    associated with this format.
    """

    MACHINE_ALIASES = [DEFAULT, MACHINE]
    """
    Aliases for the machine-readable variant.
    """

    FIELD_DELIMITER = ","
    """
    The character delimiting fields.
    """

    FIELDS = {"identifier": 0, "begin": 1, "end": 2, "text": 3}
    """
    Map that associated each field to its index.
    The map must contain the ``begin`` and ``end`` keys,
    while ``identifier`` and ``text`` are optional.
    """

    TEXT_DELIMITER: typing.ClassVar[str | None] = '"'
    """
    If ``None``, the text will not be delimited by a special character.
    Otherwise, use the specified character.
    """

    def __init__(self, variant=DEFAULT, parameters=None, rconf=None, logger=None):
        super().__init__(
            variant=variant, parameters=parameters, rconf=rconf, logger=logger
        )
        # store parse/format time functions
        if self.variant in self.MACHINE_ALIASES:
            self.parse_time_function = gf.time_from_ssmmm
            self.format_time_function = gf.time_to_ssmmm
        else:
            self.parse_time_function = gf.time_from_hhmmssmmm
            self.format_time_function = gf.time_to_hhmmssmmm
        # create write template string
        placeholders = [None for i in range(len(self.FIELDS))]
        for k in self.FIELDS:
            placeholders[self.FIELDS[k]] = k
        self.write_template = self.FIELD_DELIMITER.join(
            ["{%s}" % p for p in placeholders]
        )

    def parse(self, input_text, syncmap):
        lines = [line.strip() for line in input_text.splitlines()]
        lines = [line for line in lines if len(line) > 0]
        for index, line in enumerate(lines, 1):
            split = line.strip().split(self.FIELD_DELIMITER)

            # set identifier
            if "identifier" in self.FIELDS:
                identifier = split[self.FIELDS["identifier"]]
            else:
                identifier = "f%06d" % index

            # set begin and end
            begin = self.parse_time_function(split[self.FIELDS["begin"]])
            end = self.parse_time_function(split[self.FIELDS["end"]])

            # set text
            if "text" in self.FIELDS:
                text = self.FIELD_DELIMITER.join(split[self.FIELDS["text"] :])
                if (
                    (self.TEXT_DELIMITER is not None)
                    and (len(text) > 1)
                    and (text[0] == self.TEXT_DELIMITER)
                    and (text[-1] == self.TEXT_DELIMITER)
                ):
                    text = text[1:-1]
            else:
                text = ""

            self._add_fragment(
                syncmap=syncmap,
                identifier=identifier,
                lines=[text],
                begin=begin,
                end=end,
            )

    def format(self, syncmap):
        msg = []
        for fragment in syncmap.fragments:
            # get identifier
            identifier = fragment.text_fragment.identifier
            # get begin and end
            begin = self.format_time_function(fragment.begin)
            end = self.format_time_function(fragment.end)
            # get text
            text = fragment.text_fragment.text
            if self.TEXT_DELIMITER is not None:
                text = f"{self.TEXT_DELIMITER}{text}{self.TEXT_DELIMITER}"
            # format string
            msg.append(
                self.write_template.format(
                    identifier=identifier, begin=begin, end=end, text=text
                )
            )
        return "\n".join(msg)
