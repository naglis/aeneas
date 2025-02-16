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

import abc
import typing

from aeneas.syncmap.fragment import SyncMapFragment


# FIXME: Remove this hack.
if typing.TYPE_CHECKING:
    from aeneas.syncmap import SyncMap


class SyncMapFormatBase(abc.ABC):
    """
    Base class for I/O handlers.
    """

    def __init__(
        self,
        variant: str | None = None,
        parameters: dict | None = None,
    ):
        """
        TBW

        :param variant: the code of the format variant to read or write
        :type variant: string
        :param parameters: additional parameters to read or write
        :type parameters: ``None`` or ``dict``
        """
        super().__init__()
        self.variant = variant
        self.parameters = parameters or {}

    @abc.abstractmethod
    def parse(self, buf: typing.IO[bytes]) -> typing.Iterator[SyncMapFragment]:
        """
        Yield fragments parsed from ``buf``.
        """

    @abc.abstractmethod
    def format(self, syncmap: "SyncMap") -> str:
        """
        Format the given ``syncmap`` as a string.
        """
