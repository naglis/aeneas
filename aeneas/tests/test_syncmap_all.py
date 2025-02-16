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
import itertools
import typing

from aeneas.syncmap import SyncMapFormat

from aeneas.tests.test_syncmap import BaseSyncMapCase


class TestSyncMapAllFormats(BaseSyncMapCase):
    def iter_cases(self) -> typing.Iterator[tuple[str, bool, bool]]:
        for fmt in SyncMapFormat.ALLOWED_VALUES:
            for multiline, utf8 in itertools.product([True, False], repeat=2):
                yield fmt, multiline, utf8

    def test_read(self):
        for fmt, multiline, utf8 in self.iter_cases():
            with self.subTest(fmt=fmt, multiline=multiline, utf8=utf8):
                syn = self.load(fmt, multiline=multiline, utf8=utf8)
                self.assertEqual(len(syn), 15)
                try:
                    str(syn)
                except Exception as e:
                    raise AssertionError("Failed to convert to string") from e

    def test_dump(self):
        for fmt, multiline, utf8 in self.iter_cases():
            with self.subTest(fmt=fmt, multiline=multiline, utf8=utf8):
                syn = self.load(SyncMapFormat.XML, multiline, utf8)
                try:
                    syn.dump(io.StringIO(), fmt, parameters=self.PARAMETERS)
                except Exception as e:
                    raise AssertionError("Failed to write syncmap") from e
